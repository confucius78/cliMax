"""Add thermostat"""
import math
import logging

from .logic import ClimaxZone

from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.climate import (
    HVACAction,
    HVACMode,
    ClimateEntity,
    ClimateEntityFeature,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices) -> None:
    """Set up Climax zone thermostat based on config_entry."""

    logic = hass.data[DOMAIN].get(entry.entry_id)

    async_add_devices([ClimaxThermostat(logic, entry.entry_id)])


class ClimaxThermostat(ClimateEntity):
    """Climax thermostat"""

    def __init__(self, logic: ClimaxZone, entry_id) -> None:
        self._attr_available = "on"
        self._attr_current_temperature = 20.0
        self._attr_target_temperature_entity = "logic.name"
        self._attr_hvac_action = HVACAction.OFF
        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_name = logic.name
        self._logic = logic
        self._attr_target_temperature = self._logic.target_temperature
        self._attr_unique_id = entry_id + "thermostat"

        self._logic._async_set_thermostat(self)

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""

        await super().async_added_to_hass()

        # Add listener
        # self.async_on_remove(
        #    async_track_state_change_event(
        #        self.hass,
        #        [self._attr_target_temperature_entity],
        #        self._async_sensor_changed,
        #    )
        # )

    async def _async_sensor_changed(self, event):
        """Handle temperature changes."""
        new_state = event.data.get("new_state")
        if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return

        self._attr_current_temperature = float(new_state.state)
        self._async_update_temp(new_state)
        self.async_write_ha_state()

    @callback
    def _async_update_temp(self, state):
        """Update thermostat with latest state from sensor."""
        try:
            cur_temp = float(state.state)
            if math.isnan(cur_temp) or math.isinf(cur_temp):
                raise ValueError(f"Sensor has illegal state {state.state}")
            self._attr_current_temperature = cur_temp
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    @property
    def name(self):
        return self._attr_name

    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def hvac_modes(self):
        return [HVACMode.AUTO, HVACMode.COOL, HVACMode.HEAT, HVACMode.OFF]

    @property
    def current_temperature(self) -> float:
        if self._logic.current_temperature is None:
            return 20
        else:
            return self._logic.current_temperature

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def target_temperature(self) -> float:
        self._logic.set_target_temperature(self._attr_target_temperature)
        return self._attr_target_temperature

    @property
    def hvac_action(self):

        #        proposed_action = HVACAction.OFF
        #            if (
        #                self.hvac_mode == HVACMode.COOL
        #                and self.current_temperature > self.target_temperature
        #            ):
        #                proposed_action = HVACAction.COOLING
        #            elif (
        #                self.hvac_mode == HVACMode.HEAT
        #                and self.current_temperature < self.target_temperature
        #            ):
        #                proposed_action = HVACAction.HEATING
        #            elif self.hvac_mode == HVACMode.AUTO:
        #                if self.current_temperature < self.target_temperature:
        #                    proposed_action = HVACAction.HEATING
        #                elif self.current_temperature > self.target_temperature:
        #                    proposed_action = HVACAction.COOLING
        #                else:
        #                    proposed_action = HVACAction.OFF
        #
        #            return proposed_action
        #

        return self._logic.climate_devices_action

    @property
    def hvac_mode(self):

        return self._attr_hvac_mode

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        self._attr_hvac_mode = hvac_mode

    def set_temperature(self, **kwargs):
        """Set new target temperature."""

        self._attr_target_temperature = kwargs.get("temperature")

    def update(self):
        """TEST"""
