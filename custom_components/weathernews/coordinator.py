"""The Weather.com data coordinator."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp
import async_timeout
import re
import copy

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import json
from homeassistant.util.unit_system import METRIC_SYSTEM
from homeassistant.const import (
    PERCENTAGE, UnitOfPressure, UnitOfTemperature, UnitOfLength, UnitOfSpeed, UnitOfVolumetricFlux)
from .const import (
    ICON_CONDITION_MAP,
    SNOWYRAIN_CONDITION_MAP,
    FIELD_DAYPART,
    FIELD_HUMIDITY,
    FIELD_TEMP,
    FIELD_TEMPERATUREMAX,
    FIELD_TEMPERATUREMIN,
    FIELD_VALIDTIMEUTC,
    FIELD_VALIDTIMELOCAL,
    FIELD_WINDDIR,
    FIELD_WINDDIRECTIONCARDINAL,
    FIELD_WINDGUST,
    FIELD_WINDSPEED,
    FIELD_DAYORNIGHT,
    FIELD_PRECIPCHANCE,
    FIELD_PRECIPITATION,
    FIELD_ICONCODE,
    DOMAIN,
    RESULTS_CURRENT,
    RESULTS_FORECAST_DAILY,
    RESULTS_FORECAST_HOURLY
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=20)


@dataclass
class WeatherUpdateCoordinatorConfig:
    """Class representing coordinator configuration."""

    api_key: str
    location_name: str
    unit_system_api: str
    unit_system: str
    lang: str
    update_interval = MIN_TIME_BETWEEN_UPDATES


class WeatherUpdateCoordinator(DataUpdateCoordinator):
    """The Weather.com update coordinator."""

    icon_condition_map = ICON_CONDITION_MAP
    snowrain_condition_map = SNOWYRAIN_CONDITION_MAP

    def __init__(
            self, hass: HomeAssistant, config: WeatherUpdateCoordinatorConfig
    ) -> None:
        """Initialize."""
        self._hass = hass
        self._api_key = config.api_key
        self._location_name = config.location_name
        self._unit_system_api = config.unit_system_api
        self.unit_system = config.unit_system
        self._lang = config.lang
        self.data = None
        self._session = async_get_clientsession(self._hass)
        self._tranfile = self.get_tran_file()

        if self._unit_system_api == 'm':
            self.units_of_measurement = (UnitOfTemperature.CELSIUS, UnitOfLength.MILLIMETERS, UnitOfLength.METERS,
                                        UnitOfSpeed.KILOMETERS_PER_HOUR, UnitOfPressure.MBAR,
                                        UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR, PERCENTAGE)
            self.visibility_unit = UnitOfLength.KILOMETERS
        else:
            self.units_of_measurement = (UnitOfTemperature.FAHRENHEIT, UnitOfLength.INCHES, UnitOfLength.FEET,
                                        UnitOfSpeed.MILES_PER_HOUR, UnitOfPressure.INHG,
                                        UnitOfVolumetricFlux.INCHES_PER_HOUR, PERCENTAGE)
            self.visibility_unit = UnitOfLength.MILES

        super().__init__(
            hass,
            _LOGGER,
            name="WeatherUpdateCoordinator",
            update_interval=config.update_interval,
        )

    @property
    def is_metric(self):
        """Determine if this is the metric unit system."""
        return self._hass.config.units is METRIC_SYSTEM

    @property
    def location_name(self):
        """Return the location used for data."""
        return self._location_name

    @property
    def api_key(self):
        """Return the location used for data."""
        return self._api_key

    async def _async_update_data(self) -> dict[str, Any]:
        return await self.get_weather()

    async def get_weather(self):
        """Get weather data."""
        headers = {
            'Accept-Encoding': 'gzip',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        try:
            
            with async_timeout.timeout(10):
                """CURRENT, FORECAST"""
                # https://www.kr-weathernews.com/mv3/if/main_v4.fcgi?loc=1147010300&language=ko
                url = self._build_url('https://www.kr-weathernews.com/mv3/if/main_v4.fcgi?loc={apiKey}&language={lang}')
                response = await self._session.get(url, headers=headers)
                result_data = await response.json(content_type=None)

                if result_data is None:
                    raise ValueError('NO RESULT')
                self._check_errors(url, result_data)
                lat = result_data['lat']
                lon = result_data['lon']

            with async_timeout.timeout(10):
                """날씨요약"""
                # https://galaxy.kr-weathernews.com/api_v2/weather_v4.cgi?loc=1147010300
                url = self._build_url('https://galaxy.kr-weathernews.com/api_v2/weather_v4.cgi?loc={apiKey}&language={lang}')
                response = await self._session.get(url, headers=headers)
                result_data2 = await response.json(content_type=None)

                if result_data2 is None:
                    raise ValueError('NO RESULT2')
                self._check_errors(url, result_data2)

            with async_timeout.timeout(10):
                """통합대기등급"""
                # https://www.kr-weathernews.com/mv3/if/main2_v2.fcgi?lat=37.544147&lon=126.8357822
                url = self._build_url(f"https://www.kr-weathernews.com/mv3/if/main2_v2.fcgi?lat={lat}&lon={lon}")
                response = await self._session.get(url, headers=headers)
                result_data3 = await response.json(content_type=None)

                if result_data3 is None:
                    raise ValueError('NO RESULT3')
                self._check_errors(url, result_data3)
                tempdiff = int(result_data3['current']['tempdiff'])
                if tempdiff == 0:
                    tempdiffCmt = "어제와 같아요"
                else:
                    tempdiffCmt = "어제보다 {}도 {}아요".format(abs(tempdiff), "높" if tempdiff > 0 else "낮")

            pmForcastDaily = []
            pmForcastHourly = []

            with async_timeout.timeout(10):
                """미세먼지예보"""
                # https://www.kr-weathernews.com/mv3/if/pm_v4.fcgi?loc=1147010300
                url = self._build_url("https://www.kr-weathernews.com/mv3/if/pm_v4.fcgi?loc={apiKey}")
                response = await self._session.get(url, headers=headers)
                result_data4 = await response.json(content_type=None)

                if result_data4 is None:
                    raise ValueError('NO RESULT4')
                self._check_errors(url, result_data4)
                
                # new_item = {'date': datetime.strptime(result_data2[0]['publish_TimeLocal'], "%Y/%m/%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S"), 'pm10': result_data2[0]['air']['pm10']['value'], 'pm25': result_data2[0]['air']['pm25']['value']}
                # pmForcastDaily.append(new_item)
                # pmForcastHourly.append(new_item)
                for item in result_data4['pm']['forcast']['daily']:
                    new_item = {
                        "date": f'{item["year"]}-{item["mon"]:02d}-{item["day"]:02d} 00:00:00',
                        "pm10": item["pm10"],
                        "aqi": item["aqi"],
                        "pm25": item["pm25"],
                        "o3": item["o3"]
                    }
                    pmForcastDaily.append(new_item)

                for item in result_data4['pm']['forcast']['hourly']:
                    new_item = {
                        "date": f'{item["year"]}-{item["mon"]:02d}-{item["day"]:02d} {item["hour"]:02d}:00:00',
                        "pm10": item["pm10"],
                        "pm25": item["pm25"]
                    }
                    pmForcastHourly.append(new_item)

            # 비시작시간
            remainhour = 24 - int(result_data['hourly'][0]['hour']) 
            precipHourTodayAttr = self._get_precip_hour(result_data['hourly'], remainhour) # 오늘 
            precipHourTomarrowAttr = self._get_precip_hour(result_data['hourly'], remainhour+24, result_data['daily'][0]['day']) # 내일까지
            precipHour3Attr = self._get_precip_hour(result_data['hourly'], 3, result_data['daily'][0]['day']) # 3시간
            precipHour6Attr = self._get_precip_hour(result_data['hourly'], 6, result_data['daily'][0]['day']) # 6시간
            precipHour9Attr = self._get_precip_hour(result_data['hourly'], 9, result_data['daily'][0]['day']) # 9시간
            precipHour12Attr = self._get_precip_hour(result_data['hourly'], 12, result_data['daily'][0]['day']) # 12시간

            # 통합대기 지수
            khai = int(result_data3['aq']['khai'])
            if khai < 50:
                khaiDesc = '좋음'
            elif khai < 100:
                khaiDesc = '보통'
            elif khai < 250:
                khaiDesc = '나쁨'
            elif khai < 500:
                khaiDesc = '매우나쁨'
            else:
                khaiDesc = ''

            # 통합대기 속성추가
            result_data3['aq'].update({
                'pm10Desc': result_data2[0]['air']['pm10']['description'],
                'pm25Desc': result_data2[0]['air']['pm25']['description'],
                'khaiDesc': khaiDesc
            })

            # 열지수
            heatIndex = heatIndexCalc(result_data['current'][FIELD_TEMP], result_data['current'][FIELD_HUMIDITY])
            
            hour = int(result_data['hourly'][0]['hour'])
            mon = int(result_data['hourly'][0]['mon'])
            weather_briefing = {}
            weather_briefing['현재 날씨'] = f"현재 날씨 {result_data2[0]['cur_cmt']}"
            weather_briefing['온도'] = f"온도 {result_data['current'][FIELD_TEMP]}°C"
            weather_briefing['어제와 온도차'] = tempdiffCmt
            weather_briefing['최저 온도'] = f"최저 {result_data['current'][FIELD_TEMPERATUREMIN]}°C"
            weather_briefing['최고 온도'] = f"최고 {result_data['current'][FIELD_TEMPERATUREMAX]}°C"
            weather_briefing['습도'] = f"습도 {result_data['current'][FIELD_HUMIDITY]}%"
            weather_briefing['강수확률'] = f"강수확률 {precipHour12Attr['max_pop']}%"
            weather_briefing['강수예상'] = f"{precipHour12Attr['cmt']}, {precipHour12Attr['cmt2']} 예상"
            weather_briefing['미세먼지'] = f"미세먼지 {result_data2[0]['air']['pm10']['description']}"
            weather_briefing['초미세먼지'] = f"초미세먼지 {result_data2[0]['air']['pm25']['description']}"
            weather_briefing['통합대기'] = f"통합대기 {result_data3['aq']['khaiDesc']}"

            weather_briefing_cmt = copy.deepcopy(weather_briefing)
            if mon not in [11,12,1,2] or hour > 10:
                del weather_briefing_cmt['최저 온도']
            if hour > 14:
                del weather_briefing_cmt['최고 온도']
            if precipHour12Attr['cmt'] == '안옴':
                del weather_briefing_cmt['강수확률']
                del weather_briefing_cmt['강수예상']

            weather_briefing_str = [str(value) for value in weather_briefing_cmt.values() if value]
            weather_briefing_join = ", ".join(weather_briefing_str) + "입니다."

            # 현재날씨 속성추가
            result_data['current'].update({
                'sunrise': result_data['sunrise'],
                'sunset': result_data['sunset'],
                'pop': result_data['daily'][0]['pop'],
                FIELD_DAYORNIGHT: result_data['hourly'][0][FIELD_DAYORNIGHT],
                'cur_cmt': result_data2[0]['cur_cmt'],
                'day_cmt': result_data2[0]['daily'][0]['day_cmt'],
                'night_cmt': result_data2[0]['daily'][0]['night_cmt'],
                'dayShortCmt': result_data2[0]['daily'][0]['dayShortCmt'],
                'nextDayShortCmt': result_data2[0]['daily'][0]['nextDayShortCmt'],
                'pm10Attr': result_data2[0]['air']['pm10'],
                'pm25Attr': result_data2[0]['air']['pm25'],
                'pm10Desc': result_data2[0]['air']['pm10']['description'],
                'pm25Desc': result_data2[0]['air']['pm25']['description'],
                'heatindex': heatIndex['heatindex'],
                'heatindexAttr': heatIndex,
                'khai': result_data3['aq']['khai'],
                'pm': result_data3['aq'],
                'tempdiff': tempdiff,
                'tempdiffCmt': tempdiffCmt,
                'precipHourToday': precipHourTodayAttr['cmt'],
                'precipHourTodayAttr': precipHourTodayAttr,
                'precipHourTomarrow': precipHourTomarrowAttr['cmt'],
                'precipHourTomarrowAttr': precipHourTomarrowAttr,
                'precipHour3': precipHour3Attr['cmt'],
                'precipHour3Attr': precipHour3Attr,
                'precipHour6': precipHour6Attr['cmt'],
                'precipHour6Attr': precipHour6Attr,
                'precipHour9': precipHour9Attr['cmt'],
                'precipHour9Attr': precipHour9Attr,
                'precipHour12': precipHour12Attr['cmt'],
                'precipHour12Attr': precipHour12Attr,
                'weatherBriping': weather_briefing_join,
                'weatherBripingAttr': weather_briefing,
                'pmForcast': result_data4['pm']['forcast']['hourly'][0]['pm10'],
                'pmForcastDaily': pmForcastDaily,
                'pmForcastHourly': pmForcastHourly
            })
            
            result = {
                RESULTS_CURRENT: result_data['current'],
                RESULTS_FORECAST_DAILY: result_data['daily'],
                RESULTS_FORECAST_HOURLY: result_data['hourly'],
            }

            self.data = result

            return result

        except ValueError as err:
            _LOGGER.error("Check Weather API %s", err.args)
            raise UpdateFailed(err)
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching Weather data: %s", repr(err))
            raise UpdateFailed(err)
        # _LOGGER.debug(f'Weather data {self.data}')

    def _build_url(self, baseurl):
        return baseurl.format(
            apiKey=self._api_key,
            lang=self._lang.split('-', 1)[0]
        )

    def _check_errors(self, url: str, response: dict):
        # _LOGGER.debug(f'Checking errors from {url} in {response}')
        if 'errors' not in response:
            return
        if errors := response['errors']:
            raise ValueError(
                f'Error from {url}: '
                '; '.join([
                    e['message']
                    for e in errors
                ])
            )

    def _get_precip_hour(self, hours: dict, limit: int, day: int = None):
        data = {}
        end_hour = ''
        sum_prec = 0.0
        max_pop = 0
        cmt = '안옴'
        for idx, hour_data in enumerate(hours[:limit]):
            # 강수량이 있으면, 비오는 시작시간
            if data=={} and float(hour_data[FIELD_PRECIPITATION]) > 0:
                snowrain = self.tran_key(self._condition_to_snowrain(self._iconcode_to_condition(int(hour_data[FIELD_ICONCODE]))))
                tomorrow = '' if day==None or day==hour_data['day'] else '내일'
                cmt = f"{tomorrow} {hour_data['hour']}시 {snowrain}"
                data = hour_data
                end_hour = hour_data['hour']
                end_idx = idx
                end_sum_prec = float(hour_data[FIELD_PRECIPITATION])
            # 강수량
            sum_prec += float(hour_data[FIELD_PRECIPITATION])
            # 강수확률
            if max_pop < int(hour_data[FIELD_PRECIPCHANCE]):
                max_pop = int(hour_data[FIELD_PRECIPCHANCE])
            # 몇시까지(연속되는 강수량)
            if data!={} and idx-end_idx == 1 and float(hour_data[FIELD_PRECIPITATION]) > 0:
                end_idx = idx
                end_hour = hour_data['hour']
                end_sum_prec += float(hour_data[FIELD_PRECIPITATION])
        if sum_prec > 0:
            end_sum_prec = round(end_sum_prec,1)
            data.update({
                'cmt': cmt,
                'cmt2': f"{end_hour}시 까지 {int(end_sum_prec) if end_sum_prec == int(end_sum_prec) else end_sum_prec}mm",
                'hourlimit': limit,
                'end_hour': end_hour,
                'end_sum_prec': end_sum_prec,
                'sum_prec': round(sum_prec,1),
                'max_pop': max_pop,
                'snowrain': snowrain,
            })
            return data
        return {
            'hour': '-',
            'prec': 0,
            'pop': 0,
            'cmt': "안옴",
            'cmt2': '',
            'hour_limit': limit,
            'end_hour': '-',
            'end_sum_prec': 0,
            'sum_prec': 0,
            'max_pop': max_pop,
            'snowrain': '-'
        }

    def get_current(self, field):
        try:
            ret = self.data[RESULTS_CURRENT][field]
        except KeyError as err:
            _LOGGER.error("Current KeyError %s", repr(err))
            return None
            
        # if field not in [
        #     FIELD_DAYORNIGHT,
        #     FIELD_VALIDTIMELOCAL,
        #     FIELD_WINDDIRECTIONCARDINAL,
        # ]:
        if isinstance(ret, str) and bool(re.match(r'^[0-9][0-9.]*$', ret)):
            ret = float(ret)
        return ret

    def get_forecast(self, field, data):
        try:
            ret = data[field]
        except KeyError as err:
            _LOGGER.error("Forecast KeyError %s", repr(err))
            return None
            
        if isinstance(ret, str) and bool(re.match(r'^[0-9][0-9.]*$', ret)):
            ret = float(ret)
        return ret

    @classmethod
    def _iconcode_to_condition(cls, icon_code):
        for condition, iconcodes in cls.icon_condition_map.items():
            if icon_code in iconcodes:
                return condition
        _LOGGER.warning(f'Unmapped iconCode. (44 is Not Available (N/A)) "{icon_code}". ')
        return None
    
    @classmethod
    def _condition_to_snowrain(cls, condition):
        for snowrain, conditions in cls.snowrain_condition_map.items():
            if condition in conditions:
                return snowrain
        _LOGGER.warning(f'Unmapped condition. (44 is Not Available (N/A)) "{condition}". ')
        return None

    @classmethod
    def _format_timestamp(cls, timestamp_secs):
        return datetime.utcfromtimestamp(timestamp_secs).isoformat('T') + 'Z'

    def get_tran_file(self):
        """get translation file for Weather.com sensor friendly_name"""
        tfiledir = f'{self._hass.config.config_dir}/custom_components/{DOMAIN}/weather_translations/'
        tfilename = self._lang.split('-', 1)[0]
        try:
            tfiledata = json.load_json(f'{tfiledir}{tfilename}.json')
        except Exception:  # pylint: disable=broad-except
            tfiledata = json.load_json(f'{tfiledir}en.json')
            _LOGGER.warning(f'Sensor translation file {tfilename}.json does not exist. Defaulting to en-US.')
        return tfiledata

    def tran_key(self, key):
        """Return the name of the sensor."""
        if key in self._tranfile.keys():
            return self._tranfile[key]
        return key

class InvalidApiKey(HomeAssistantError):
    """Error to indicate there is an invalid api key."""

def heatIndexCalc(temp,hum):
    """https://github.com/gregnau/heat-index-calc/blob/master/heat-index-calc.py"""

    temp = int(temp)
    # ...then wait for the relative humidity in % value
    hum = int(hum)
    # Convert celius to fahrenheit (heat-index is only fahrenheit compatible)
    fahrenheit = ((temp * 9/5) + 32)

    # Creating multiples of 'fahrenheit' & 'hum' values for the coefficients
    T2 = pow(fahrenheit, 2)
    T3 = pow(fahrenheit, 3)
    H2 = pow(hum, 2)
    H3 = pow(hum, 3)

    # Coefficients for the calculations
    # C1 = [ -42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-03, -5.481717e-02, 1.22874e-03, 8.5282e-04, -1.99e-06]
    C2 = [ 0.363445176, 0.988622465, 4.777114035, -0.114037667, -0.000850208, -0.020716198, 0.000687678, 0.000274954, 0]
    # C3 = [ 16.923, 0.185212, 5.37941, -0.100254, 0.00941695, 0.00728898, 0.000345372, -0.000814971, 0.0000102102, -0.000038646, 0.0000291583, 0.00000142721, 0.000000197483, -0.0000000218429, 0.000000000843296, -0.0000000000481975]

    # Calculating heat-indexes with 3 different formula
    # heatindex1 = C1[0] + (C1[1] * fahrenheit) + (C1[2] * hum) + (C1[3] * fahrenheit * hum) + (C1[4] * T2) + (C1[5] * H2) + (C1[6] * T2 * hum) + (C1[7] * fahrenheit * H2) + (C1[8] * T2 * H2)
    heatindex2 = C2[0] + (C2[1] * fahrenheit) + (C2[2] * hum) + (C2[3] * fahrenheit * hum) + (C2[4] * T2) + (C2[5] * H2) + (C2[6] * T2 * hum) + (C2[7] * fahrenheit * H2) + (C2[8] * T2 * H2)
    # heatindex3 = C3[0] + (C3[1] * fahrenheit) + (C3[2] * hum) + (C3[3] * fahrenheit * hum) + (C3[4] * T2) + (C3[5] * H2) + (C3[6] * T2 * hum) + (C3[7] * fahrenheit * H2) + (C3[8] * T2 * H2) + (C3[9] * T3) + (C3[10] * H3) + (C3[11] * T3 * hum) + (C3[12] * fahrenheit * H3) + (C3[13] * T3 * H2) + (C3[14] * T2 * H3) + (C3[15] * T3 * H3)

    # 32 주의, 39 매우주의, 51 위험 , 매우위
    # 통합대기 지수
    heatindex = round(((heatindex2 - 32) * 5/9), 0)
    if heatindex > 51:
        heatgrade = '매우위험'
    elif heatindex > 39:
        heatgrade = '위험'
    elif heatindex > 32:
        heatgrade = '매우주의'
    elif heatindex > 27:
        heatgrade = '주의'
    else:
        heatgrade = '-'
    return {
        'heatindex': heatindex,
        'heatgrade': heatgrade
    }
