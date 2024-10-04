from odoo import models, fields, api
from odoo.exceptions import ValidationError
import io
import xlsxwriter
import base64

class LibraryReportWizard(models.TransientModel):
    _name = 'library.report.wizard'
    _description = 'Library Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    book_ids = fields.Many2many("library.book", string="Books")
    branch_ids = fields.Many2many("res.company", string="Branches")

    def action_generate_report(self):
        # Validate that start_date is earlier than end_date
        if self.start_date > self.end_date:
            raise ValidationError("End date must be greater than start date.")

        # Construct the base domain for filtering library loan records
        domain = [
            ('loan_date', '>=', self.start_date),
            ('loan_date', '<=', self.end_date)
        ]

        # Filter by selected branches
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))

        # Filter by selected books
        if self.book_ids:
            domain.append(('book_id', 'in', self.book_ids.ids))

        loan_records = self.env['library.loan'].search(domain)

        # Create an Excel report
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Library Loans Report")

        # Write headers
        headers = ['Loan Date', 'Book Title', 'Branch', 'Borrower']
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        for col_idx, header in enumerate(headers):
            worksheet.write(0, col_idx, header, header_format)

        # Write loan records
        for row_idx, record in enumerate(loan_records, start=1):
            worksheet.write(row_idx, 0, record.loan_date.strftime("%Y-%m-%d"))
            worksheet.write(row_idx, 1, record.book_id.name)
            worksheet.write(row_idx, 2, record.branch_id.name)
            borrower_name = record.borrower_id.name if record.borrower_id else 'Unknown'
            worksheet.write(row_idx, 3, borrower_name)

        workbook.close()
        output.seek(0)

        attachment_ids = []  # Initialize attachment_ids for storing attachments

        if self.book_ids:
            branch_ids = {book.branch_id.id for book in self.book_ids if book.branch_id}  # Get branches from books
        else:
            branch_ids = self.branch_ids.ids  # Use selected branches if no books are selected

        if not branch_ids:
            raise ValidationError("No valid branches associated with the selected books or branches.")

        for branch_id in branch_ids:
            branch = self.env['res.company'].browse(branch_id)

            report_name = f"Report from {self.start_date} to {self.end_date}"

            if self.book_ids:
                report_name += f" ({', '.join(book.name for book in self.book_ids)})"
            elif self.branch_ids:
                report_name += f" ({', '.join(branch.name for branch in self.branch_ids)})"
            else:
                report_name += " (General)"

            total_books = 0
            total_loans = 0

            if self.book_ids:
                total_books = self.env['library.book'].search_count([('branch_id', '=', branch.id), ('id', 'in', self.book_ids.ids)])
                
                # For each selected book, count the loans associated with the current branch
                for book in self.book_ids:
                    if book.branch_id == branch:
                        loans_count = len(loan_records.filtered(lambda r: r.branch_id.id == branch.id and r.book_id.id == book.id))
                        total_loans += loans_count
            elif self.branch_ids:
                total_books = self.env['library.book'].search_count([('branch_id', '=', branch.id)])
                total_loans = len(loan_records.filtered(lambda r: r.branch_id.id == branch.id))

            report_vals = {
                'name': report_name,
                'total_books': total_books,
                'total_loans': total_loans,
                'branch_id': branch.id,
            }

            report = self.env['library.report'].create(report_vals)

            # Create the attachment for the report
            attachment = self.env['ir.attachment'].create({
                'name': f'Loan_Report_{branch.name}_{fields.Date.today()}.xlsx',
                'type': 'binary',
                'datas': base64.b64encode(output.getvalue()),
                'store_fname': f'Loan_Report_{branch.name}_{fields.Date.today()}.xlsx',
                'res_model': 'library.report',
                'res_id': report.id,
            })

            attachment_ids.append(attachment.id)  # Append the attachment ID

        # Return the download link for the first attachment created
        if attachment_ids:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment_ids[0]}?download=true',
                'target': 'self',
            }
        else:
            raise ValidationError("Failed to create the attachment.")

class LibraryReport(models.Model):
    _name = 'library.report'
    _description = 'Library Report'

    name = fields.Char(string='Report Name')
    total_books = fields.Integer(string='Total Books')  # Total books is set during report creation
    total_loans = fields.Integer(string='Total Loans')  # Total loans is set during report creation
    branch_id = fields.Many2one('res.company', string='Branch')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Apply company or branch filtering
        if not self.env.user.has_group('base.group_system'):
            allowed_company_ids = self.env.context.get('allowed_company_ids')
            if allowed_company_ids:
                args.append(('branch_id', 'in', allowed_company_ids))
            else:
                current_company = self.env.company
                args.append(('branch_id', '=', current_company.id))
        
        return super(LibraryReport, self).search(args, offset, limit, order, count=count)
