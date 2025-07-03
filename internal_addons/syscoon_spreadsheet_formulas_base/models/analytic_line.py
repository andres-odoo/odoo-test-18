# © 2025 syscoon Estonia OÜ (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

import re
from datetime import date

from odoo import api, fields, models
from odoo.osv import expression


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    budget_type = fields.Char()
    budget_version = fields.Char()
    country_id = fields.Many2one(
        "res.country",
        related="partner_id.country_id",
        string="Country",
        store=True,
        readonly=True,
    )
    sales_person = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True
    )

    def _domain_manager(  # noqa
        self,
        mandatory_domain,
        account_code,
        budget_version,
        product,
        partner,
        sales_person,
        company_id,
        result_message,
    ):
        general_account_id = product_id = partner_id = sales_person_id = False
        domain = mandatory_domain

        if account_code:
            general_account_id = (
                self.env["account.account"]
                .sudo()
                .search(
                    expression.AND(
                        [
                            [("company_ids", "in", [company_id])],
                            [("code", "=", account_code)],
                        ]
                    ),
                    limit=1,
                )
                .id
            )
            if not general_account_id:
                result_message = '⚠️ Check "Account Code"'
            else:
                domain = expression.AND(
                    [domain, [("general_account_id", "=", general_account_id)]]
                )

        if budget_version:
            domain = expression.AND([domain, [("budget_version", "=", budget_version)]])

        if product:
            product_id = self._product_domain_builder(domain, product)
            if not product_id:
                result_message = '⚠️ Check "Product"'

        if partner:
            partner_id = (
                self.env["res.partner"].search([("name", "=", partner)], limit=1).id
            )
            if not partner_id:
                result_message = '⚠️ Check "Partner"'
            else:
                domain = expression.AND([domain, [("partner_id", "=", partner_id)]])

        if sales_person:
            sales_person_id = (
                self.env["res.users"].search([("name", "=", sales_person)], limit=1).id
            )
            if not sales_person_id:
                result_message = '⚠️ Check "Sales Person"'
            else:
                domain = expression.AND(
                    [domain, [("sales_person", "=", sales_person_id)]]
                )

        if company_id:
            domain = expression.AND([domain, [("company_id", "=", company_id)]])

        return {
            "general_account_id": general_account_id,
            "product_id": product_id,
            "partner_id": partner_id,
            "sales_person_id": sales_person_id,
            "domain": domain,
            "result_message": result_message,
        }

    def _data_manager(self, amount, quantity, params_obj, result_message):
        (
            date_obj,
            account_code,
            analytic_acc,
            budget_type,
            budget_version,
            product,
            partner,
            sales_person,
            company_id,
        ) = params_obj.values()

        if company_id:
            company = self.env["res.company"].search([("id", "=", company_id)], limit=1)
            if not company:
                return {
                    "company_id": None,
                    "domain": [],
                    "analytic_item": {},
                    "result_message": '⚠️ "Company ID" not found',
                }
        else:
            company_id = self.env.company.id

        # Mandatory parameters
        parsed_date = date(**date_obj)

        analytic_account = (
            self.env["account.analytic.account"]
            .sudo()
            .search([("name", "=", analytic_acc)], limit=1)
        )
        column_name = "account_id"
        if not analytic_account:
            result_message = '⚠️ Check "Analytic Account"'
        else:
            analytic_plan = analytic_account.plan_id
            column_name = analytic_plan._strict_column_name()

        mandatory_domain = expression.AND(
            [
                [("date", "=", parsed_date)],
                [("budget_type", "=", budget_type)],
                [(column_name, "=", analytic_account.id)],
            ]
        )

        # Optional parameters
        domain_obj = self._domain_manager(
            mandatory_domain,
            account_code,
            budget_version,
            product,
            partner,
            sales_person,
            company_id,
            result_message,
        )

        (
            general_account_id,
            product_id,
            partner_id,
            sales_person_id,
            domain,
            result_message,
        ) = domain_obj.values()

        analytic_item = {
            "name": "Created from Spreadsheet Formula",
            "amount": amount or 0,
            "unit_amount": quantity,
            "date": parsed_date,
            "budget_type": budget_type,
            "budget_version": budget_version,
            "general_account_id": general_account_id,
            column_name: analytic_account.id,
            "product_id": product_id,
            "partner_id": partner_id,
            "sales_person": sales_person_id,
        }

        return {
            "company_id": company_id,
            "domain": domain,
            "analytic_item": analytic_item,
            "result_message": result_message,
        }

    @api.model
    def set_analytic_item(self, args_list):
        results = []
        for args in args_list:
            trigger = args.get("trigger")
            amount = args.get("amount", 0)
            quantity = args.get("quantity")
            params_obj = args.get("params_obj", {})

            result_message = "🔴 INACTIVE"

            if trigger == "Run":
                result_message = "🟢"
                data_obj = self._data_manager(
                    amount, quantity, params_obj, result_message
                )
                company_id, domain, new_analytic_item, result_message = data_obj.values()

                if result_message != "🟢":
                    results.append(result_message)
                    continue

                acc_analytic_line = self.sudo().search(domain, limit=1)

                if acc_analytic_line:
                    fields_to_update = {
                        "amount": new_analytic_item.get("amount"),
                        "unit_amount": new_analytic_item.get("unit_amount"),
                    }
                    changes = {}
                    for field, new_value in fields_to_update.items():
                        if getattr(acc_analytic_line, field) != new_value:
                            changes[field] = new_value

                    if changes:
                        acc_analytic_line.write(changes)
                        field_names = {
                            "amount": "Amount",
                            "unit_amount": "Quantity",
                        }
                        updated_fields = [
                            f'"{field_names[field]}" set to {value}'
                            for field, value in changes.items()
                        ]
                        results.append(f"{' and '.join(updated_fields)}")
                    else:
                        results.append("🟢 No Changes")
                else:
                    new_analytic_item = self.with_company(company_id).create(
                        new_analytic_item
                    )
                    results.append(f"🟢 Created ID-{new_analytic_item.id}")
            else:
                results.append(result_message)

        return results

    @api.model
    def get_aal_data(self, args_list):  # noqa
        results = []
        for args in args_list:
            start_date, end_date = self._get_custom_date_period_boundaries(
                args["start_date"], args["end_date"]
            )
            domain = [("date", ">=", start_date), ("date", "<=", end_date)]

            if args.get("budget_type") is not None:
                domain.append(("budget_type", "=", args["budget_type"]))
            if args.get("budget_version") is not None:
                domain.append(("budget_version", "=", args["budget_version"]))
            if args.get("account"):
                domain.append(("general_account_id.code", "=", args["account"]))
            if args.get("account_tags"):
                account_tag_ids = (
                    self.env["account.account.tag"]
                    .search([("name", "in", args["account_tags"])])
                    .ids
                )
                domain.append(("general_account_id.tag_ids", "in", account_tag_ids))
            if args.get("analytic_account"):
                aa_name = args.get("analytic_account")
                analytic_account = (
                    self.env["account.analytic.account"]
                    .sudo()
                    .search([("name", "=", aa_name)], limit=1)
                )
                column_name = "account_id"
                if analytic_account:
                    plan_id = analytic_account.plan_id.id
                    analytic_plan = self.env["account.analytic.plan"].browse(plan_id)
                    column_name = analytic_plan._strict_column_name()
                domain.append((f"{column_name}.name", "=", aa_name))
            if args.get("product"):
                domain.append(("product_id.name", "=", args["product"]))
            if args.get("partner"):
                domain.append(("partner_id.name", "=", args["partner"]))
            if args.get("sales_person"):
                domain.append(("sales_person.name", "=", args["sales_person"]))
            if args.get("country"):
                domain.append(("country_id.name", "=", args["country"]))
            if args.get("company_id"):
                domain.append(("company_id", "=", args["company_id"]))

            analytic_lines = self.search(domain)
            balance = sum(analytic_lines.mapped("amount"))
            quantity = sum(analytic_lines.mapped("unit_amount"))

            results.append({"balance": balance, "quantity": quantity})

        return results

    @api.model
    def _get_custom_date_period_boundaries(self, start_date, end_date):
        start_date = date(start_date["year"], start_date["month"], start_date["day"])
        end_date = date(end_date["year"], end_date["month"], end_date["day"])
        return start_date, end_date

    def _product_domain_builder(self, domain, product):
        product_id = None
        product_count = self.env["product.product"].search_count([("name", "=", product)])
        if product_count == 0:
            (
                default_code,
                product_name,
                product_template_variant_names,
            ) = self._process_product_name(product).values()

            if default_code:
                domain.append(("product_id.default_code", "=", default_code))
                product_id = (
                    self.env["product.product"]
                    .search([("default_code", "=", default_code)])
                    .id
                )
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
                    product_ids = (
                        self.env["product.product"]
                        .search([("name", "=", product_name)])
                        .ids
                    )
                    domain.append(("product_id", "in", product_ids))
                    # For creating a record, we have to pick only one product:
                    product_id = product_ids and product_ids[0] or None
                else:
                    domain.append(("product_id.name", "=", product))
                    product_id = (
                        self.env["product.product"].search([("name", "=", product)]).id
                    )
        else:
            product_ids = self.env["product.product"].search([("name", "=", product)]).ids
            domain.append(("product_id", "in", product_ids))
            # For creating a record, we have to pick only one product:
            product_id = product_ids and product_ids[0] or None

        return product_id

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
