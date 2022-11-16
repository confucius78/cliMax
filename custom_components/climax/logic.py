"""Climax zone base class holding settings and calculations"""
import homeassistant.util.dt as dt_util

from homeassistant.core import HomeAssistant
from homeassistant.components.climate import (
    SERVICE_SET_TEMPERATURE,
    SERVICE_SET_HVAC_MODE,
    ATTR_HVAC_MODE,
)
from homeassistant.components.recorder import get_instance, history
from homeassistant.helpers.event import (
    async_track_time_interval,
)
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
)
from homeassistant.components.climate import (
    HVACAction,
    HVACMode,
)

from .const import CLIMATE_DOMAIN


class ClimaxZone:
    """Climax zone with multiple HVAC devices"""

    def __init__(
        self,
        hass: HomeAssistant,
        zoneid,
        current_temp_sensors: list,
        outdoor_temp_sensor: str,
        climate_ac_entities: list,
    ):
        """Setup and defaults"""

        # internal variables general
        self._available = True
        self._id = zoneid
        self._name = zoneid
        self._hass = hass

        # Entities
        self._main_thermostat = None

        self._climate_devices = climate_ac_entities
        self._climate_mode = HVACMode.OFF
        self._climate_devices_action = HVACAction.OFF

        self._target_temperature = 20.0

        # internal variables for zone temp calculation
        self._source_entities_current_temperature = current_temp_sensors
        self._attr_current_temperature = None
        self._attr_precision = 0
        self._attr_sigma_level = 3
        self._attr_dropped_entities = list()

        # internal variables for zone temp control
        self._sample_time = dt_util.parse_duration("00:01:00")
        self._climate_error: float = 0.0
        self._climate_error_derivative: float = 0.0
        self._climate_error_integral: float = 0.0
        self._derivative_minutes = 3
        self._derivative_history = [None] * self._derivative_minutes
        self._p: float = 10
        self._i: float = 5
        self._d: float = 0.5
        self._pid: float = None
        self._ac_set_temp: float = None

        self._update_current_temperature(None)

        # internal variables for outdoor temp monmitoring
        self._source_entity_outdoor_temperature = outdoor_temp_sensor
        self._attr_1d_outdoor_temperature = None

        # async_track_state_change_event(
        #    self._hass,
        #    self._source_entities_current_temperature,
        #    self._async_sensor_changed,
        # )

        # async_track_state_change_event(
        #    self._hass,
        #    self._source_entity_outdoor_temperature,
        #    self._outside_temp_update_average,
        # )

        async_track_time_interval(
            self._hass,
            self._update_current_temperature,
            self._sample_time,
        )

        async_track_time_interval(
            self._hass,
            self._outside_temp_update_average,
            self._sample_time,
        )

        async_track_time_interval(
            self._hass,
            self._update_climate_state,
            self._sample_time,
        )

        async_track_time_interval(
            self._hass,
            self._update_climate_mode,
            self._sample_time,
        )

        async_track_time_interval(
            self._hass,
            self._control_climate_devices,
            self._sample_time,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return True
        except Exception as exception:
            raise UpdateFailed() from exception

    async def async_refresh(self):
        """Refresh data"""

    @property
    def last_update_success(self) -> bool:
        """Inform coordinator the last update was successful"""
        return True

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def name(self) -> str:
        """Return instance name"""
        return self._name

    @property
    def source_entities_current_temperature(self) -> list:
        """Return current temperature"""
        return self._source_entities_current_temperature

    @property
    def dropped_entities(self) -> list:
        """Return current temperature"""
        return self._attr_dropped_entities

    @property
    def precision(self) -> float:
        """Return precision"""
        return self._attr_precision

    @property
    def target_temperature(self) -> float:
        """Return precision"""
        if self._target_temperature is None:
            return STATE_UNKNOWN
        else:
            return self._target_temperature

    def set_target_temperature(self, target: float):
        """set target temperature"""
        self._target_temperature = target

    def set_main_thermostat(self, target):
        """set main climate device"""
        self._main_thermostat = target

    @property
    def outdoor_1d_temperature(self) -> float:
        """Return outdoor temperature"""
        if self._attr_1d_outdoor_temperature is None:
            return STATE_UNKNOWN
        else:
            return self._attr_1d_outdoor_temperature

    @property
    def climate_error(self) -> float:
        """Return climate error"""
        if self._climate_error is None:
            return STATE_UNKNOWN
        else:
            return self._climate_error

    @property
    def climate_error_derivative(self) -> float:
        """Return climate error derivative"""
        if self._climate_error_derivative is None:
            return STATE_UNKNOWN
        else:
            return self._climate_error_derivative

    @property
    def climate_error_integral(self) -> float:
        """Return climate error integral"""
        if self._climate_error_integral is None:
            return STATE_UNKNOWN
        else:
            return self._climate_error_integral

    @property
    def current_temperature(self) -> float:
        """Return current average temp"""
        if self._attr_current_temperature is None:
            return STATE_UNKNOWN
        else:
            return self._attr_current_temperature

    async def _async_update_current_temperature(
        self, event
    ):  # pylint: disable=unused-argument
        """Handle temperature changes."""

        self._update_current_temperature(None)

        _new_error = self._target_temperature - self._attr_current_temperature
        self.update_climate_error(_new_error)

        self.update_pid()

    def _update_current_temperature(self, event):  # pylint: disable=unused-argument
        _current_temp = 0.0
        _max_error_index = 0
        _errors = list()
        _squared_errors = list()
        _values = list()
        _temp_entities = self._source_entities_current_temperature.copy()
        _dropped_entities = list()

        while len(_temp_entities) > 1 and _max_error_index > -1:

            _errors.clear()
            _squared_errors.clear()
            _values.clear()

            for _idx, _entity in enumerate(_temp_entities):
                try:
                    _values.append(float(self._hass.states.get(_entity).state))
                except Exception:  # pylint: disable=broad-except
                    _temp_entities.pop(_idx)
                    _values.append(20.0)

            _current_temp = sum(_values) / len(_values)
            _max_error = 0
            _max_error_index = -1

            for _idx, _entity in enumerate(_temp_entities):
                _error = _values[_idx] - _current_temp
                _error_squared = _error**2
                if _error_squared > _max_error:
                    _max_error = _error_squared
                    _max_error_index = _idx

                _errors.append(_error)
                _squared_errors.append(_error_squared)

            _stdev = (sum(_squared_errors) / (len(_squared_errors) - 1.0)) ** 0.5

            if abs(_errors[_max_error_index]) > _stdev * self._attr_sigma_level / 2:
                _dropped_entities.append(_temp_entities[_max_error_index])
                _temp_entities.pop(_max_error_index)
            else:
                _max_error_index = -1

        self._attr_current_temperature = _current_temp
        self._attr_dropped_entities = _dropped_entities.copy()
        self._attr_precision = _stdev * self._attr_sigma_level / 2

        self.update_climate_error(
            self._target_temperature - self._attr_current_temperature
        )

        if self._main_thermostat is not None:
            self._main_thermostat.async_update_temp(_current_temp)

    def update_pid(self):
        """Update PID signal for thermostat settemp"""
        if self._p is not None and self._i is not None and self._d is not None:
            self._pid = (
                self._target_temperature
                + self._climate_error * self._p
                + self._climate_error_integral * self._i
                + self._climate_error_derivative * self._d
            )
        else:
            self._pid = self._target_temperature

        self._ac_set_temp = (
            round(
                2
                * min(
                    max(self._pid, self._target_temperature - 2.0),
                    self._target_temperature + 2.0,
                )
            )
            / 2
        )

    def update_climate_error(self, new_error):
        """Update filtered proportional, derivative and integral error"""
        # assumed last timestamp is exactly a minute ago
        last_error = self._climate_error
        time_constant = 8.0

        # proportional filtered error
        _a = 1 / time_constant
        _b = 1.0 - _a
        self._climate_error = last_error * _b + new_error * _a

        # Derivative, spans n minutes
        self._derivative_history.pop(0)
        self._derivative_history.append(self._climate_error)
        if self._derivative_history[0] is not None:
            # error by minute, times 60 minutes
            self._climate_error_derivative = (
                (self._climate_error - self._derivative_history[0])
                / self._derivative_minutes
            ) * 60
        else:
            self._climate_error_derivative = 0.0

        # integral base unit is hours
        if self._climate_error_integral is None:
            self._climate_error_integral = max(min(self._climate_error, 0.5), -0.5)
        else:
            self._climate_error_integral += (self._climate_error + last_error) / 2 / 60
            self._climate_error_integral = max(
                min(self._climate_error_integral, 0.5), -0.5
            )

        self.update_pid()

    async def _outside_temp_update_average(
        self, event
    ):  # pylint: disable=unused-argument
        """Update outdoor temperature average"""
        start = dt_util.as_utc(dt_util.now() - dt_util.parse_duration("24:00:00"))
        end = dt_util.as_utc(dt_util.now())
        entity_id = self._source_entity_outdoor_temperature
        history_list = await get_instance(self._hass).async_add_executor_job(
            history.state_changes_during_period,
            self._hass,
            start,
            end,
            str(entity_id),
        )

        value = 0
        elapsed = 0

        # Get the first state

        while history_list[entity_id][0].state == STATE_UNKNOWN:
            history_list[entity_id].pop(0)

        item = history_list[entity_id][0]
        first_time = item.last_changed.timestamp()
        first_state = float(item.state)

        # Get the other states
        for item in history_list.get(entity_id):
            current_time = item.last_changed.timestamp()
            current_state = None
            if item is not None:

                if item.state == STATE_UNKNOWN or item.state == STATE_UNAVAILABLE:
                    current_state = None
                else:
                    current_state = float(item.state)

            if first_state is not None:
                current_elapsed = current_time - first_time
                value += first_state * current_elapsed
                elapsed += current_elapsed

            first_state = current_state
            first_time = current_time

            # Time elapsed between last history state and now
        if current_state is not None:
            last_elapsed = end.timestamp() - current_time
            value += current_state * last_elapsed
            elapsed += last_elapsed

        if elapsed:
            value /= elapsed

        self._attr_1d_outdoor_temperature = round(value, 3)

    @property
    def climate_devices_action(self):
        """Return current HVAC action"""
        return self._climate_devices_action

    async def _update_climate_state(self, event):  # pylint: disable=unused-argument
        """Update current climate action of controlled devices"""

        # Set default state
        self._climate_devices_action = HVACAction.OFF

        # Loop controlled climate devices
        for _device in self._climate_devices:

            # Retrieve climate device state
            _climate_device = self._hass.states.get(_device)

            # If the device does not exist, state will be None
            if _climate_device is not None:
                # If the state is not OFF use this as the new state, otherwise loop to next
                _hvac_action = _climate_device.attributes["hvac_action"]
                if (
                    self._climate_devices_action == HVACAction.OFF
                    and _hvac_action != HVACAction.OFF
                ):
                    self._climate_devices_action = _climate_device.attributes[
                        "hvac_action"
                    ]

    async def _update_climate_mode(self, event):  # pylint: disable=unused-argument
        """Update current climate mode of controlled devices"""

        self._climate_mode = HVACMode.OFF

        if self._attr_1d_outdoor_temperature is not None:
            if (
                self._attr_1d_outdoor_temperature > 18.0
                and self._pid < self._target_temperature + 2.0
            ):
                self._climate_mode = HVACMode.COOL
            elif (
                self._attr_1d_outdoor_temperature < 15.0
                and self._pid > self._target_temperature - 2.0
            ):
                self._climate_mode = HVACMode.HEAT

    async def _control_climate_devices(self, event):  # pylint: disable=unused-argument
        """Update current climate action of controlled devices"""

        # Loop controlled climate devices
        if self._ac_set_temp is not None:
            for _device in self._climate_devices:

                if not self._hass.states.async_available(_device):
                    # Set climate device target temperature
                    service_data = {ATTR_ENTITY_ID: _device}
                    service_data[ATTR_HVAC_MODE] = self._climate_mode

                    await self._hass.services.async_call(
                        CLIMATE_DOMAIN, SERVICE_SET_HVAC_MODE, service_data
                    )

                    if (
                        self._pid < self._target_temperature + 2.0
                        and self._climate_mode == HVACMode.COOL
                    ) or (
                        self._pid > self._target_temperature - 2.0
                        and self._climate_mode == HVACMode.HEAT
                    ):
                        service_data[ATTR_TEMPERATURE] = self._ac_set_temp

                        await self._hass.services.async_call(
                            CLIMATE_DOMAIN, SERVICE_SET_TEMPERATURE, service_data
                        )
