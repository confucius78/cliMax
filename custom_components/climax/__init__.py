"""The Climax integration."""
from __future__ import annotations
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, STARTUP_MESSAGE
from .logic import ClimaxZone

PLATFORMS = [Platform.CLIMATE, Platform.SENSOR]
entity_list_current_temperature = [
    "sensor.weather_station_temperature",
    "sensor.living_room_back_temperature_2",
    "sensor.living_room_l_temperature",
    "sensor.living_room_r_temperature",
    "sensor.living_room_window_back_temperature",
    "sensor.kitchen_temp_mid",
    "sensor.kitchen_temp_back",
    "sensor.kitchen_temp_front_temperature",
]
outdoor_temperature_sensor = "sensor.average_outside_temperature_5m_sampled"
ac_climate_entities = [
    "climate.upstairs",
    "climate.ac_living_room",
    "climate.ac_kitchen",
]

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Create climax zone component from UI"""

    # Log startup message and set defaults
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    conf = entry.data

    this_climax_zone = ClimaxZone(
        hass,
        conf["zone"],
        entity_list_current_temperature,
        outdoor_temperature_sensor,
        ac_climate_entities,
    )

    hass.data.setdefault(DOMAIN, {}).update({entry.entry_id: this_climax_zone})

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info(LOADED_MESSAGE)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
