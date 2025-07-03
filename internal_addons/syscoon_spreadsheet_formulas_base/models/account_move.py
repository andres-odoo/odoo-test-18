# © 2024 syscoon Estonia OÜ (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    country_id = fields.Many2one(
        "res.country",
        related="partner_id.country_id",
        string="Country",
        store=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        related="move_id.invoice_user_id",
        string="Sales Person",
        store=True,
        readonly=True,
    )
