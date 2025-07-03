# © 2025 syscoon Estonia OÜ (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def get_company_id_by_name(self, company_name):
        if not company_name:
            return None
        return self.search([("name", "=", company_name)], limit=1).id

    @api.model
    def get_default_company_id(self):
        return self.env.company.id
