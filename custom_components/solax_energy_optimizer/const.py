"""Constants for the Solar Energy Optimizer integration."""
from datetime import timedelta
from typing import Final

DOMAIN: Final = "solax_energy_optimizer"

# Configuration keys (v2 — generic, provider-agnostic)
CONF_INVERTER_ENTITY: Final = "inverter_entity"
CONF_FORECAST_ENTITY: Final = "forecast_entity"
CONF_PRICES_ENTITY: Final = "prices_entity"

CONF_INVERTER_TYPE: Final = "inverter_type"
CONF_FORECAST_TYPE: Final = "forecast_type"
CONF_PRICES_TYPE: Final = "prices_type"

# Inverter type options
INVERTER_TYPE_SOLAX_MODBUS: Final = "solax_modbus"
INVERTER_TYPE_GENERIC_STATE: Final = "generic_state"
INVERTER_TYPE_GENERIC_ATTRIBUTE: Final = "generic_attribute"

# Solar forecast type options
FORECAST_TYPE_SOLCAST: Final = "solcast"
FORECAST_TYPE_GENERIC: Final = "generic"

# Electricity price type options
PRICES_TYPE_FRANK_ENERGIE: Final = "frank_energie"
PRICES_TYPE_NORDPOOL: Final = "nordpool"
PRICES_TYPE_TIBBER: Final = "tibber"
PRICES_TYPE_AWATTAR: Final = "awattar"
PRICES_TYPE_AMBER: Final = "amber"
PRICES_TYPE_GENERIC: Final = "generic"

# Generic field mapping config keys
CONF_INVERTER_SOC_ATTRIBUTE: Final = "inverter_soc_attribute"
CONF_FORECAST_ATTRIBUTE: Final = "forecast_attribute"
CONF_FORECAST_PERIOD_START_FIELD: Final = "forecast_period_start_field"
CONF_FORECAST_PV_ESTIMATE_FIELD: Final = "forecast_pv_estimate_field"
CONF_FORECAST_TODAY_FROM_STATE: Final = "forecast_today_from_state"
CONF_PRICES_ATTRIBUTE: Final = "prices_attribute"
CONF_PRICES_PERIOD_START_FIELD: Final = "prices_period_start_field"
CONF_PRICES_PRICE_FIELD: Final = "prices_price_field"

# Legacy v1 config keys — kept as aliases so migration code can read them
CONF_SOLAX_INVERTER_ENTITY: Final = "solax_inverter_entity"
CONF_SOLCAST_ENTITY: Final = "solcast_entity"
CONF_ELECTRICITY_PRICES_ENTITY: Final = "frank_energie_entity"
CONF_FRANK_ENERGIE_ENTITY = CONF_ELECTRICITY_PRICES_ENTITY

CONF_BATTERY_CAPACITY: Final = "battery_capacity"
CONF_MAX_CHARGE_RATE: Final = "max_charge_rate"
CONF_MAX_DISCHARGE_RATE: Final = "max_discharge_rate"
CONF_MIN_SOC: Final = "min_soc"
CONF_MAX_SOC: Final = "max_soc"

# Default values
DEFAULT_MIN_SOC: Final = 20
DEFAULT_MAX_SOC: Final = 95
DEFAULT_UPDATE_INTERVAL: Final = timedelta(minutes=5)

# Optimization strategies
STRATEGY_MINIMIZE_COST: Final = "minimize_cost"
STRATEGY_MAXIMIZE_SELF_CONSUMPTION: Final = "maximize_self_consumption"
STRATEGY_GRID_INDEPENDENCE: Final = "grid_independence"
STRATEGY_BALANCED: Final = "balanced"

STRATEGIES: Final = [
    STRATEGY_MINIMIZE_COST,
    STRATEGY_MAXIMIZE_SELF_CONSUMPTION,
    STRATEGY_GRID_INDEPENDENCE,
    STRATEGY_BALANCED,
]

# Entity keys
ENTITY_CURRENT_STRATEGY: Final = "current_strategy"
ENTITY_NEXT_ACTION: Final = "next_action"
ENTITY_LAST_ACTION_TIME: Final = "last_action_time"
ENTITY_NEXT_UPDATE_TIME: Final = "next_update_time"
ENTITY_DECISION_REASON: Final = "decision_reason"
ENTITY_UPDATE_COUNT: Final = "update_count"
ENTITY_BATTERY_SOC: Final = "battery_soc"
ENTITY_CURRENT_PRICE: Final = "current_price"
ENTITY_SOLAR_FORECAST_TODAY: Final = "solar_forecast_today"
ENTITY_TARGET_SOC: Final = "target_soc"
ENTITY_DAILY_COST: Final = "daily_cost"
ENTITY_DAILY_SAVINGS: Final = "daily_savings"
ENTITY_MONTHLY_COST: Final = "monthly_cost"
ENTITY_MONTHLY_SAVINGS: Final = "monthly_savings"
ENTITY_AUTOMATION_ENABLED: Final = "automation_enabled"
ENTITY_MANUAL_OVERRIDE: Final = "manual_override"
ENTITY_DRY_RUN: Final = "dry_run"
ENTITY_MIN_SOC: Final = "min_soc"
ENTITY_MAX_SOC: Final = "max_soc"

# Actions
ACTION_CHARGE: Final = "charge"
ACTION_DISCHARGE: Final = "discharge"
ACTION_IDLE: Final = "idle"

# Attributes
ATTR_BATTERY_SOC: Final = "battery_soc"
ATTR_CURRENT_PRICE: Final = "current_price"
ATTR_SOLAR_FORECAST: Final = "solar_forecast"
ATTR_DRY_RUN_MODE: Final = "dry_run_mode"
