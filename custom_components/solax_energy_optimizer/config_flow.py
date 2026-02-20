"""Config flow for Solax Energy Optimizer integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_ELECTRICITY_PRICES_ENTITY,
    CONF_MAX_CHARGE_RATE,
    CONF_MAX_DISCHARGE_RATE,
    CONF_SOLCAST_ENTITY,
    CONF_SOLAX_INVERTER_ENTITY,
    DOMAIN,
)


class SolaxEnergyOptimizerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solax Energy Optimizer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if not self.hass.states.get(user_input[CONF_SOLAX_INVERTER_ENTITY]):
                errors[CONF_SOLAX_INVERTER_ENTITY] = "entity_not_found"
            if not self.hass.states.get(user_input[CONF_SOLCAST_ENTITY]):
                errors[CONF_SOLCAST_ENTITY] = "entity_not_found"
            if not self.hass.states.get(user_input[CONF_ELECTRICITY_PRICES_ENTITY]):
                errors[CONF_ELECTRICITY_PRICES_ENTITY] = "entity_not_found"

            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_SOLAX_INVERTER_ENTITY]}_optimizer"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Solax Energy Optimizer",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SOLAX_INVERTER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_SOLCAST_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_ELECTRICITY_PRICES_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_BATTERY_CAPACITY): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=100,
                        step=0.1,
                        unit_of_measurement="kWh",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(CONF_MAX_CHARGE_RATE): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0.1,
                        max=50,
                        step=0.1,
                        unit_of_measurement="kW",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(CONF_MAX_DISCHARGE_RATE): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0.1,
                        max=50,
                        step=0.1,
                        unit_of_measurement="kW",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
