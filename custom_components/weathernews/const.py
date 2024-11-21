"""
Support for Weather.com weather service.
For more details about this platform, please refer to the documentation at
https://github.com/jaydeethree/Home-Assistant-weatherdotcom
"""
from typing import Final

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_EXCEPTIONAL,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
    ATTR_CONDITION_WINDY_VARIANT
)

DOMAIN = 'weathernews'
# MANUFACTURER = 'WeatherUnderground'
# NAME = 'WeatherUnderground'
CONF_ATTRIBUTION = 'Data provided by the kr-weathernews.com weather service'
CONF_LANG = 'lang'

ENTRY_WEATHER_COORDINATOR = 'weather_coordinator'

# Language Supported Codes
LANG_CODES = ['ko-KR', 'en-US']
# Only the TWC  5-day forecast API handles the translation of phrases for values of the following data.
# However, when formatting a request URL a valid language must be passed along.
# dayOfWeek,daypartName,moonPhase,qualifierPhrase,uvDescription,windDirectionCardinal,windPhrase,wxPhraseLong

# 100 맑음
# 101 대체로 맑음
# 102 맑지만 한때 비
# 104 맑지만 한때 눈
# 200 흐림
# 201 대체로 흐림 
# 202 흐리고 한때 비
# 204 흐리고 한때 눈
# 300 비
# 301 맑지만 한때 비
# 302 한때 비
# 303 진눈깨비
# 308 빗발
# 400 눈
# 401 눈 해
# 402 눈 구름
# 403 눈 비
# 500 맑은 밤
# 501 대체로 맑은 밤
# 502 맑은 밤 한때 비
# 502 대체로 맑은 밤 한때 비
# 504 대체로 맑은 밤 한때 눈

# https://www.kr-weathernews.com/mv4/html/assets/images/weather-icon-set/icon1/light/day/400.svg
# https://www.jma.go.jp/bosai/forecast/img/400.svg

ICON_CONDITION_MAP: Final[dict[str, list[int]]] = {
    ATTR_CONDITION_CLEAR_NIGHT: [1100, 500, 501],  # 맑은 밤
    ATTR_CONDITION_CLOUDY: [200],       # 많은 구름 
    ATTR_CONDITION_EXCEPTIONAL: [],     # 특별한 44 is Not Available (N/A)
    ATTR_CONDITION_FOG: [],             # 안개
    ATTR_CONDITION_HAIL: [308],            # 빗발
    ATTR_CONDITION_LIGHTNING: [],       # 번개/뇌우
    ATTR_CONDITION_LIGHTNING_RAINY: [], # 번개/천둥, 비
    ATTR_CONDITION_PARTLYCLOUDY: [101, 102, 104, 201, 202],    # 구름 몇 개 
    ATTR_CONDITION_POURING: [],         # 쏟아지는 비
    ATTR_CONDITION_RAINY: [300, 301, 302, 502],        # 비
    ATTR_CONDITION_SNOWY: [204, 400, 401, 402, 504],           # 눈
    ATTR_CONDITION_SNOWY_RAINY: [303, 403],     # 눈과 비
    ATTR_CONDITION_SUNNY: [100],        # 햇빛
    ATTR_CONDITION_WINDY: [],           # 바람
    ATTR_CONDITION_WINDY_VARIANT: []    # 바람과 구름
}
SNOWYRAIN_CONDITION_MAP = {
    'pouring': [ATTR_CONDITION_POURING],
    'rain': [ATTR_CONDITION_PARTLYCLOUDY,ATTR_CONDITION_RAINY,ATTR_CONDITION_HAIL,ATTR_CONDITION_LIGHTNING_RAINY],
    'snow': [ATTR_CONDITION_SNOWY],
    'snowrainy': [ATTR_CONDITION_SNOWY_RAINY]
}
DEFAULT_LANG = 'ko-KR'
API_IMPERIAL: Final = "imperial"
API_METRIC: Final = "metric"
API_URL_IMPERIAL: Final = "e"
API_URL_METRIC: Final = "m"

TEMPUNIT = 0
LENGTHUNIT = 1
SPEEDUNIT = 3
PRESSUREUNIT = 4

RESULTS_CURRENT = 'current'
RESULTS_FORECAST_DAILY = 'daily'
RESULTS_FORECAST_HOURLY = 'hourly'

FIELD_CLOUD_COVER = 'cloudCover' # 
FIELD_DAYPART = 'daypart' #
FIELD_DESCRIPTION = 'wxPhraseLong' #
FIELD_DEW_POINT = 'dewpt'
FIELD_FEELS_LIKE = 'feeltemp'
FIELD_HUMIDITY = 'rhum'
FIELD_HUMIDITY_HOURLY = 'humi'
FIELD_ICONCODE = 'wx'
FIELD_ICONCODE_DAILY = 'wx_am'
FIELD_ICONCODE_AM = 'wx_am'
FIELD_ICONCODE_PM = 'wx_pm'
FIELD_DAYORNIGHT = 'dayOrNight'
FIELD_PRECIPCHANCE = 'pop'
FIELD_PRESSURE = 'press'
FIELD_PRECIPITATION = 'prec'
FIELD_TEMPERATUREMAX = 'tmax'
FIELD_TEMPERATUREMIN = 'tmin'
FIELD_TEMP = 'temp'
FIELD_UV_INDEX = 'uv'
FIELD_VALIDTIMELOCAL = 'TimeLocal'
FIELD_VALIDTIMEUTC = 'TimeUtc'
FIELD_VISIBILITY = 'visi'
FIELD_WINDDIRECTIONCARDINAL = 'wdir'
FIELD_WINDDIR = 'wdir' #
FIELD_WINDGUST = 'windGust' #
FIELD_WINDSPEED = 'wspd'

ICON_THERMOMETER = 'mdi:thermometer'
ICON_UMBRELLA = 'mdi:umbrella'
ICON_WIND = 'mdi:weather-windy'