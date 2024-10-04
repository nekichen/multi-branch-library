from odoo import fields, models, api
from odoo.exceptions import UserError

class LibraryBookCategory(models.Model):
    _name = "library.book.category"
    _description = "Book Category"
    
    name = fields.Char(string="Category Name", required=True)
    description = fields.Text()
    
    _sql_constraints = [
        ("name_uniq", "unique(name)", "The category name must be unique"),
    ]
    
class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Book"
    
    # Fields
    name = fields.Char(string="Title", required=True)
    date_release = fields.Date()
    author_ids = fields.Many2many("res.partner", string="Authors")
    category_id = fields.Many2one("library.book.category", string="Category", ondelete="cascade")
    description = fields.Html()

    attachment = fields.Binary(string="Attachment")
    
    branch_id = fields.Many2one('res.company', string='Branch', required=True)

    # SQL Constraints
    _sql_constraints = [
        ("name_uniq", "unique(name)", "The book title must be unique"),
    ]
    
    # Methods
    @api.model
    def create(self, vals):
        if 'branch_id' not in vals and not self.env.user.has_group('base.group_system'):
            vals['branch_id'] = self.env.user.company_id.id
        return super(LibraryBook, self).create(vals)

    def write(self, vals):
        if 'branch_id' in vals and not self.env.user.has_group('base.group_system'):
            vals.pop('branch_id')
        return super(LibraryBook, self).write(vals)

    @api.model
    def get_books_for_current_company(self):
        # This retrieves the company that is currently active in the UI.
        current_company_id = self.env.context.get('force_company', self.env.user.company_id.id)
        return self.search([('branch_id', '=', current_company_id)])
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Check if the user is not an admin (i.e., does not belong to the 'base.group_system')
        if not self.env.user.has_group('base.group_system'):
            # Get the allowed company IDs from the current context
            allowed_company_ids = self.env.context.get('allowed_company_ids')
            
            # If there are allowed company IDs, filter by these companies
            if allowed_company_ids:
                args.append(('branch_id', 'in', allowed_company_ids))
            else:
                # Fallback to the current active company if no companies are specified in the context
                current_company = self.env.company
                args.append(('branch_id', '=', current_company.id))
        
        # Perform the search with the updated args
        return super(LibraryBook, self).search(args, offset, limit, order, count=count)
