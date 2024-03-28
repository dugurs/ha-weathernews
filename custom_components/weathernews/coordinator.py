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
    FIELD_DAYPART,
    FIELD_HUMIDITY,
    FIELD_TEMPERATUREMAX,
    FIELD_TEMPERATUREMIN,
    FIELD_VALIDTIMEUTC,
    FIELD_VALIDTIMELOCAL,
    FIELD_WINDDIR,
    FIELD_WINDDIRECTIONCARDINAL,
    FIELD_WINDGUST,
    FIELD_WINDSPEED,
    FIELD_DAYORNIGHT,
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
                # https://www.kr-weathernews.com/mv3/if/pm_v4.fcgi?loc=1147010300
                url = self._build_url(f"https://www.kr-weathernews.com/mv3/if/main2_v2.fcgi?lat={lat}&lon={lon}")
                response = await self._session.get(url, headers=headers)
                result_data3 = await response.json(content_type=None)

                if result_data3 is None:
                    raise ValueError('NO RESULT3')
                self._check_errors(url, result_data3)
                tempdiff = int(result_data3['current']['tempdiff'])
                if tempdiff == 0:
                    tempdiffCmt = "어제와 같아요."
                else:
                    tempdiffCmt = "어제보다 {}도 {}아요.".format(abs(tempdiff), "높" if tempdiff > 0 else "낮")


            # 오늘비시작시간 - 비안옴
            # 지금 시간과 첫번째 시간이 같지 않은 경우가 있어 처리
            # if int(result_data['hourly'][0]['hour']) == 0 and int(result_data['hourly'][0]['hour']) != int(result_data3['current']['time'][:2]):
            #     remainhour = 1 
            # elif int(result_data['hourly'][0]['hour']) != int(result_data3['current']['time'][:2]):
            #     remainhour = 23 - int(result_data['hourly'][0]['hour']) - 1
            # else:
            remainhour = 23 - int(result_data['hourly'][0]['hour']) 
                
            precipHourTodayAttr = self._get_precip_hour(result_data['hourly'], remainhour)
            if precipHourTodayAttr['hour'] != None:
                precipHourTodayAttr['cmt'] = f"{precipHourTodayAttr['hour']}시"

            # 오늘내일비시작시간 - 내일 05시
            precipHourTomarrowAttr = self._get_precip_hour(result_data['hourly'], remainhour+24)
            if precipHourTomarrowAttr['hour'] != None:
                precipHourTomarrowAttr['cmt'] = "{} {}시".format("" if result_data['daily'][0]['day']==precipHourTomarrowAttr['day'] else "내일", precipHourTomarrowAttr['hour'])

            # 통합대기 지수
            khai = int(result_data3['aq']['khai'])
            if khai < 50:
                khaigrade = '좋음'
            elif khai < 100:
                khaigrade = '보통'
            elif khai < 250:
                khaigrade = '나쁨'
            elif khai < 500:
                khaigrade = '매우나쁨'
            else:
                khaigrade = ''

            # 통합대기 속성추가
            result_data3['aq'].update({
                'pm10grade': result_data2[0]['air']['pm10']['description'],
                'pm25grade': result_data2[0]['air']['pm25']['description'],
                'khaigrade': khaigrade
            })
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
                'pm10grade': result_data2[0]['air']['pm10']['description'],
                'pm25grade': result_data2[0]['air']['pm25']['description'],
                'khai': result_data3['aq']['khai'],
                'pm': result_data3['aq'],
                'tempdiff': tempdiff,
                'tempdiffCmt': tempdiffCmt,
                'precipHourToday': precipHourTodayAttr['cmt'],
                'precipHourTodayAttr': precipHourTodayAttr,
                'precipHourTomarrow': precipHourTomarrowAttr['cmt'],
                'precipHourTomarrowAttr': precipHourTomarrowAttr,

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

    def _get_precip_hour(self, hours: dict, limit: int):
        for hour_data in hours[:limit]:
            if float(hour_data["prec"]) > 0:
                return hour_data
        return {'cmt': '비안옴', 'hour': None, 'prec': 0}

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
        _LOGGER.warning(f'Unmapped iconCode from TWC Api. (44 is Not Available (N/A)) "{icon_code}". ')
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


class InvalidApiKey(HomeAssistantError):
    """Error to indicate there is an invalid api key."""
