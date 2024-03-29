from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any, cast

from .const import (
    FIELD_VALIDTIMELOCAL,
    FIELD_DESCRIPTION,
    FIELD_DEW_POINT,
    FIELD_FEELS_LIKE,
    FIELD_HUMIDITY,
    FIELD_PRESSURE,
    FIELD_TEMP,
    FIELD_UV_INDEX,
    FIELD_WINDDIR,
    FIELD_WINDDIRECTIONCARDINAL,
    FIELD_WINDGUST,
    FIELD_WINDSPEED,
    ICON_THERMOMETER,
    ICON_UMBRELLA,
    ICON_WIND,
    RESULTS_CURRENT
)
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UV_INDEX, DEGREE, UnitOfLength, UnitOfTemperature, \
    UnitOfVolumetricFlux, UnitOfPressure, UnitOfSpeed, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.helpers.typing import StateType


@dataclass
class WeatherRequiredKeysMixin:
    """Mixin for required keys."""
    value_fn: Callable[[dict[str, Any], str], StateType]


@dataclass
class WeatherSensorEntityDescription(
    SensorEntityDescription, WeatherRequiredKeysMixin
):
    # attr_fn: Callable[[dict[str, Any]], dict[str, StateType]] = lambda _: {}
    unit_fn: Callable[[bool], str | None] = lambda _: None
    attr_key: Callable[[list], Any | None] = lambda _: None 
    """Describes Weather.com Sensor entity."""


current_condition_sensor_descriptions = [
    WeatherSensorEntityDescription(
        key=FIELD_VALIDTIMELOCAL,
        name="Local Observation Time",
        icon="mdi:clock",
        value_fn=lambda data, _: cast(str, data),
    ),
    # WeatherSensorEntityDescription(
    #     key=FIELD_DESCRIPTION,
    #     name="Weather Description",
    #     icon="mdi:note-text",
    #     value_fn=lambda data, _: cast(str, data),
    # ),
    WeatherSensorEntityDescription(
        key=FIELD_HUMIDITY,
        name="Relative Humidity",
        icon="mdi:water-percent",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_fn=lambda _: PERCENTAGE,
        value_fn=lambda data, _: cast(int, data) or 0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_UV_INDEX,
        name="UV Index",
        icon="mdi:sunglasses",
        state_class=SensorStateClass.MEASUREMENT,
        unit_fn=lambda _: UV_INDEX,
        value_fn=lambda data, _: cast(int, data) or 0,
    ),
    # WeatherSensorEntityDescription(
    #     key=FIELD_WINDDIR,
    #     name="Wind Direction - Degrees",
    #     icon=ICON_WIND,
    #     state_class=SensorStateClass.MEASUREMENT,
    #     unit_fn=lambda _: DEGREE,
    #     value_fn=lambda data, _: cast(int, data) or 0,
    # ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDDIRECTIONCARDINAL,
        name="Wind Direction - Cardinal",
        icon="mdi:windsock",
        unit_fn=lambda _: None,
        value_fn=lambda data, _: cast(str, data) or "",
    ),
    WeatherSensorEntityDescription(
        key=FIELD_DEW_POINT,
        name="Dewpoint",
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS if metric else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data),
    ),
    WeatherSensorEntityDescription(
        key=FIELD_FEELS_LIKE,
        name="Temperature - Feels Like",
        icon=ICON_THERMOMETER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS if metric else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data),
    ),
    WeatherSensorEntityDescription(
        key=FIELD_TEMP,
        name="Temperature",
        icon=ICON_THERMOMETER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS if metric else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data),
    ),
    WeatherSensorEntityDescription(
        key="heatindex",
        name="Heat Index",
        icon=ICON_THERMOMETER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS if metric else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data),
        attr_key=['heatindexAttr'],
    ),
    # WeatherSensorEntityDescription(
    #     key="temperatureWindChill",
    #     name="Wind Chill",
    #     icon=ICON_THERMOMETER,
    #     state_class=SensorStateClass.MEASUREMENT,
    #     device_class=SensorDeviceClass.TEMPERATURE,
    #     unit_fn=lambda metric: UnitOfTemperature.CELSIUS if metric else UnitOfTemperature.FAHRENHEIT,
    #     value_fn=lambda data, _: cast(float, data),
    # ),
    # WeatherSensorEntityDescription(
    #     key="precip1Hour",
    #     name="Precipitation - Last hour",
    #     icon=ICON_UMBRELLA,
    #     state_class=SensorStateClass.MEASUREMENT,
    #     device_class=SensorDeviceClass.PRECIPITATION,
    #     unit_fn=lambda metric: UnitOfLength.MILLIMETERS if metric else UnitOfLength.INCHES,
    #     value_fn=lambda data, _: cast(float, data) or 0,
    # ),
    WeatherSensorEntityDescription(
        key="pop",
        name="Precipitation Probability",
        icon=ICON_UMBRELLA,
        state_class=SensorStateClass.MEASUREMENT,
        unit_fn=lambda _: PERCENTAGE,
        value_fn=lambda data, _: cast(int, data) or None,
        attr_key=['prec'],
    ),
    # WeatherSensorEntityDescription(
    #     key="precip6Hour",
    #     name="Precipitation - Last 6 hours",
    #     icon=ICON_UMBRELLA,
    #     state_class=SensorStateClass.MEASUREMENT,
    #     device_class=SensorDeviceClass.PRECIPITATION,
    #     unit_fn=lambda metric: UnitOfLength.MILLIMETERS if metric else UnitOfLength.INCHES,
    #     value_fn=lambda data, _: cast(int, data) or None,
    #     attr_key=['precip6HourAttr'],
    # ),
    # WeatherSensorEntityDescription(
    #     key="precip12Hour",
    #     name="Precipitation - Last 12 hours",
    #     icon=ICON_UMBRELLA,
    #     state_class=SensorStateClass.MEASUREMENT,
    #     device_class=SensorDeviceClass.PRECIPITATION,
    #     unit_fn=lambda metric: UnitOfLength.MILLIMETERS if metric else UnitOfLength.INCHES,
    #     value_fn=lambda data, _: cast(int, data) or None,
    #     attr_key=['precip12HourAttr'],
    # ),
    WeatherSensorEntityDescription(
        key=FIELD_PRESSURE,
        name="Pressure",
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        unit_fn=lambda metric: UnitOfPressure.MBAR if metric else UnitOfPressure.INHG,
        value_fn=lambda data, _: cast(float, data),
    ),
    # WeatherSensorEntityDescription(
    #     key=FIELD_WINDGUST,
    #     name="Wind Gust",
    #     icon=ICON_WIND,
    #     state_class=SensorStateClass.MEASUREMENT,
    #     device_class=SensorDeviceClass.WIND_SPEED,
    #     unit_fn=lambda metric: UnitOfSpeed.KILOMETERS_PER_HOUR if metric else UnitOfSpeed.MILES_PER_HOUR,
    #     value_fn=lambda data, _: cast(float, data),
    # ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDSPEED,
        name="Wind Speed",
        icon=ICON_WIND,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.WIND_SPEED,
        unit_fn=lambda metric: UnitOfSpeed.KILOMETERS_PER_HOUR if metric else UnitOfSpeed.MILES_PER_HOUR,
        value_fn=lambda data, _: cast(float, data),
    ),
    # WeatherSensorEntityDescription(
    #     key="cloudCeiling",
    #     name="Cloud Ceiling",
    #     icon="mdi:clouds",
    #     state_class=SensorStateClass.MEASUREMENT,
    #     device_class=SensorDeviceClass.DISTANCE,
    #     unit_fn=lambda metric: UnitOfLength.METERS if metric else UnitOfLength.FEET,
    #     value_fn=lambda data, _: cast(int, data) or 0,
    # ),
    # WeatherSensorEntityDescription(
    #     key="pressureTendencyTrend",
    #     name="Pressure Tendency Trend",
    #     icon="mdi:gauge",
    #     value_fn=lambda data, _: cast(str, data),
    # ),
    # WeatherSensorEntityDescription(
    #     key="cloudCoverPhrase",
    #     name="Cloud Cover Phrase",
    #     icon="mdi:clouds",
    #     value_fn=lambda data, _: cast(str, data),
    # ),
    WeatherSensorEntityDescription(
        key="sunrise",
        name="Sunrise",
        icon="mdi:weather-sunset-up",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="sunset",
        name="Sunset",
        icon="mdi:weather-sunset",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="pm10",
        name="PM10",
        icon="mdi:blur",
        unit_fn=lambda metric: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        value_fn=lambda data, _: cast(float, data),
        attr_key=['pm10grade'],
    ),
    WeatherSensorEntityDescription(
        key="pm25",
        name="PM2.5",
        icon="mdi:blur-linear",
        unit_fn=lambda metric: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        value_fn=lambda data, _: cast(float, data),
        attr_key=['pm25grade'],
    ),
    WeatherSensorEntityDescription(
        key="pm10grade",
        name="PM10 grade",
        icon="mdi:blur",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="pm25grade",
        name="PM2.5 grade",
        icon="mdi:blur-linear",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="cur_cmt",
        name="current condition",
        icon="mdi:cloud-question-outline",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['day_cmt','night_cmt','dayShortCmt','nextDayShortCmt'],
    ),
    WeatherSensorEntityDescription(
        key="day_cmt",
        name="day condition",
        icon="mdi:weather-sunny",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="night_cmt",
        name="night condition",
        icon="mdi:weather-night",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="dayShortCmt",
        name="day Short Comment",
        icon="mdi:comment-text-outline",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="nextDayShortCmt",
        name="next Day Short Comment",
        icon="mdi:comment-text-outline",
        value_fn=lambda data, _: cast(str, data),
    ),
    WeatherSensorEntityDescription(
        key="tempdiffCmt",
        name="Temp diff Comment",
        icon="mdi:thermometer-lines",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['tempdiff'],
    ),
    WeatherSensorEntityDescription(
        key="weatherBriping",
        name="Weather briefing",
        icon="mdi:comment-text-outline",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['weatherBripingAttr'],
    ),
    WeatherSensorEntityDescription(
        key="khai",
        name="CAI",
        icon="mdi:tailwind",
        unit_fn=lambda metric: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        value_fn=lambda data, _: cast(float, data),
        # attr_fn=lambda _: {}
        attr_key=['pm'],
    ),
    WeatherSensorEntityDescription(
        key="precipHourToday",
        name="precip Hour Today",
        icon="mdi:weather-rainy",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['precipHourTodayAttr'],
    ),
    WeatherSensorEntityDescription(
        key="precipHourTomarrow",
        name="precip Hour Today Tomarrow",
        icon="mdi:weather-rainy",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['precipHourTomarrowAttr'],
    ),
    WeatherSensorEntityDescription(
        key="precipHour3",
        name="precip 3Hour",
        icon="mdi:weather-rainy",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['precipHour3Attr'],
    ),
    WeatherSensorEntityDescription(
        key="precipHour6",
        name="precip 6Hour",
        icon="mdi:weather-rainy",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['precipHour6Attr'],
    ),
    WeatherSensorEntityDescription(
        key="precipHour9",
        name="precip 9Hour",
        icon="mdi:weather-rainy",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['precipHour9Attr'],
    ),
    WeatherSensorEntityDescription(
        key="precipHour12",
        name="precip 12Hour",
        icon="mdi:weather-rainy",
        value_fn=lambda data, _: cast(str, data),
        attr_key=['precipHour12Attr'],
    ),
]
