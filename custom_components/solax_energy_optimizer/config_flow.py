"""Config flow for Solar Energy Optimizer integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_FORECAST_ATTRIBUTE,
    CONF_FORECAST_ENTITY,
    CONF_FORECAST_PERIOD_START_FIELD,
    CONF_FORECAST_PV_ESTIMATE_FIELD,
    CONF_FORECAST_TODAY_FROM_STATE,
    CONF_FORECAST_TYPE,
    CONF_INVERTER_ENTITY,
    CONF_INVERTER_SOC_ATTRIBUTE,
    CONF_INVERTER_TYPE,
    CONF_MAX_CHARGE_RATE,
    CONF_MAX_DISCHARGE_RATE,
    CONF_PRICES_ATTRIBUTE,
    CONF_PRICES_ENTITY,
    CONF_PRICES_PERIOD_START_FIELD,
    CONF_PRICES_PRICE_FIELD,
    CONF_PRICES_TYPE,
    DOMAIN,
    FORECAST_TYPE_GENERIC,
    FORECAST_TYPE_SOLCAST,
    INVERTER_TYPE_GENERIC_ATTRIBUTE,
    INVERTER_TYPE_GENERIC_STATE,
    INVERTER_TYPE_SOLAX_MODBUS,
    PRICES_TYPE_AMBER,
    PRICES_TYPE_AWATTAR,
    PRICES_TYPE_FRANK_ENERGIE,
    PRICES_TYPE_GENERIC,
    PRICES_TYPE_NORDPOOL,
    PRICES_TYPE_TIBBER,
)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entries from older versions."""
    if entry.version == 1:
        old_data = dict(entry.data)
        new_data = {
            CONF_INVERTER_ENTITY: old_data.get("solax_inverter_entity", ""),
            CONF_FORECAST_ENTITY: old_data.get("solcast_entity", ""),
            CONF_PRICES_ENTITY: old_data.get("frank_energie_entity", ""),
            CONF_INVERTER_TYPE: INVERTER_TYPE_SOLAX_MODBUS,
            CONF_FORECAST_TYPE: FORECAST_TYPE_SOLCAST,
            CONF_PRICES_TYPE: PRICES_TYPE_FRANK_ENERGIE,
            CONF_BATTERY_CAPACITY: old_data.get("battery_capacity", 10.0),
            CONF_MAX_CHARGE_RATE: old_data.get("max_charge_rate", 3.6),
            CONF_MAX_DISCHARGE_RATE: old_data.get("max_discharge_rate", 3.6),
        }
        hass.config_entries.async_update_entry(entry, data=new_data, version=2)

    return True


class EnergyOptimizerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar Energy Optimizer."""

    VERSION = 2

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: Inverter / Battery SOC source."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_id = user_input[CONF_INVERTER_ENTITY]
            if not self.hass.states.get(entity_id):
                errors[CONF_INVERTER_ENTITY] = "entity_not_found"
            else:
                self._data.update(user_input)
                return await self.async_step_forecast()

        inverter_type = (user_input or {}).get(CONF_INVERTER_TYPE, INVERTER_TYPE_SOLAX_MODBUS)
        show_attribute = inverter_type == INVERTER_TYPE_GENERIC_ATTRIBUTE

        schema_fields: dict = {
            vol.Required(CONF_INVERTER_TYPE, default=INVERTER_TYPE_SOLAX_MODBUS): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": INVERTER_TYPE_SOLAX_MODBUS, "label": "Solax Modbus"},
                        {"value": INVERTER_TYPE_GENERIC_STATE, "label": "Generic (SOC from entity state)"},
                        {"value": INVERTER_TYPE_GENERIC_ATTRIBUTE, "label": "Generic (SOC from entity attribute)"},
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Required(CONF_INVERTER_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
        }
        if show_attribute:
            schema_fields[vol.Optional(CONF_INVERTER_SOC_ATTRIBUTE, default="")] = selector.TextSelector()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema_fields),
            errors=errors,
        )

    async def async_step_forecast(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: Solar forecast source."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_id = user_input[CONF_FORECAST_ENTITY]
            if not self.hass.states.get(entity_id):
                errors[CONF_FORECAST_ENTITY] = "entity_not_found"
            else:
                self._data.update(user_input)
                return await self.async_step_prices()

        forecast_type = (user_input or {}).get(CONF_FORECAST_TYPE, FORECAST_TYPE_SOLCAST)
        show_field_mapping = forecast_type == FORECAST_TYPE_GENERIC

        schema_fields: dict = {
            vol.Required(CONF_FORECAST_TYPE, default=FORECAST_TYPE_SOLCAST): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": FORECAST_TYPE_SOLCAST, "label": "Solcast Solar"},
                        {"value": FORECAST_TYPE_GENERIC, "label": "Generic (configurable field mapping)"},
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Required(CONF_FORECAST_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
        }
        if show_field_mapping:
            schema_fields[vol.Optional(CONF_FORECAST_ATTRIBUTE, default="forecasts")] = selector.TextSelector()
            schema_fields[vol.Optional(CONF_FORECAST_PERIOD_START_FIELD, default="period_start")] = selector.TextSelector()
            schema_fields[vol.Optional(CONF_FORECAST_PV_ESTIMATE_FIELD, default="pv_estimate")] = selector.TextSelector()
            schema_fields[vol.Optional(CONF_FORECAST_TODAY_FROM_STATE, default=True)] = selector.BooleanSelector()

        return self.async_show_form(
            step_id="forecast",
            data_schema=vol.Schema(schema_fields),
            errors=errors,
        )

    async def async_step_prices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 3: Electricity price source."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_id = user_input[CONF_PRICES_ENTITY]
            if not self.hass.states.get(entity_id):
                errors[CONF_PRICES_ENTITY] = "entity_not_found"
            else:
                self._data.update(user_input)
                return await self.async_step_battery()

        prices_type = (user_input or {}).get(CONF_PRICES_TYPE, PRICES_TYPE_FRANK_ENERGIE)
        show_field_mapping = prices_type == PRICES_TYPE_GENERIC

        schema_fields: dict = {
            vol.Required(CONF_PRICES_TYPE, default=PRICES_TYPE_FRANK_ENERGIE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": PRICES_TYPE_FRANK_ENERGIE, "label": "Frank Energie"},
                        {"value": PRICES_TYPE_NORDPOOL, "label": "Nordpool"},
                        {"value": PRICES_TYPE_TIBBER, "label": "Tibber"},
                        {"value": PRICES_TYPE_AWATTAR, "label": "aWATTar"},
                        {"value": PRICES_TYPE_AMBER, "label": "Amber Electric"},
                        {"value": PRICES_TYPE_GENERIC, "label": "Generic (configurable field mapping)"},
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Required(CONF_PRICES_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
        }
        if show_field_mapping:
            schema_fields[vol.Optional(CONF_PRICES_ATTRIBUTE, default="prices")] = selector.TextSelector()
            schema_fields[vol.Optional(CONF_PRICES_PERIOD_START_FIELD, default="from")] = selector.TextSelector()
            schema_fields[vol.Optional(CONF_PRICES_PRICE_FIELD, default="price")] = selector.TextSelector()

        return self.async_show_form(
            step_id="prices",
            data_schema=vol.Schema(schema_fields),
            errors=errors,
        )

    async def async_step_battery(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 4: Battery hardware specifications."""
        if user_input is not None:
            self._data.update(user_input)
            await self.async_set_unique_id(
                f"{self._data[CONF_INVERTER_ENTITY]}_optimizer"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Solar Energy Optimizer",
                data=self._data,
            )

        data_schema = vol.Schema(
            {
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
            step_id="battery",
            data_schema=data_schema,
        )
