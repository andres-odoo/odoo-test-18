# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WeatherConfig(models.Model):
    _name = "weather.config"
    _description = "Weather Configuration"

    name = fields.Char(required=True)
    api_key = fields.Char(password=True, required=True)
    url = fields.Char(string="URL")
    active = fields.Boolean(default=False)

    def get_api_key(self):
        weather_config = self.sudo().search([("active", "=", True)], limit=1)
        return weather_config.api_key, weather_config.url
