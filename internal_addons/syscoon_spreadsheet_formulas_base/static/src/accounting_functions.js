/** @odoo-module **/

import {_t} from "@web/core/l10n/translation"
import {EvaluationError} from "@odoo/o-spreadsheet"
import {registries, helpers} from "@odoo/o-spreadsheet"

const {arg, toBoolean, toString} = helpers
const {functionRegistry} = registries

const AML_BALANCE_ARGS = [
  arg("startDate (date)", _t(`The start date in dd/mm/yyyy format (string).`)),
  arg("endDate (date)", _t(`The end date in dd/mm/yyyy format (string).`)),
  arg("accountCodes (string, optional)", _t("The codes of the accounts to look for, separated by commas.")),
  arg("accountTags (string, optional)", _t("The tags of the accounts to look for, separated by commas.")),
  arg("partnerId (number, optional)", _t("The partner of the accounts to look for.")),
  arg("product (string, optional)", _t("The product to filter by.")),
  arg("country (string, optional)", _t("The country to filter by.")),
  arg("salesPerson (string, optional)", _t("The sales person to filter by.")),
  arg("companyId (number, optional)", _t("The company to target (Advanced).")),
  arg("includeUnposted (boolean, optional)", _t("Set it to TRUE to include unposted entries.")),
]

const ACC_TYPE_BALANCE_ARGS = [
  arg("startDate (date)", _t("The start date in dd/mm/yyyy format (string).")),
  arg("endDate (date)", _t("The end date in dd/mm/yyyy format (string).")),
  arg("accountType (string)", _t("The account type to filter by (e.g., 'asset', 'liability', etc.).")),
  arg("companyId (number, optional)", _t("The company to target (Advanced).")),
  arg("includeUnposted (boolean, optional)", _t("Set it to TRUE to include unposted entries.")),
]

const SET_ANALYTIC_ITEM_ARGS = [
  arg("trigger (string)", _t("Activates the function if set to 'Run'")),
  arg("amount (number)", _t("Value to be set in the field 'Amount'")),
  arg("quantity (number)", _t("Value to be set in the field 'Quantity'")),
  arg("date (date)", _t("Date in format dd/mm/yyyy")),
  arg("analyticAccount (string)", _t("Associated Analytic Account")),
  arg("budgetType (string)", _t("Budget Type")),
  arg("accountCode (string, optional)", _t("Associated Account")),
  arg("budgetVersion (string, optional)", _t("Budget Version")),
  arg("product (string, optional)", _t("Associated Product")),
  arg("partner (string, optional)", _t("Associated Partner")),
  arg("salesPerson (string, optional)", _t("Sales Person Assigned")),
  arg("companyId (number, optional)", _t("The ID of the company to target")),
]

const AAL_ARGS = [
  arg("startDate (date)", _t("The start date in dd/mm/yyyy format.")),
  arg("endDate (date)", _t("The end date in dd/mm/yyyy format.")),
  arg("budgetType (string, optional)", _t("The budget type to filter by.")),
  arg("budgetVersion (string, optional)", _t("The budget version to filter by.")),
  arg("account (string, optional)", _t("The account code to filter by.")),
  arg("accountTags (string, optional)", _t("The account tags to filter by, separated by commas.")),
  arg("analyticAccount (string, optional)", _t("The analytic account to filter by.")),
  arg("product (string, optional)", _t("The product to filter by.")),
  arg("partner (string, optional)", _t("The partner to filter by.")),
  arg("salesPerson (string, optional)", _t("The sales person to filter by.")),
  arg("country (string, optional)", _t("The country to filter by.")),
  arg("companyId (number, optional)", _t("The company to target (Advanced).")),
]

/**
 * @param {string | number} date
 * @returns {CustomDate}
 */
export function parseAccountingDateToObj(date) {
  let dateObj = {}
  if (typeof date === "number") {
    dateObj = {
      day: functionRegistry.get("MONTH").compute(date),
      month: functionRegistry.get("DAY").compute(date),
      year: functionRegistry.get("YEAR").compute(date),
    }
  } else if (typeof date === "string") {
    const dateParts = date.split(/\/|\-/)
    if (dateParts.length !== 3) {
      throw new EvaluationError(_t("Invalid date format. Use DD/MM/YYYY or DD-MM-YYYY"))
    }
    const day = parseInt(dateParts[0])
    const month = parseInt(dateParts[1])
    const year = parseInt(dateParts[2])
    if (isNaN(day) || isNaN(month) || isNaN(year)) {
      throw new EvaluationError(_t("Date parts must be numbers"))
    }
    if (day < 1 || day > 31) {
      throw new EvaluationError(_t("Day must be between 1 and 31"))
    }
    if (month < 1 || month > 12) {
      throw new EvaluationError(_t("Month must be between 1 and 12"))
    }
    if (year < 1900) {
      throw new EvaluationError(_t("Year must be 1900 or later"))
    }
    dateObj = {day, month, year}
  } else {
    throw new EvaluationError(_t("Date is required and must be a number or string"))
  }
  const testDate = new Date(dateObj.year, dateObj.month - 1, dateObj.day)
  if (testDate.getDate() !== dateObj.day) {
    throw new EvaluationError(_t("Invalid date for the given month"))
  }
  return dateObj
}

functionRegistry

  .add("SYSCOON.GET.COMPANY.ID", {
    description: _t("Get the company ID by its name"),
    args: [arg("company_name (string)", _t("Name of the company."))],
    returns: ["NUMBER"],
    compute: function (companyId) {
      const _companyId = companyId.value
      return this.getters.getCompanyIdByName(_companyId)
    },
  })

  .add("SYSCOON.GET.PARTNER.ID", {
    description: _t("Get the partner ID by its name"),
    args: [arg("partner_name (string)", _t("Name of the partner."))],
    returns: ["NUMBER"],
    compute: function (partnerId) {
      const _partnerId = partnerId.value
      return this.getters.getPartnerIdByName(_partnerId)
    },
  })

  .add("SYSCOON.AML.BALANCE", {
    description: _t(
      "Get the total balance for the specified period, account(s), tag(s), partner and company"
    ),
    args: AML_BALANCE_ARGS,
    returns: ["NUMBER"],
    compute: function (
      startDate,
      endDate,
      accountCodes = {value: null},
      accountTags = {value: null},
      partnerId = {value: null},
      product = {value: null},
      country = {value: null},
      salesPerson = {value: null},
      companyId = {value: null},
      includeUnposted = {value: false}
    ) {
      const _startDate = parseAccountingDateToObj(startDate.value)
      const _endDate = parseAccountingDateToObj(endDate.value)
      const _accountCodes = accountCodes.value && toString(accountCodes.value).split(",").sort()
      const _accountTags = accountTags.value && toString(accountTags.value).split(",").sort()
      const _partnerId = partnerId.value
      const _product = product.value
      const _country = country.value
      const _salesPerson = salesPerson.value
      const _companyId = companyId.value
      const _includeUnposted = toBoolean(includeUnposted.value)
      const value = this.getters.getAmlBalance(
        _startDate,
        _endDate,
        _accountCodes,
        _accountTags,
        _partnerId,
        _product,
        _country,
        _salesPerson,
        _companyId,
        _includeUnposted
      )
      return {value, format: this.getters.getCompanyCurrencyFormat(_companyId) || "#,##0.00"}
    },
  })

  .add("SYSCOON.AML.QUANTITY", {
    description: _t(
      "Get the total quantity for the specified period, account(s), tag(s), partner and company"
    ),
    args: AML_BALANCE_ARGS,
    returns: ["NUMBER"],
    compute: function (
      startDate,
      endDate,
      accountCodes = {value: null},
      accountTags = {value: null},
      partnerId = {value: null},
      product = {value: null},
      country = {value: null},
      salesPerson = {value: null},
      companyId = {value: null},
      includeUnposted = {value: false}
    ) {
      const _startDate = parseAccountingDateToObj(startDate.value)
      const _endDate = parseAccountingDateToObj(endDate.value)
      const _accountCodes = accountCodes.value && toString(accountCodes.value).split(",").sort()
      const _accountTags = accountTags.value && toString(accountTags.value).split(",").sort()
      const _partnerId = partnerId.value
      const _product = product.value
      const _country = country.value
      const _salesPerson = salesPerson.value
      const _companyId = companyId.value
      const _includeUnposted = toBoolean(includeUnposted.value)
      const value = this.getters.getAmlQuantity(
        _startDate,
        _endDate,
        _accountCodes,
        _accountTags,
        _partnerId,
        _product,
        _country,
        _salesPerson,
        _companyId,
        _includeUnposted
      )
      return {value, format: "#,##0.00"}
    },
  })

  .add("SYSCOON.AML.ACC.TYPE.BALANCE", {
    description: _t(
      "Get the total balance for the specified period and account type, with optional company and unposted entries filters."
    ),
    args: ACC_TYPE_BALANCE_ARGS,
    returns: ["NUMBER"],
    compute: function (
      startDate,
      endDate,
      accountType,
      companyId = {value: null},
      includeUnposted = {value: false}
    ) {
      const _startDate = parseAccountingDateToObj(startDate.value)
      const _endDate = parseAccountingDateToObj(endDate.value)
      const _accountType = accountType.value
      const _companyId = companyId.value
      const _includeUnposted = toBoolean(includeUnposted.value)
      const value = this.getters.getAmlBalanceByAccountType(
        _startDate,
        _endDate,
        _accountType,
        _companyId,
        _includeUnposted
      )
      return {value, format: this.getters.getCompanyCurrencyFormat(_companyId) || "#,##0.00"}
    },
  })

  .add("SYSCOON.AAL.BALANCE", {
    description: _t("Get the total balance for the specified period and filters from analytic account lines"),
    args: AAL_ARGS,
    returns: ["NUMBER"],
    compute: function (
      startDate,
      endDate,
      budgetType = {value: null},
      budgetVersion = {value: null},
      account = {value: null},
      accountTags = {value: null},
      analyticAccount = {value: null},
      product = {value: null},
      partner = {value: null},
      salesPerson = {value: null},
      country = {value: null},
      companyId = {value: null}
    ) {
      const _startDate = parseAccountingDateToObj(startDate.value)
      const _endDate = parseAccountingDateToObj(endDate.value)
      const _budgetType = budgetType.value
      const _budgetVersion = budgetVersion.value
      const _account = account.value
      const _accountTags = accountTags.value
        ? toString(accountTags.value)
            .split(",")
            .map((code) => code.trim())
            .sort()
        : []
      const _analyticAccount = analyticAccount.value
      const _product = product.value
      const _partner = partner.value
      const _salesPerson = salesPerson.value
      const _country = country.value
      const _companyId = companyId.value
      const value = this.getters.getAnalyticBalance(
        _startDate,
        _endDate,
        _budgetType,
        _budgetVersion,
        _account,
        _accountTags,
        _analyticAccount,
        _product,
        _partner,
        _salesPerson,
        _country,
        _companyId
      )
      return {value, format: this.getters.getCompanyCurrencyFormat(_companyId) || "#,##0.00"}
    },
  })

  .add("SYSCOON.AAL.QUANTITY", {
    description: _t(
      "Get the total quantity for the specified period and filters from analytic account lines"
    ),
    args: AAL_ARGS,
    returns: ["NUMBER"],
    compute: function (
      startDate,
      endDate,
      budgetType = {value: null},
      budgetVersion = {value: null},
      account = {value: null},
      accountTags = {value: null},
      analyticAccount = {value: null},
      product = {value: null},
      partner = {value: null},
      salesPerson = {value: null},
      country = {value: null},
      companyId = {value: null}
    ) {
      const _startDate = parseAccountingDateToObj(startDate.value)
      const _endDate = parseAccountingDateToObj(endDate.value)
      const _budgetType = budgetType.value
      const _budgetVersion = budgetVersion.value
      const _account = account.value
      const _accountTags = accountTags.value
        ? toString(accountTags.value)
            .split(",")
            .map((code) => code.trim())
            .sort()
        : []
      const _analyticAccount = analyticAccount.value
      const _product = product.value
      const _partner = partner.value
      const _salesPerson = salesPerson.value
      const _country = country.value
      const _companyId = companyId.value
      const value = this.getters.getAnalyticQuantity(
        _startDate,
        _endDate,
        _budgetType,
        _budgetVersion,
        _account,
        _accountTags,
        _analyticAccount,
        _product,
        _partner,
        _salesPerson,
        _country,
        _companyId
      )
      return {value, format: "#,##0.00"}
    },
  })

  .add("SYSCOON.SET.ANALYTIC.ITEM", {
    description: _t("Creates or Updates an specific analytic line according to the given parameters"),
    args: SET_ANALYTIC_ITEM_ARGS,
    returns: ["STRING"],
    compute: function (
      trigger,
      amount,
      quantity,
      date,
      analyticAccount,
      budgetType,
      accountCode = {value: null},
      budgetVersion = {value: null},
      product = {value: null},
      partner = {value: null},
      salesPerson = {value: null},
      companyId = {value: null}
    ) {
      const _trigger = trigger.value
      const _amount = amount.value
      const _quantity = quantity.value
      const _date = parseAccountingDateToObj(date.value)
      const _account_code = accountCode.value
      const _analyticAccount = analyticAccount.value
      const _budgetType = budgetType.value
      const _budgetVersion = budgetVersion.value
      const _product = product.value
      const _partner = partner.value
      const _salesPerson = salesPerson.value
      const _companyId = companyId.value
      const _paramsObj = {
        _date,
        _account_code,
        _analyticAccount,
        _budgetType,
        _budgetVersion,
        _product,
        _partner,
        _salesPerson,
        _companyId,
      }
      return this.getters.setAnalyticItem(_trigger, _amount, _quantity, _paramsObj)
    },
  })
