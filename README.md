# Home-Assistant-Weathernews.com
Home Assistant custom integration for Weathernews.com.
Includes a native Home Assistant Weather Entity and a variety of weather sensors.  

This is a fork of the excellent [weatherdotcom integration by @jaydeethree](https://github.com/jaydeethree/Home-Assistant-weatherdotcom)

* **kr-weathernews.com 날씨 데이타를 사용합니다. 날씨 데이타 저작권은 모두 `Weathernews`에 있습니다**
* **개인(본인 또는 그 동거 가족)이 사적 이용 목적에 한해 사용가능합니다!**

-------------------

# Installation Prerequisites
Please review the minimum requirements below to determine whether you will be able to
install and use the software.

- This integration requires Home Assistant Version 2023.9 or greater

# Screenshot

![weather](https://github.com/dugurs/ha-weathernews/assets/41262994/30621ead-c5a5-4307-8894-26dd5307407b)

![sensors](https://github.com/dugurs/ha-weathernews/assets/41262994/37a9aa51-ce74-4d7d-ac27-6eb261a9c96a)

[Back to top](#top)

# Installation

This integration is available in HACS, so just install it from there and then:

1. HACS integration add repository `https://github.com/dugurs/ha-weathernews`
   
   [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdugurs%2Fha-weathernews)
   
2. In Home Assistant Settings, select DEVICES & SERVICES, then ADD INTEGRATION. `웨더뉴스 WeatherNews`
   
   [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=weathernews)
3. Select the "웨더뉴스 WeatherNews" integration.
4. url 열기 https://www.kr-weathernews.com/
5. 도시검색 > 도시 선택
6. 주소표시줄 ?region=XXXXXXXXXX의 XXXXXXXXXX 숫자를 "지역코드"에 넣기 

[Back to top](#top)

# Sensors Created By This Integration
The following Weathernews.com data is available in the `weather.wn_<LOCATION_NAME>` entity:

Current conditions:
- Condition (icon)
- Temperature
- Barometric pressure
- Wind speed
- Wind bearing (cardinal direction)
- Visibility

Forecast (daily and hourly):
- Date/time of forecast
- Temperature (high)
- Temperature (low)
- Condition (icon)
- Precipitation quantity
- Precipitation probability
- Wind speed
- Wind bearing (cardinal direction)

To access these values in automations, scripts, etc. you will need to create triggered template sensors for them. [This post](https://community.home-assistant.io/t/customising-the-bom-weather-and-lovelace-now-in-hacs/123549/1465) on the Home Assistant forums provides details about how to do that.

In addition to the Weather entity, these additional sensors will be created by this integration:

* `sensor.wn_<LOCATION_NAME>_cloud_ceiling` - distance to the lowest cloud layer, or 0 if there are no clouds
* `sensor.wn_<LOCATION_NAME>_cloud_cover_phrase` - a description of the current cloud cover, e.g. "Clear" or "Mostly Cloudy"
* `sensor.wn_<LOCATION_NAME>_dewpoint` - the current dew point
* `sensor.wn_<LOCATION_NAME>_heat_index` - the current heat index, which is what the current temperature "feels like" when combined with the current humidity
* `sensor.wn_<LOCATION_NAME>_latitude` - the latitude that is configured for this location
* `sensor.wn_<LOCATION_NAME>_local_observation_time` - the time that the Weather.com data was generated
* `sensor.wn_<LOCATION_NAME>_longitude` - the longitude that is configured for this location
* `sensor.wn_<LOCATION_NAME>_precipitation_last_hour` - the quantity of precipitation in the last hour
* `sensor.wn_<LOCATION_NAME>_precipitation_last_6_hours` - the quantity of precipitation in the last 6 hours
* `sensor.wn_<LOCATION_NAME>_precipitation_last_24_hours` - the quantity of precipitation in the last 24 hours
* `sensor.wn_<LOCATION_NAME>_pressure` - the current barometric pressure
* `sensor.wn_<LOCATION_NAME>_pressure_tendency_trend` - the current trend for barometric pressure, e.g. "Rising" or "Falling"
* `sensor.wn_<LOCATION_NAME>_relative_humidity` - the current relative humidity
* `sensor.wn_<LOCATION_NAME>_temperature` - the current temperature
* `sensor.wn_<LOCATION_NAME>_temperature_feels_like` - what the current temperature "feels like" when combined with the current heat index and wind chill
* `sensor.wn_<LOCATION_NAME>_uv_index` - the current UV index, ranging from 0 (very low) to 10 (very high)
* `sensor.wn_<LOCATION_NAME>_weather_description` - the current weather description, e.g. "Freezing Rain" or "Scattered Showers"
* `sensor.wn_<LOCATION_NAME>_wind_chill` - the current wind chill, which is what the current temperature "feels like" when combined with the current wind
* `sensor.wn_<LOCATION_NAME>_wind_direction_cardinal` - the current cardinal wind direction - for example: North
* `sensor.wn_<LOCATION_NAME>_wind_direction_degrees` - the current cardinal wind direction in degrees
* `sensor.wn_<LOCATION_NAME>_wind_gust` - the current wind gust speed
* `sensor.wn_<LOCATION_NAME>_wind_speed` - the current wind speed



[Back to top](#top)

# Localization

Sensor "friendly names" are set via translation files.  
Weather.com translation files are located in the 'weathernews/weather_translations' directory.
Files were translated, using 'en.json' as the base, via https://translate.i18next.com.  
Translations only use the base language code and not the variant (i.e. zh-CN/zh-HK/zh-TW uses zh).  
The default is en-US (translations/en.json) if the lang: option is not set in the Weather.com config.  
If lang: is set (i.e.  lang: de-DE), then the translations/de.json file is loaded, and the Weather.com API is queried with de-DE.    
The translation file applies to all sensor friendly names.    
Available lang: options are:  
```
'en-US', 'ko-KR'
```
Weather Entity translations are handled by Home Assistant and configured under the User -> Language setting.

[Back to top](#top)
