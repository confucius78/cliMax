"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .logic import ClimaxZone


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices
) -> None:
    """Set up Climax zone thermostat based on config_entry."""

    logic = hass.data[DOMAIN].get(entry.entry_id)
    async_add_devices(
        [
            ZoneTempSensor(logic, entry.entry_id),
            OutdoorAverageTempSensor(logic, entry.entry_id),
            TargetTempSensor(logic, entry.entry_id),
            ErrorTempSensor(logic, entry.entry_id),
            ErrorTempDerivativeSensor(logic, entry.entry_id),
            ErrorTempIntegralSensor(logic, entry.entry_id),
        ]
    )


class ZoneTempSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None
    _attr_native_value = STATE_UNAVAILABLE
    _attr_precision = STATE_UNAVAILABLE
    _attr_dropped_entities = STATE_UNAVAILABLE

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # check valid state, else provide unavailable
        if self._logic.current_temperature is not None:
            self._attr_native_value = self._logic.current_temperature
        else:
            self._attr_native_value = STATE_UNAVAILABLE

        # check valid state, else provide unavailable
        if self._logic.precision is not None:
            self._attr_precision = round(self._logic.precision)
        else:
            self._attr_precision = STATE_UNAVAILABLE

        # check valid state, else provide unavailable
        if self._logic.dropped_entities is not None:
            self._attr_dropped_entities = self._logic.dropped_entities
        else:
            self._attr_dropped_entities = STATE_UNAVAILABLE

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone temperature"
        self._attr_unique_id = entry_id + "_zone_temp"
        self._logic = logic

        # self._attr_state = logic.current_temperature

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes of the sensor."""

        return {
            "Precision": self._attr_precision,
            "Dropped entities": self._attr_dropped_entities,
        }


class OutdoorAverageTempSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None
    _attr_native_value = STATE_UNAVAILABLE

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # check valid state, else provide unavailable
        if self._logic.outdoor_1d_temperature is not None:
            self._attr_native_value = self._logic.outdoor_1d_temperature
        else:
            self._attr_native_value = STATE_UNAVAILABLE

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone outside 1d average temperature"
        self._logic = logic
        self._attr_unique_id = entry_id + "_outdoor_1d_temp"


class TargetTempSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None
    _attr_native_value = STATE_UNAVAILABLE

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # check valid state, else provide unavailable
        if self._logic.target_temperature is not None:
            self._attr_native_value = self._logic.target_temperature
        else:
            self._attr_native_value = STATE_UNAVAILABLE

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone target temperature"
        self._logic = logic
        self._attr_unique_id = entry_id + "_zone_tgt_temp"


class ErrorTempSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None
    _attr_native_value = STATE_UNAVAILABLE

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # check valid state, else provide unavailable
        if self._logic.climate_error is not None:
            self._attr_native_value = self._logic.climate_error
        else:
            self._attr_native_value = STATE_UNAVAILABLE

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone error temperature"
        self._logic = logic
        self._attr_unique_id = entry_id + "_zone_error_temp"


class ErrorTempDerivativeSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = "°C/h"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None
    _attr_native_value = STATE_UNAVAILABLE

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # check valid state, else provide unavailable
        if self._logic.climate_error_derivative is not None:
            self._attr_native_value = self._logic.climate_error_derivative
        else:
            self._attr_native_value = STATE_UNAVAILABLE

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone error derivative temperature"
        self._logic = logic
        self._attr_unique_id = entry_id + "_zone_error_temp_derivative"


class ErrorTempIntegralSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = "°Ch"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None
    _attr_native_value = STATE_UNAVAILABLE

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # check valid state, else provide unavailable
        if self._logic.climate_error_integral is not None:
            self._attr_native_value = self._logic.climate_error_integral
        else:
            self._attr_native_value = STATE_UNAVAILABLE

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone error integral temperature"
        self._logic = logic
        self._attr_unique_id = entry_id + "_zone_error_temp_integral"
