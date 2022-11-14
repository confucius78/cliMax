"""The Climax integration."""
from __future__ import annotations

from .logic import ClimaxZone

from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Create climax zone component."""
    conf = entry.data
    # For backwards compat, set unique ID
    if entry.unique_id is None or ".local" in entry.unique_id:
        hass.config_entries.async_update_entry(entry, unique_id="climax123")

    this_climax_zone = ClimaxZone(
        hass,
        conf["zone"],
        entity_list_current_temperature,
        outdoor_temperature_sensor,
        ac_climate_entities,
    )

    hass.data.setdefault(DOMAIN, {}).update({entry.entry_id: this_climax_zone})

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
