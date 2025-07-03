/** @odoo-module */

import {_lt} from "@web/core/l10n/translation"
import SyscoonAccountingPlugin from "./plugins/accounting_plugin"
import {registries} from "@odoo/o-spreadsheet"

const {featurePluginRegistry} = registries

featurePluginRegistry.add("SyscoonAccountingAggregates", SyscoonAccountingPlugin)
