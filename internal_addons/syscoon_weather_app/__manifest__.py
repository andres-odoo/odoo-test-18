# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon_weather_app",
    "summary": """
        Syscoon's Weather App
    """,
    "description": """
        Syscoon's Weather App
    """,
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    "category": "Customizations",
    "version": "18.0.0.0.0",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/weather_config_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "syscoon_weather_app/static/src/**/*",
            # "syscoon_weather_app/static/src/js/weather_systray_menu.js",
            # "syscoon_weather_app/static/src/xml/weather_systray_menu.xml",
        ],
    },
    "installable": True,
}
