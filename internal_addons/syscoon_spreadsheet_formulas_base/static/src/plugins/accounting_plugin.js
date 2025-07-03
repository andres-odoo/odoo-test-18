/** @odoo-module */

import {OdooUIPlugin} from "@spreadsheet/plugins"
import {camelToSnakeObject} from "@spreadsheet/helpers/helpers"
import {_t} from "@web/core/l10n/translation"

export default class SyscoonAccountingPlugin extends OdooUIPlugin {
  static getters = /** @type {const} */ ([
    "getPartnerIdByName",
    "getCompanyIdByName",
    "getDefaultCompanyId",
    "getAmlBalance",
    "getAmlQuantity",
    "setAnalyticItem",
    "getAnalyticBalance",
    "getAnalyticQuantity",
    "getAmlBalanceByAccountType",
  ])
  constructor(config) {
    super(config)
    /** @type {import("@spreadsheet/data_sources/server_data").ServerData} */
    this._serverData = config.custom.odooDataProvider?.serverData
  }

  get serverData() {
    if (!this._serverData) {
      throw new Error(
        "'serverData' is not defined, please make sure a 'OdooDataProvider' instance is provided to the model."
      )
    }
    return this._serverData
  }

  // -------------------------------------------------------------------------
  // Getters
  // -------------------------------------------------------------------------

  /**
   * Gets the partner ID for a given partner name
   * @param {string} partnerName name of the partner
   * @returns {number | undefined}
   */
  getPartnerIdByName(partnerName) {
    return this.serverData.get("res.partner", "get_partner_id_by_name", [partnerName])
  }

  /**
   * Gets the company ID for a given company name
   * @param {string} companyId name of the company
   * @returns {number | undefined}
   */
  getCompanyIdByName(companyId) {
    return this.serverData.get("res.company", "get_company_id_by_name", [companyId])
  }

  /**
   * Gets the default company ID
   * @returns {number | undefined}
   */
  getDefaultCompanyId() {
    return this.serverData.get("res.company", "get_default_company_id")
  }

  /**
   * Gets the total credit for a given period and arguments
   * @param {CustomDate} startDate Start date of the period to look
   * @param {CustomDate} endDate End date of the period to look
   * @param {string[]} codes Accounts codes
   * @param {string[]} tags Accounts tags
   * @param {number} partnerId Specific partner to target
   * @param {string} product The product to filter by
   * @param {string} country The country to filter by
   * @param {string} salesPerson The sales person to filter by
   * @param {number | null} companyId Specific company to target
   * @param {boolean} includeUnposted Wether or not select unposted entries
   * @returns {number}
   */
  getAmlBalance(...args) {
    const data = this._fetchAmlData(...args)
    return data.balance
  }

  /**
   * Gets the total debit for a given period and arguments
   * @param {CustomDate} startDate Start date of the period to look
   * @param {CustomDate} endDate End date of the period to look
   * @param {string[] | null} codes Accounts codes
   * @param {string[] | null} tags Accounts tags
   * @param {number | null} partnerId Specific partner to target
   * @param {string} product The product to filter by
   * @param {string} country The country to filter by
   * @param {string} salesPerson The sales person to filter by
   * @param {number | null} companyId Specific company to target
   * @param {boolean} includeUnposted Wether or not select unposted entries
   * @returns {number}
   */
  getAmlQuantity(...args) {
    const data = this._fetchAmlData(...args)
    return data.quantity
  }

  /**
   * Gets the analytic balance for given parameters
   * @param {'balance' | 'quantity'} type The type of data to fetch
   * @param {CustomDate} startDate
   * @param {CustomDate} endDate
   * @param {string} budgetType
   * @param {string} budgetVersion
   * @param {string} account
   * @param {string[]} accountTags
   * @param {string} analyticAccount
   * @param {string} product
   * @param {string} partner
   * @param {string} salesPerson
   * @param {string} country
   * @param {number} companyId
   * @returns {number}
   */
  getAnalyticBalance(...args) {
    const data = this._fetchAnalyticData(...args)
    return data.balance
  }

  /**
   * Gets the analytic quantity for given parameters
   * @param {'balance' | 'quantity'} type The type of data to fetch
   * @param {CustomDate} startDate
   * @param {CustomDate} endDate
   * @param {string} budgetType
   * @param {string} budgetVersion
   * @param {string} account
   * @param {string[]} accountTags
   * @param {string} analyticAccount
   * @param {string} product
   * @param {string} partner
   * @param {string} salesPerson
   * @param {string} country
   * @param {number} companyId
   * @returns {number}
   */
  getAnalyticQuantity(...args) {
    const data = this._fetchAnalyticData(...args)
    return data.quantity
  }

  /**
   * Creates or Updates a specific analytic line according to the given parameters
   * @param {string} trigger determines if the function is running
   * @param {number} amount sets the new value to assign to the analytic item
   * @param {number} quantity sets the new value to assign to the analytic item
   * @param {object} paramsObj parameters object
   * @returns {string} result message
   */
  setAnalyticItem(trigger, amount, quantity, paramsObj) {
    return this.serverData.batch.get(
      "account.analytic.line",
      "set_analytic_item",
      camelToSnakeObject({trigger, amount, quantity, paramsObj})
    )
  }

  /**
   * Gets the total balance for a given period and account type
   * @param {CustomDate} startDate
   * @param {CustomDate} endDate
   * @param {string} accountType
   * @param {number|null} companyId
   * @param {boolean} includeUnposted
   * @returns {number}
   */
  getAmlBalanceByAccountType(startDate, endDate, accountType, companyId, includeUnposted) {
    const data = this.serverData.batch.get(
      "account.account",
      "get_aml_acc_type_data",
      camelToSnakeObject({
        startDate,
        endDate,
        accountType,
        companyId,
        includeUnposted,
      })
    )
    return data.balance
  }

  // -------------------------------------------------------------------------
  // Private
  // -------------------------------------------------------------------------

  /**
   * Fetch the account information (credit/debit) for the given account codes and tags
   * @private
   * @param {CustomDate} startDate Start date of the period to look
   * @param {CustomDate} endDate End date of the period to look
   * @param {string[]} codes Accounts codes
   * @param {string[]} tags Accounts tags
   * @param {number} partnerId Specific partner to target
   * @param {string} product The product to filter by
   * @param {string} country The country to filter by
   * @param {string} salesPerson The sales person to filter by
   * @param {number} companyId Specific company to target
   * @param {boolean} includeUnposted Whether or not select unposted entries
   * @returns {{ credit: number, debit: number }}
   */
  _fetchAmlData(
    startDate,
    endDate,
    codes,
    tags,
    partnerId,
    product,
    country,
    salesPerson,
    companyId,
    includeUnposted
  ) {
    this._validateDates(startDate, endDate)

    return this.serverData.batch.get(
      "account.account",
      "get_aml_data",
      camelToSnakeObject({
        startDate,
        endDate,
        codes,
        tags,
        partnerId,
        product,
        country,
        salesPerson,
        companyId,
        includeUnposted,
      })
    )
  }

  /**
   * Fetch analytic data (balance or quantity)
   * @private
   * @param {CustomDate} startDate
   * @param {CustomDate} endDate
   * @param {string} budgetType
   * @param {string} budgetVersion
   * @param {string} account
   * @param {string[]} accountTags
   * @param {string} analyticAccount
   * @param {string} product
   * @param {string} partner
   * @param {string} salesPerson
   * @param {string} country
   * @param {number} companyId
   * @returns {number}
   */
  _fetchAnalyticData(
    startDate,
    endDate,
    budgetType,
    budgetVersion,
    account,
    accountTags,
    analyticAccount,
    product,
    partner,
    salesPerson,
    country,
    companyId
  ) {
    this._validateDates(startDate, endDate)
    return this.serverData.batch.get(
      "account.analytic.line",
      "get_aal_data",
      camelToSnakeObject({
        startDate,
        endDate,
        budgetType,
        budgetVersion,
        account,
        accountTags,
        analyticAccount,
        product,
        partner,
        salesPerson,
        country,
        companyId,
      })
    )
  }

  /**
   * Validate start and end dates
   * @private
   * @param {CustomDate} startDate
   * @param {CustomDate} endDate
   * @throws {Error} If dates are invalid
   */
  _validateDates(startDate, endDate) {
    if (!startDate.year || !endDate.year) {
      throw new Error(_t("You must enter both Start and End dates"))
    }
    if (startDate.year < 1900) {
      throw new Error(sprintf(_t("%s is not a valid year."), startDate.year))
    }
    if (startDate.month > 12 || endDate.month > 12) {
      throw new Error(_t("Month must be between 1 and 12."))
    }
    const start = new Date(startDate.year, startDate.month - 1, startDate.day)
    const end = new Date(endDate.year, endDate.month - 1, endDate.day)
    if (start > end) {
      throw new Error(_t("End date must be greater than or equal to start date"))
    }
  }
}
