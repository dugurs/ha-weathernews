"""
Support for Weather.com weather service.
For more details about this platform, please refer to the documentation at
https://github.com/jaydeethree/Home-Assistant-weatherdotcom
"""

from . import WeatherUpdateCoordinator
from homeassistant.config_entries import ConfigEntry

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_SUNNY
)
from .const import (
    DOMAIN,

    TEMPUNIT,
    LENGTHUNIT,
    SPEEDUNIT,
    PRESSUREUNIT,

    FIELD_CLOUD_COVER,
    FIELD_DEW_POINT,
    FIELD_FEELS_LIKE,
    FIELD_HUMIDITY,
    FIELD_HUMIDITY_HOURLY,
    FIELD_ICONCODE,
    FIELD_ICONCODE_DAILY,
    FIELD_DAYORNIGHT,
    FIELD_PRECIPCHANCE,
    FIELD_PRESSURE,
    FIELD_PRECIPITATION,
    FIELD_TEMP,
    FIELD_TEMPERATUREMAX,
    FIELD_TEMPERATUREMIN,
    FIELD_UV_INDEX,
    FIELD_VALIDTIMEUTC,
    FIELD_VISIBILITY,
    FIELD_WINDDIR,
    FIELD_WINDDIRECTIONCARDINAL,
    FIELD_WINDGUST,
    FIELD_WINDSPEED,
    
    RESULTS_CURRENT,
    RESULTS_FORECAST_DAILY,
    RESULTS_FORECAST_HOURLY,
    ICON_CONDITION_MAP
)

import logging

from homeassistant.components.weather import (
    ATTR_FORECAST_CLOUD_COVERAGE,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_NATIVE_APPARENT_TEMP,
    ATTR_FORECAST_NATIVE_DEW_POINT,
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_UV_INDEX,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
    Forecast,
    DOMAIN as WEATHER_DOMAIN
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

ENTITY_ID_FORMAT = WEATHER_DOMAIN + ".{}"


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add weather entity."""
    coordinator: WeatherUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        WeatherNewsForecast(coordinator),
    ])


class WeatherNews(SingleCoordinatorWeatherEntity):

    @property
    def name(self) -> str:
        return self.coordinator._location_name
        
    @property
    def native_temperature(self) -> float:
        """
        Return the platform temperature in native units
        (i.e. not converted).
        """
        return self.coordinator.get_current(FIELD_TEMP)

    @property
    def native_temperature_unit(self) -> str:
        """Return the native unit of measurement for temperature."""
        return self.coordinator.units_of_measurement[TEMPUNIT]

    @property
    def native_pressure(self) -> float:
        """Return the pressure in native units."""
        return self.coordinator.get_current(FIELD_PRESSURE)

    @property
    def native_pressure_unit(self) -> str:
        """Return the native unit of measurement for pressure."""
        return self.coordinator.units_of_measurement[PRESSUREUNIT]

    @property
    def humidity(self) -> float:
        """Return the relative humidity in native units."""
        return self.coordinator.get_current(FIELD_HUMIDITY)

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed in native units."""
        return self.coordinator.get_current(FIELD_WINDSPEED)

    @property
    def native_wind_speed_unit(self) -> str:
        """Return the native unit of measurement for wind speed."""
        return self.coordinator.units_of_measurement[SPEEDUNIT]

    @property
    def wind_bearing(self) -> str:
        """Return the wind bearing."""
        return self.coordinator.get_current(FIELD_WINDDIR)

    @property
    def native_visibility(self) -> float:
        """Return the visibility in native units."""
        return self.coordinator.get_current(FIELD_VISIBILITY)

    @property
    def native_visibility_unit(self) -> str:
        """Return the native unit of measurement for visibility."""
        return self.coordinator.visibility_unit

    @property
    def native_precipitation_unit(self) -> str:
        """
        Return the native unit of measurement for accumulated precipitation.
        """
        return self.coordinator.units_of_measurement[LENGTHUNIT]

    @property
    def condition(self) -> str:
        """Return the current condition."""
        
        iconcode = self.coordinator.get_current(FIELD_ICONCODE)
        if self.coordinator.get_current(FIELD_DAYORNIGHT) == 'N' and iconcode in ICON_CONDITION_MAP[ATTR_CONDITION_SUNNY]:
            iconcode = iconcode + 1000

        return self.coordinator._iconcode_to_condition(iconcode)

    @property
    def native_apparent_temperature(self) -> float:
        """Return the 'feels like' temperature."""
        return self.coordinator.get_current(FIELD_FEELS_LIKE)

    @property
    def native_dew_point(self) -> float:
        """Return the dew point."""
        return self.coordinator.get_current(FIELD_DEW_POINT)

    # @property
    # def native_wind_gust_speed(self) -> float:
    #     """Return the wind gust speed."""
    #     return self.coordinator.get_current(FIELD_WINDGUST)

    @property
    def uv_index(self) -> float:
        """Return the UV index."""
        return self.coordinator.get_current(FIELD_UV_INDEX)

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.coordinator._location_name)},
            "name": self.coordinator._location_name,
            "sw_version": 1,
            "manufacturer": 'WeatherNews',
            "model": 'WeatherNews',
            "configuration_url": self.coordinator._build_url('https://www.kr-weathernews.com/mv4/html/today.html?loc={apiKey}')
        }

class WeatherNewsForecast(WeatherNews):

    def __init__(
            self,
            coordinator: WeatherUpdateCoordinator
    ):
        super().__init__(coordinator)
        """Initialize the sensor."""
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, f"wn_{coordinator.location_name}", hass=coordinator.hass
        )
        self._attr_unique_id = f"wn_{coordinator.location_name},{WEATHER_DOMAIN}".lower()

    @property
    def supported_features(self) -> WeatherEntityFeature:
        return (WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY)

    async def async_forecast_daily(self) -> list[Forecast] | None:
        return self.forecast_daily

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        return self.forecast_hourly

    @property
    def forecast_daily(self) -> list[Forecast]:
        """Return the daily forecast in native units."""

        forecast = []
        for data in self.coordinator.data[RESULTS_FORECAST_DAILY]:
            forecast.append(Forecast({
                # ATTR_FORECAST_CLOUD_COVERAGE:
                #     self.coordinator.get_forecast_daily(FIELD_CLOUD_COVER, data),
                ATTR_FORECAST_CONDITION:
                    self.coordinator._iconcode_to_condition(
                        self.coordinator.get_forecast(FIELD_ICONCODE_DAILY, data)
                    ),
                ATTR_FORECAST_HUMIDITY:
                    self.coordinator.get_forecast(FIELD_HUMIDITY, data),
                ATTR_FORECAST_PRECIPITATION:
                    self.coordinator.get_forecast(FIELD_PRECIPITATION, data),
                ATTR_FORECAST_PRECIPITATION_PROBABILITY:
                    self.coordinator.get_forecast(FIELD_PRECIPCHANCE, data),

                ATTR_FORECAST_TEMP:
                    self.coordinator.get_forecast(FIELD_TEMPERATUREMAX, data),
                ATTR_FORECAST_TEMP_LOW:
                    self.coordinator.get_forecast(FIELD_TEMPERATUREMIN, data),

                ATTR_FORECAST_TIME:
                    self.coordinator._format_timestamp(
                        self.coordinator.get_forecast(FIELD_VALIDTIMEUTC, data)),
                ATTR_FORECAST_UV_INDEX:
                    self.coordinator.get_forecast(FIELD_UV_INDEX, data),
                ATTR_FORECAST_WIND_BEARING:
                    self.coordinator.get_forecast(FIELD_WINDDIRECTIONCARDINAL, data),
                ATTR_FORECAST_WIND_SPEED:
                    self.coordinator.get_forecast(FIELD_WINDSPEED, data)
            }))
        return forecast
    
    @property
    def forecast_hourly(self) -> list[Forecast]:
        """Return the hourly forecast in native units."""

        forecast = []
        for data in self.coordinator.data[RESULTS_FORECAST_HOURLY]:
            
            iconcode = self.coordinator.get_forecast(FIELD_ICONCODE, data)
            if self.coordinator.get_forecast(FIELD_DAYORNIGHT, data) == 'N' and iconcode in ICON_CONDITION_MAP[ATTR_CONDITION_SUNNY]:
                iconcode = iconcode + 1000

            forecast.append(Forecast({
                # ATTR_FORECAST_CLOUD_COVERAGE:
                #     self.coordinator.get_forecast_hourly(FIELD_CLOUD_COVER, data),
                ATTR_FORECAST_CONDITION:
                    self.coordinator._iconcode_to_condition(
                        iconcode
                    ),
                ATTR_FORECAST_HUMIDITY:
                    self.coordinator.get_forecast(FIELD_HUMIDITY_HOURLY, data),
                ATTR_FORECAST_NATIVE_APPARENT_TEMP:
                    self.coordinator.get_forecast(FIELD_FEELS_LIKE, data),
                ATTR_FORECAST_NATIVE_DEW_POINT:
                    self.coordinator.get_forecast(FIELD_DEW_POINT, data),
                # ATTR_FORECAST_NATIVE_WIND_GUST_SPEED:
                #     self.coordinator.get_forecast(FIELD_WINDGUST, data),
                ATTR_FORECAST_PRECIPITATION:
                    self.coordinator.get_forecast(FIELD_PRECIPITATION, data),
                ATTR_FORECAST_PRECIPITATION_PROBABILITY:
                    self.coordinator.get_forecast(FIELD_PRECIPCHANCE, data),
                ATTR_FORECAST_TEMP:
                    self.coordinator.get_forecast(FIELD_TEMP, data),
                ATTR_FORECAST_TIME:
                    self.coordinator._format_timestamp(
                        self.coordinator.get_forecast(FIELD_VALIDTIMEUTC, data)),
                ATTR_FORECAST_UV_INDEX:
                    self.coordinator.get_forecast(FIELD_UV_INDEX, data),
                ATTR_FORECAST_WIND_BEARING:
                    self.coordinator.get_forecast(FIELD_WINDDIRECTIONCARDINAL, data),
                ATTR_FORECAST_WIND_SPEED:
                    self.coordinator.get_forecast(FIELD_WINDSPEED, data)
            }))
        return forecast
