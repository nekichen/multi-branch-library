from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        # Call super to create the user
        user = super(ResUsers, self).create(vals)
        
        # Automatically assign Library User group
        library_user_group = self.env.ref('library_management.group_library_user')
        user.groups_id = [(4, library_user_group.id)]
        
        return user
