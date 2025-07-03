/** @odoo-module **/
import {registry} from "@web/core/registry"
import {useService} from "@web/core/utils/hooks"
import {Component, useRef, onMounted, onWillUnmount} from "@odoo/owl"
import {Dropdown} from "@web/core/dropdown/dropdown"
import {DropdownItem} from "@web/core/dropdown/dropdown_item"
import {renderToElement} from "@web/core/utils/render"

class SystrayIcon extends Component {
  setup() {
    super.setup()
    this.action = useService("action")
    this.dropdownRef = useRef("weatherDropdown")
    this.observer = null
    onMounted(this.onMounted.bind(this))
    onWillUnmount(this.onWillUnmount.bind(this))
  }

  async onMounted() {
    await this._fetchWeatherForecastList()
    this._setupMutationObserver()
    this._setupOutsideClickHandler()
  }

  onWillUnmount() {
    if (this.observer) {
      this.observer.disconnect()
    }
    document.removeEventListener("click", this._onOutsideClick)
  }

  async _fetchWeatherForecastList() {
    try {
      this.weatherData = await this.env.services.rpc("/weather_app")
      const weatherData = this.weatherData
      const systrayIcon = document.getElementById("systray_icon")

      // Clear previous content before adding new
      systrayIcon.innerHTML = ""

      if (weatherData) {
        const weatherInfo = renderToElement("SystrayIcon", {weatherData})
        systrayIcon.appendChild(weatherInfo)
      } else {
        const errorInfo = renderToElement("SystrayIcon", {error: true})
        systrayIcon.appendChild(errorInfo)
      }
    } catch (error) {
      console.error("Error fetching weather information:", error)
    }
  }

  async _onClick(ev) {
    ev.stopPropagation()
    await this._fetchWeatherForecastList()
    const weatherData = this.weatherData

    const dropdownMenu = this.dropdownRef.el.querySelector("#systray_notif")
    const systrayDetails = this.dropdownRef.el.querySelector("#systray_details")

    if (dropdownMenu.style.display === "block") {
      this._hideDropdown()
    } else {
      dropdownMenu.style.display = "block"

      systrayDetails.innerHTML = ""

      if (weatherData) {
        const weatherInfo = renderToElement("SystrayDetails", {weatherData})
        systrayDetails.appendChild(weatherInfo)
      } else {
        const errorInfo = renderToElement("SystrayDetails", {error: true})
        systrayDetails.appendChild(errorInfo)
      }
    }
  }

  _setupMutationObserver() {
    const systrayContainer = document.querySelector(".o_menu_systray")
    if (!systrayContainer) return

    this.observer = new MutationObserver((mutations) => {
      for (let mutation of mutations) {
        if (mutation.type === "attributes" && mutation.attributeName === "class") {
          const target = mutation.target
          if (target.classList.contains("show") && !this.dropdownRef.el.contains(target)) {
            this._hideDropdown()
          }
        }
      }
    })

    this.observer.observe(systrayContainer, {
      attributes: true,
      subtree: true,
      attributeFilter: ["class"],
    })
  }

  _setupOutsideClickHandler() {
    this._onOutsideClick = this._onOutsideClick.bind(this)
    document.addEventListener("click", this._onOutsideClick)
  }

  _onOutsideClick(ev) {
    const weatherManager = this.dropdownRef.el
    if (!weatherManager.contains(ev.target)) {
      this._hideDropdown()
    }
  }

  _hideDropdown() {
    const dropdownMenu = this.dropdownRef.el.querySelector("#systray_notif")
    if (dropdownMenu) {
      dropdownMenu.style.display = "none"
    }
  }
}

SystrayIcon.template = "IconSystrayDropdown"
SystrayIcon.components = {Dropdown, DropdownItem}
SystrayIcon.props = {}
export const systrayItem = {Component: SystrayIcon}
registry.category("systray").add("SystrayIcon", systrayItem, {sequence: 100})
