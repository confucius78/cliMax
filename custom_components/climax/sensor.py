"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    _precision = None
    _dropped_entities = list()

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        if self._logic.current_temperature is not None:
            self._attr_native_value = self._logic.current_temperature
        else:
            self._attr_native_value = None
        if self._logic.precision is not None:
            self._precision = self._logic.precision
        else:
            self._precision = None
        self._dropped_entities = self._logic.dropped_entities

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
            "Precision": round(self._precision, 3),
            "Dropped entities": self._dropped_entities,
        }


class OutdoorAverageTempSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None
    _precision = None
    _dropped_entities = list()

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self._logic.outdoor_1d_temperature

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone outside 1d average temperature"
        self._logic = logic
        self._attr_native_value = self._logic.outdoor_1d_temperature
        self._attr_unique_id = entry_id + "_outdoor_1d_temp"


class TargetTempSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self._logic.target_temperature

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone target temperature"
        self._logic = logic
        self._attr_native_value = self._logic.target_temperature
        self._attr_unique_id = entry_id + "_zone_tgt_temp"


class ErrorTempSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self._logic.climate_error

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone error temperature"

        self._logic = logic
        self._attr_native_value = self._logic.climate_error
        self._attr_unique_id = entry_id + "_zone_error_temp"


class ErrorTempDerivativeSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = "°C/h"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self._logic.climate_error_derivative

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone error derivative temperature"
        self._logic = logic
        self._attr_native_value = self._logic.climate_error_derivative
        self._attr_unique_id = entry_id + "_zone_error_temp_derivative"


class ErrorTempIntegralSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = ""
    _attr_native_unit_of_measurement = "°Ch"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _logic = None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self._logic.climate_error_integral

    def __init__(self, logic: ClimaxZone, entry_id):
        """Initialize the sensor."""
        self._attr_name = logic.name + " zone error integral temperature"
        self._logic = logic
        self._attr_native_value = self._logic.climate_error_integral
        self._attr_unique_id = entry_id + "_zone_error_temp_integral"
