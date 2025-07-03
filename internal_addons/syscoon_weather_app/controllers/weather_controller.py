# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

import logging
from collections import Counter
from datetime import datetime

import pytz
import requests
from odoo import http

_logger = logging.getLogger(__name__)
TIMEOUT = 5


class WeatherController(http.Controller):
    def get_api_key(self):
        return http.request.env["weather.config"].get_api_key()

    def get_city_and_country(self, timezone):
        # Extract the city and country from the timezone string
        parts = timezone.split("/")
        if len(parts) >= 2:
            country_code = parts[-2]
            city_name = parts[-1].replace("_", " ")
            return city_name, country_code
        return None, None

    def get_formatted_date(self, timestamp, timezone):
        # Create a timezone object using the offset
        local_timezone = pytz.FixedOffset(timezone / 60)
        # Convert the Unix timestamp to a datetime object in UTC
        utc_date = datetime.fromtimestamp(timestamp)
        # Localize the UTC datetime to the local timezone
        local_date = utc_date.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        # Format the localized date as desired
        return {
            "date": local_date.strftime("%A, %d %B %Y - %H:%M"),
            "short_date": local_date.strftime("%d %B").title(),
            "short_day": local_date.strftime("%a")[:3].title(),
            "day_num": local_date.strftime("%d"),
            "time": local_date.strftime("%H:%M"),
        }

    def group_temp_and_rain(self, weather_data):
        weather_dict = {}

        # Loop through the original list of dictionaries
        for data in weather_data:
            day_num = data["day_num"]
            temp = data["temp"]
            rain = data["rain"]
            short_date = data["short_date"]
            short_day = data["short_day"]
            icon_code = data["icon_code"]

            # If the day_num is not in the dictionary, add it with the current temp as both min and max
            if day_num not in weather_dict:
                weather_dict[day_num] = {
                    "day_num": day_num,
                    "temp_min": temp,
                    "temp_max": temp,
                    "rain_sum": 0,
                    "rain_count": 0,
                    "short_date": short_date,
                    "short_day": short_day,
                    "icon_code": icon_code,
                    "icon_codes": [],
                }

            # Update the minimum and maximum temperatures for the day
            weather_dict[day_num]["temp_min"] = min(
                weather_dict[day_num]["temp_min"], temp
            )
            weather_dict[day_num]["temp_max"] = max(
                weather_dict[day_num]["temp_max"], temp
            )

            # Update the rainfall sum and count if rain is not False
            if rain:
                # rain_value = float(rain)
                weather_dict[day_num]["rain_sum"] += rain
                weather_dict[day_num]["rain_count"] += 1

        # Create a list of icon_codes for the day and add the icon_code to it:
        # weather_dict[day_num]['icon_codes'] = []
        weather_dict[day_num]["icon_codes"].append(icon_code)

        # Calculate the average rainfall for each day
        for day_num in weather_dict:
            if weather_dict[day_num]["rain_count"] > 0:
                weather_dict[day_num]["rain_avg"] = round(
                    weather_dict[day_num]["rain_sum"]
                    * 100
                    / weather_dict[day_num]["rain_count"]
                )
            else:
                weather_dict[day_num]["rain_avg"] = 0

                # Determine the most frequent icon_code for the day
                icon_counter = Counter(weather_dict[day_num]["icon_codes"])
                most_common_icons = icon_counter.most_common(1)
                if most_common_icons:
                    weather_dict[day_num]["icon_code"] = most_common_icons[0][0]

            # Remove the temporary rain_sum and rain_count fields
            del weather_dict[day_num]["rain_sum"]
            del weather_dict[day_num]["rain_count"]
            del weather_dict[day_num]["icon_codes"]

        # Convert the dictionary values to a list
        result = list(weather_dict.values())

        return result

    @http.route("/weather_app", auth="public", type="json", methods=["POST"], csrf=False)
    def get_weather_data(self, **kwargs):
        user_id = http.request.env.uid
        user = http.request.env["res.users"].browse(user_id)
        timezone = user.tz
        city_name, country_code = self.get_city_and_country(timezone)

        api_key = self.get_api_key()[0]
        base_url = "http://api.openweathermap.org/data/2.5"

        try:
            # Make a request to get the current weather
            current_weather_url = f"{base_url}/weather"
            current_weather_params = {
                "q": f"{city_name},{country_code}" if country_code else city_name,
                "appid": api_key,
                "units": "metric",  # Use metric units (Celsius)
            }
            current_weather_response = requests.get(
                current_weather_url, params=current_weather_params, timeout=TIMEOUT
            )
            current_weather_response.raise_for_status()
            weather_result = current_weather_response.json()

            current_weather_timestamp = weather_result["dt"]
            current_weather_timezone_offset = weather_result["timezone"]
            cw_date = self.get_formatted_date(
                current_weather_timestamp, current_weather_timezone_offset
            )

            # Process the current weather data
            current_weather = {
                "short_date": cw_date["short_date"],
                "short_day": cw_date["short_day"],
                "city": city_name,
                "country": weather_result["sys"]["country"],
                "icon_code": weather_result["weather"][0]["icon"],
                "short_desc": weather_result["weather"][0]["main"].title(),
                "description": weather_result["weather"][0]["description"].title(),
                "temp": round(weather_result["main"]["temp"]),
                "temp_min": round(weather_result["main"]["temp_min"]),
                "temp_max": round(weather_result["main"]["temp_max"]),
                "wind_speed": weather_result["wind"]["speed"],
            }

            # Make a request to get the forecast data
            forecast_url = f"{base_url}/forecast"
            forecast_params = {
                "q": f"{city_name},{country_code}" if country_code else city_name,
                "appid": api_key,
                "units": "metric",  # Use metric units (Celsius)
                "cnt": 40,  # Get forecast for the next 40 intervals of 3 hours
            }
            forecast_response = requests.get(
                forecast_url, params=forecast_params, timeout=TIMEOUT
            )
            forecast_response.raise_for_status()
            forecast_result = forecast_response.json()

            # Process the forecast data
            forecast_list = []
            three_h_forecast = {}
            for forecast in forecast_result["list"]:
                timestamp = forecast["dt"]
                timezone_offset = forecast_result["city"]["timezone"]
                fw_date = self.get_formatted_date(timestamp, timezone_offset)
                date = fw_date["date"]

                three_h_forecast[date] = {
                    "date": date,
                    "short_date": fw_date["short_date"],
                    "short_day": fw_date["short_day"],
                    "day_num": fw_date["day_num"],
                    "time": fw_date["time"],
                    "city": city_name,
                    "icon_code": forecast["weather"][0]["icon"],
                    "temp": round(forecast["main"]["temp"]),
                    "rain": forecast["pop"],
                }

            forecast_list = list(three_h_forecast.values())

            info_list = self.group_temp_and_rain(forecast_list)

            return {
                "current_weather": current_weather,
                "forecast": forecast_list,
                "info_list": info_list,
            }

        except Exception as e:
            _logger.exception("Error in /weather_app route: %s", str(e))
            return {"error": str(e)}, 500
