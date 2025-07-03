# © 2025 syscoon Estonia OÜ (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "Syscoon Spreadsheet Formulas Base",
    "version": "18.0.0.1.1",
    "category": "Spreadsheets",
    "summary": "Custom formulas with new filters",
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    "depends": ["analytic", "spreadsheet_account"],
    "data": [
        "views/account_move_line_views.xml",
        "views/account_analytic_line_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "assets": {
        "spreadsheet.o_spreadsheet": [
            (
                "after",
                "spreadsheet/static/src/**/*.js",
                "syscoon_spreadsheet_formulas_base/static/src/**/*.js",
            )
        ],
    },
}
