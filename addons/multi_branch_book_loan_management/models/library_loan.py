from odoo import fields, models, api
from odoo.exceptions import UserError

class LibraryLoan(models.Model):
    _name = "library.loan"
    _description = "Library Loan"

    book_id = fields.Many2one("library.book", string="Book", required=True)
    borrower_id = fields.Many2one("res.partner", string="Borrower", required=True)
    loan_date = fields.Datetime(string="Loan Date", default=fields.Date.context_today)
    return_date = fields.Datetime(string="Return Date")
    state = fields.Selection([
        ("draft", "Draft"),
        ("borrowed", "Borrowed"),
        ("returned", "Returned"),
    ], string="Status", default="draft", required=True, tracking=True)

    branch_id = fields.Many2one('res.company', string='Branch', compute='_compute_branch_id', store=True)

    @api.depends('book_id')
    def _compute_branch_id(self):
        for record in self:
            if record.book_id:
                record.branch_id = record.book_id.branch_id
                    
    @api.model
    def create(self, vals):
        # Add any necessary logic before creating a loan record
        res = super(LibraryLoan, self).create(vals)
        return res

    def action_borrow(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Only draft loans can be borrowed.")
            record.state = 'borrowed'

    def action_return(self):
        for record in self:
            if record.state != 'borrowed':
                raise UserError("Only borrowed books can be returned.")
            record.state = 'returned'
            record.return_date = fields.Date.today()
            
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Check if the user is not a system admin
        if not self.env.user.has_group('base.group_system'):
            # Get allowed company IDs from the context
            allowed_company_ids = self.env.context.get('allowed_company_ids')
            if allowed_company_ids:
                # Filter records based on allowed companies (branches)
                args.append(('branch_id', 'in', allowed_company_ids))
            else:
                # Default to the current session company if no allowed companies found
                current_company = self.env.company
                args.append(('branch_id', '=', current_company.id))
        
        # Call the parent class's search method
        return super(LibraryLoan, self).search(args, offset, limit, order, count=count)
    
    def action_library_loan_search_wizard(self):
        return {
            'name': 'Search Library Loans',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan.search.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

class LibraryLoanSearchWizard(models.TransientModel):
    _name = "library.loan.search.wizard"
    _description = "Library Loan Search Wizard"

    branch_ids = fields.Many2many('res.company', string='Branch')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def search_loans(self):
        # Prepare domain based on wizard inputs
        domain = []
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
        if self.start_date:
            domain.append(('loan_date', '>=', self.start_date))
        if self.end_date:
            domain.append(('loan_date', '<=', self.end_date))
            
        tree_view_id = self.env.ref('multi_branch_book_loan_management.view_library_loan_tree').id
        
        # Open the tree view with the filtered records
        return {
            'name': 'Filtered Library Loans',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'tree',
            'view_id': tree_view_id,
            'domain': domain,
            'context': self.env.context,
        }
        