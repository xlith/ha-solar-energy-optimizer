"""Factory functions for building provider adapters from config entry data."""
from __future__ import annotations

from .base import InverterAdapter, PriceAdapter, SolarForecastAdapter
from .frank_energie import FrankEnergieAdapter
from .generic_forecast import ForecastFieldMap, GenericForecastAdapter
from .generic_inverter import GenericSocEntityAdapter
from .generic_price import GenericPriceAdapter, PriceFieldMap
from .solax_modbus import SolaxModbusInverterAdapter
from .solcast import SolcastSolarForecastAdapter

INVERTER_TYPE_SOLAX_MODBUS = "solax_modbus"
INVERTER_TYPE_GENERIC_STATE = "generic_state"
INVERTER_TYPE_GENERIC_ATTRIBUTE = "generic_attribute"

FORECAST_TYPE_SOLCAST = "solcast"
FORECAST_TYPE_GENERIC = "generic"

PRICES_TYPE_FRANK_ENERGIE = "frank_energie"
PRICES_TYPE_GENERIC = "generic"


def build_inverter_adapter(config_data: dict) -> InverterAdapter:
    """Build the correct InverterAdapter from config entry data."""
    inverter_type = config_data.get("inverter_type", INVERTER_TYPE_SOLAX_MODBUS)
    entity_id = config_data.get("inverter_entity") or config_data.get("solax_inverter_entity", "")

    if inverter_type == INVERTER_TYPE_SOLAX_MODBUS:
        return SolaxModbusInverterAdapter(entity_id)

    if inverter_type == INVERTER_TYPE_GENERIC_ATTRIBUTE:
        return GenericSocEntityAdapter(
            entity_id,
            soc_attribute=config_data.get("inverter_soc_attribute") or None,
        )

    # generic_state — same as solax_modbus: reads float from entity state
    return GenericSocEntityAdapter(entity_id, soc_attribute=None)


def build_forecast_adapter(config_data: dict) -> SolarForecastAdapter:
    """Build the correct SolarForecastAdapter from config entry data."""
    forecast_type = config_data.get("forecast_type", FORECAST_TYPE_SOLCAST)
    entity_id = config_data.get("forecast_entity") or config_data.get("solcast_entity", "")

    if forecast_type == FORECAST_TYPE_SOLCAST:
        return SolcastSolarForecastAdapter(entity_id)

    field_map = ForecastFieldMap(
        forecast_attribute=config_data.get("forecast_attribute") or "forecasts",
        period_start_field=config_data.get("forecast_period_start_field") or "period_start",
        pv_estimate_field=config_data.get("forecast_pv_estimate_field") or "pv_estimate",
        today_total_from_state=config_data.get("forecast_today_from_state", True),
    )
    return GenericForecastAdapter(entity_id, field_map)


def build_price_adapter(config_data: dict) -> PriceAdapter:
    """Build the correct PriceAdapter from config entry data."""
    prices_type = config_data.get("prices_type", PRICES_TYPE_FRANK_ENERGIE)
    entity_id = (
        config_data.get("prices_entity")
        or config_data.get("frank_energie_entity")
        or config_data.get("electricity_prices_entity", "")
    )

    if prices_type == PRICES_TYPE_FRANK_ENERGIE:
        return FrankEnergieAdapter(entity_id)

    field_map = PriceFieldMap(
        prices_attribute=config_data.get("prices_attribute") or "prices",
        period_start_field=config_data.get("prices_period_start_field") or "from",
        price_field=config_data.get("prices_price_field") or "price",
    )
    return GenericPriceAdapter(entity_id, field_map)
