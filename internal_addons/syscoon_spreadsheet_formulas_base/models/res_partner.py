# © 2025 syscoon Estonia OÜ (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_partner_id_by_name(self, partner_name):
        if not partner_name:
            return None
        return self.search([("name", "=", partner_name)], limit=1).id
