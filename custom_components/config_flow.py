"""Config flow for the Climax platform."""
import logging
import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize the Climax config flow."""
        self.zone_name = None

    @property
    def schema(self):
        """Return current schema"""
        return vol.Schema(
            {
                vol.Required("Zone name", default=self.zone_name): str,
            }
        )

    async def _create_entry(self, zone):
        """Register new entry."""
        if not self.unique_id:
            await self.async_set_unique_id(zone)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=zone,
            data={
                "zone": zone,
            },
        )

    async def _create_device(self, zone):
        """Create device."""

        return await self._create_entry(zone)

    async def async_step_user(self, user_input=None):
        """User initiated config flow."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=self.schema)

        return await self._create_device(user_input["Zone name"])
