# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import os
import time
import urllib2
import urllib
import json
import xbmcplugin

addon = xbmcaddon.Addon('script.cortanaWeather')
CITY = addon.getSetting('city')
WEATHER_URL = "https://wttr.in/{}?format=j1".format(urllib.quote(CITY))
TEMP_UNIT = addon.getSetting('temp_unit')
ICON_SAVE_PATH = "special://temp/weather.png"

def get_weather_data():
	try:
		req = urllib2.Request(WEATHER_URL, headers={'User-Agent': 'Mozilla/5.0'})
		response = urllib2.urlopen(req, timeout=5)
		data = response.read()
		weather = json.loads(data)
		current_condition = weather['current_condition'][0]
		main_desc = current_condition['weatherDesc'][0]['value']
		temp_c = current_condition.get('temp_C', "??")
		temp_f = current_condition.get('temp_F', "??")
		weather_code = current_condition.get('weatherCode', None)

		# Extract location info
		area_info = weather.get('nearest_area', [{}])[0]
		area_name = area_info.get('areaName', [{}])[0].get('value', '')
		region = area_info.get('region', [{}])[0].get('value', '')
		country = area_info.get('country', [{}])[0].get('value', '')
		full_location = "{}, {}".format(area_name, country)

		if not temp_c or not temp_c.strip() or not temp_c.replace('-','').isdigit():
			temp_c = "??"
		if not temp_f or not temp_f.strip() or not temp_f.replace('-','').isdigit():
			temp_f = "??"

		return main_desc, temp_c, temp_f, weather_code, full_location
	except Exception as e:
		xbmc.log("Failed to fetch weather: {}".format(e), xbmc.LOGERROR)
		return "Clear", "??", "??", None, "Unknown Location"


def map_wttr_code_to_owm_icon(code):
	mapping = {
		"113": "01d",
		"116": "02d",
		"119": "03d",
		"122": "04d",
		"143": "50d",
		"176": "09d",
		"179": "13d",
		"182": "13d",
		"185": "13d",
		"200": "11d",
		"227": "13d",
		"230": "13d",
		"248": "50d",
		"260": "50d",
		"263": "09d",
		"266": "10d",
		"281": "13d",
		"284": "13d",
		"293": "09d",
		"296": "10d",
		"299": "09d",
		"302": "10d",
		"305": "09d",
		"308": "10d",
		"311": "13d",
		"314": "13d",
		"317": "13d",
		"320": "13d",
		"323": "13d",
		"326": "13d",
		"329": "13d",
		"332": "13d",
		"335": "13d",
		"338": "13d",
		"350": "13d",
		"353": "09d",
		"356": "10d",
		"359": "09d",
		"362": "13d",
		"365": "13d",
		"368": "13d",
		"371": "13d",
		"374": "13d",
		"377": "13d",
		"386": "11d",
		"389": "11d",
		"392": "11d",
		"395": "13d",
	}
	return mapping.get(str(code), "01d")  # default to clear day icon

def download_icon(weather_code):
	if not weather_code:
		return
	try:
		owm_icon_code = map_wttr_code_to_owm_icon(weather_code)
		icon_url = "http://openweathermap.org/img/wn/{}@2x.png".format(owm_icon_code)
		req = urllib2.Request(icon_url, headers={'User-Agent': 'Mozilla/5.0'})
		response = urllib2.urlopen(req, timeout=5)
		icon_data = response.read()
		with open(ICON_SAVE_PATH, 'wb') as f:
			f.write(icon_data)
	except Exception as e:
		xbmc.log("Failed to download icon: {}".format(e), xbmc.LOGERROR)


def get_current_hour():
	# Return string like "1PM", "12AM"
	hour_with_zero = time.strftime("%I%p")
	return hour_with_zero.lstrip("0")

def show_notification(hour, weather_desc, temp_c, temp_f, location):
	if TEMP_UNIT == "F":
		temp = "{}°F".format(temp_f)
	else:
		temp = "{}°C".format(temp_c)
	xbmc.executebuiltin(
		'Notification("cortanaWeather - {temp}", "{location} - {message}", 10000, "{icon}")'.format(
			hour=hour,
			location=location,
			message=weather_desc,
			temp=temp,
			icon=ICON_SAVE_PATH if os.path.exists(ICON_SAVE_PATH) else ""
		)
	)

def main():
	last_hour = None
	while True:
		current_hour = get_current_hour()
		if current_hour != last_hour:
			last_hour = current_hour
			weather_desc, temp_c, temp_f, weather_code, location = get_weather_data()
			if "??" not in (temp_c, temp_f) and "Unknown" not in location:
				download_icon(weather_code)
				show_notification(current_hour, weather_desc, temp_c, temp_f, location)
			else:
				xbmc.log("Weather data incomplete, skipping notification", xbmc.LOGWARNING)
		xbmc.sleep(30000)

if __name__ == "__main__":
	main()
