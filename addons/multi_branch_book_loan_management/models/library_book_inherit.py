from odoo import models, fields, api

class LibraryBookInherit(models.Model):
    _inherit = 'library.book'

    total_copies = fields.Integer(string="Total Copies", default=1)
    available_copies = fields.Integer(string="Available Copies", compute="_compute_available_copies", store=True)
    loan_ids = fields.One2many('library.loan', 'book_id', string='Loans')
    total_borrows = fields.Integer(string="Total Borrowed", compute="_compute_total_borrows", store=True)

    @api.depends('loan_ids.state')
    def _compute_available_copies(self):
        for book in self:
            borrowed_copies = len(book.loan_ids.filtered(lambda l: l.state == "borrowed"))
            book.available_copies = book.total_copies - borrowed_copies
            
    @api.depends('loan_ids.state')
    def _compute_total_borrows(self):
        for book in self:
            book.total_borrows = len(book.loan_ids.filtered(lambda l: l.state in ["borrowed", "returned"]))

