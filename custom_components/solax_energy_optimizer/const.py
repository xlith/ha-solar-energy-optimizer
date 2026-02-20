"""Constants for the Solax Energy Optimizer integration."""
from datetime import timedelta
from typing import Final

DOMAIN: Final = "solax_energy_optimizer"

# Configuration keys
CONF_SOLAX_INVERTER_ENTITY: Final = "solax_inverter_entity"
CONF_SOLCAST_ENTITY: Final = "solcast_entity"
CONF_ELECTRICITY_PRICES_ENTITY: Final = "frank_energie_entity"
CONF_FRANK_ENERGIE_ENTITY = CONF_ELECTRICITY_PRICES_ENTITY  # backwards compat for existing config entries
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
ENTITY_DAILY_COST: Final = "daily_cost"
ENTITY_DAILY_SAVINGS: Final = "daily_savings"
ENTITY_MONTHLY_COST: Final = "monthly_cost"
ENTITY_MONTHLY_SAVINGS: Final = "monthly_savings"
ENTITY_AUTOMATION_ENABLED: Final = "automation_enabled"
ENTITY_MANUAL_OVERRIDE: Final = "manual_override"
ENTITY_DRY_RUN: Final = "dry_run"

# Actions
ACTION_CHARGE: Final = "charge"
ACTION_DISCHARGE: Final = "discharge"
ACTION_IDLE: Final = "idle"

# Attributes
ATTR_BATTERY_SOC: Final = "battery_soc"
ATTR_CURRENT_PRICE: Final = "current_price"
ATTR_SOLAR_FORECAST: Final = "solar_forecast"
ATTR_DRY_RUN_MODE: Final = "dry_run_mode"
