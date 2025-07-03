# © 2025 syscoon Estonia OÜ (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

import re
from datetime import date

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.account"

    # --- SPREADSHEET METHODS --- #

    @api.model
    def get_aml_data(self, args_list):
        results = []
        for args in args_list:
            start_date, end_date = self._get_custom_date_period_boundaries(
                args["start_date"], args["end_date"]
            )
            domain = [("date", ">=", start_date), ("date", "<=", end_date)]
            company_id = (
                args.get("company_id")
                if args.get("company_id") is not None
                else self.env.company.id
            )
            domain.append(("company_id", "=", company_id))

            if "codes" in args:
                domain = self._build_aml_domain(args, domain)

            account_move_lines = self.env["account.move.line"].sudo().search(domain)
            if not account_move_lines:
                results.append({"balance": 0.0, "quantity": 0.0})
                continue

            balance = sum(account_move_lines.mapped("balance"))
            quantity = sum(account_move_lines.mapped("quantity"))

            results.append({"balance": balance, "quantity": quantity})

        return results

    def _build_aml_domain(self, formula_params, domain):
        if formula_params.get("codes"):
            domain.append(("account_id.code", "in", formula_params["codes"]))

        if formula_params.get("tags"):
            tag_names = [name.strip() for name in formula_params["tags"]]
            domain.append(("account_id.tag_ids.name", "in", tag_names))

        if formula_params.get("partner_id"):
            domain.append(("partner_id", "=", formula_params["partner_id"]))

        if formula_params.get("product"):
            self._product_domain_builder(domain, formula_params["product"])

        if formula_params.get("country"):
            domain.append(("country_id.name", "=", formula_params["country"]))

        if formula_params.get("sales_person"):
            domain.append(("user_id.name", "=", formula_params["sales_person"]))

        include_unposted = formula_params.get("include_unposted")
        states = ["draft", "posted"] if include_unposted else ["posted"]
        domain.append(("parent_state", "in", states))

        return domain

    @api.model
    def _get_custom_date_period_boundaries(self, start_date, end_date):
        start_date = date(start_date["year"], start_date["month"], start_date["day"])
        end_date = date(end_date["year"], end_date["month"], end_date["day"])
        return start_date, end_date

    def _product_domain_builder(self, domain, product):
        product_count = self.env["product.product"].search_count([("name", "=", product)])
        if product_count == 0:
            (default_code, product_name, product_template_variant_names) = (
                self._process_product_name(product).values()
            )
            if default_code:
                domain.append(("product_id.default_code", "=", default_code))
            elif product_template_variant_names:
                variants = True
                for name in product_template_variant_names:
                    if (
                        not self.env["product.template.attribute.value"]
                        .sudo()
                        .search_count([("name", "=", name)])
                    ):
                        variants = False
                        break
                    domain.append(
                        ("product_id.product_template_variant_value_ids.name", "=", name)
                    )
                if variants:
                    domain.append(("product_id.name", "=", product_name))
            else:
                domain.append(("product_id.name", "=", product))
        else:
            domain.append(("product_id.name", "=", product))

    def _process_product_name(self, input_string):
        result = {"default_code": "", "name": "", "product_template_variant_names": []}

        default_code_match = re.match(r"^\[([^\]]+)\]", input_string)
        if default_code_match:
            result["default_code"] = default_code_match.group(1)
            input_string = input_string[len(default_code_match.group(0)) :].strip()

        last_parentheses_match = re.search(
            r"\((?:[^()]*(?:\([^()]*\)[^()]*)*)\)$", input_string
        )
        if last_parentheses_match and any(
            char.isdigit() for char in last_parentheses_match.group(0)
        ):
            variant_content = last_parentheses_match.group(0)[1:-1]
            variant_values = variant_content.split(", ")
            result["product_template_variant_names"] = variant_values
            input_string = input_string[: last_parentheses_match.start()].strip()

        result["name"] = input_string.strip()

        return result

    @api.model
    def get_aml_acc_type_data(self, args_list):
        results = []
        for args in args_list:
            start_date, end_date = self._get_custom_date_period_boundaries(
                args["start_date"], args["end_date"]
            )
            domain = [
                ("date", ">=", start_date),
                ("date", "<=", end_date),
            ]

            company_id = args.get("company_id") or self.env.company.id
            domain.append(("company_id", "=", company_id))

            account_type = args.get("account_type")
            if account_type:
                acc_type_key = next(
                    (
                        k
                        for k, v in self._fields["account_type"].selection
                        if v == account_type
                    ),
                    account_type,
                )
                domain.append(("account_type", "=", acc_type_key))

            include_unposted = args.get("include_unposted")
            states = ["draft", "posted"] if include_unposted else ["posted"]
            domain.append(("parent_state", "in", states))

            account_move_lines = self.env["account.move.line"].sudo().search(domain)
            balance = (
                sum(account_move_lines.mapped("balance")) if account_move_lines else 0.0
            )
            results.append({"balance": balance})

        return results
