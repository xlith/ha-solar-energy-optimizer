"""Tests for provider adapter factory functions."""
from __future__ import annotations

import pytest

from custom_components.solax_energy_optimizer.adapters.factory import (
    build_forecast_adapter,
    build_inverter_adapter,
    build_price_adapter,
)
from custom_components.solax_energy_optimizer.adapters.frank_energie import (
    FrankEnergieAdapter,
)
from custom_components.solax_energy_optimizer.adapters.generic_forecast import (
    GenericForecastAdapter,
)
from custom_components.solax_energy_optimizer.adapters.generic_inverter import (
    GenericSocEntityAdapter,
)
from custom_components.solax_energy_optimizer.adapters.generic_price import (
    GenericPriceAdapter,
)
from custom_components.solax_energy_optimizer.adapters.solax_modbus import (
    SolaxModbusInverterAdapter,
)
from custom_components.solax_energy_optimizer.adapters.solcast import (
    SolcastSolarForecastAdapter,
)


# ---------------------------------------------------------------------------
# build_inverter_adapter
# ---------------------------------------------------------------------------


class TestBuildInverterAdapter:
    def test_defaults_to_solax_modbus_when_no_type(self):
        adapter = build_inverter_adapter({"inverter_entity": "sensor.soc"})
        assert isinstance(adapter, SolaxModbusInverterAdapter)
        assert adapter.source_entity_id == "sensor.soc"

    def test_solax_modbus_type_explicit(self):
        config = {"inverter_entity": "sensor.soc", "inverter_type": "solax_modbus"}
        adapter = build_inverter_adapter(config)
        assert isinstance(adapter, SolaxModbusInverterAdapter)

    def test_generic_state_type(self):
        config = {"inverter_entity": "sensor.soc", "inverter_type": "generic_state"}
        adapter = build_inverter_adapter(config)
        assert isinstance(adapter, GenericSocEntityAdapter)
        assert adapter.source_entity_id == "sensor.soc"

    def test_generic_attribute_type_with_attribute(self):
        config = {
            "inverter_entity": "sensor.soc",
            "inverter_type": "generic_attribute",
            "inverter_soc_attribute": "battery_level",
        }
        adapter = build_inverter_adapter(config)
        assert isinstance(adapter, GenericSocEntityAdapter)

    def test_generic_attribute_type_without_attribute_name(self):
        config = {
            "inverter_entity": "sensor.soc",
            "inverter_type": "generic_attribute",
        }
        adapter = build_inverter_adapter(config)
        assert isinstance(adapter, GenericSocEntityAdapter)

    def test_falls_back_to_legacy_v1_key(self):
        # v1 config entries use "solax_inverter_entity"
        config = {"solax_inverter_entity": "sensor.old_soc"}
        adapter = build_inverter_adapter(config)
        assert adapter.source_entity_id == "sensor.old_soc"

    def test_v2_key_takes_precedence_over_v1(self):
        config = {
            "inverter_entity": "sensor.new_soc",
            "solax_inverter_entity": "sensor.old_soc",
        }
        adapter = build_inverter_adapter(config)
        assert adapter.source_entity_id == "sensor.new_soc"


# ---------------------------------------------------------------------------
# build_forecast_adapter
# ---------------------------------------------------------------------------


class TestBuildForecastAdapter:
    def test_defaults_to_solcast_when_no_type(self):
        adapter = build_forecast_adapter({"forecast_entity": "sensor.forecast"})
        assert isinstance(adapter, SolcastSolarForecastAdapter)
        assert adapter.source_entity_id == "sensor.forecast"

    def test_solcast_type_explicit(self):
        config = {"forecast_entity": "sensor.forecast", "forecast_type": "solcast"}
        adapter = build_forecast_adapter(config)
        assert isinstance(adapter, SolcastSolarForecastAdapter)

    def test_generic_type_with_custom_fields(self):
        config = {
            "forecast_entity": "sensor.forecast",
            "forecast_type": "generic",
            "forecast_attribute": "periods",
            "forecast_period_start_field": "time",
            "forecast_pv_estimate_field": "power_kw",
            "forecast_today_from_state": False,
        }
        adapter = build_forecast_adapter(config)
        assert isinstance(adapter, GenericForecastAdapter)
        assert adapter.source_entity_id == "sensor.forecast"
        assert adapter._field_map.forecast_attribute == "periods"
        assert adapter._field_map.period_start_field == "time"
        assert adapter._field_map.pv_estimate_field == "power_kw"
        assert adapter._field_map.today_total_from_state is False

    def test_generic_type_uses_defaults_for_missing_fields(self):
        config = {"forecast_entity": "sensor.forecast", "forecast_type": "generic"}
        adapter = build_forecast_adapter(config)
        assert isinstance(adapter, GenericForecastAdapter)
        assert adapter._field_map.forecast_attribute == "forecasts"
        assert adapter._field_map.period_start_field == "period_start"
        assert adapter._field_map.pv_estimate_field == "pv_estimate"
        assert adapter._field_map.today_total_from_state is True

    def test_falls_back_to_legacy_v1_key(self):
        config = {"solcast_entity": "sensor.old_forecast"}
        adapter = build_forecast_adapter(config)
        assert adapter.source_entity_id == "sensor.old_forecast"

    def test_v2_key_takes_precedence_over_v1(self):
        config = {
            "forecast_entity": "sensor.new_forecast",
            "solcast_entity": "sensor.old_forecast",
        }
        adapter = build_forecast_adapter(config)
        assert adapter.source_entity_id == "sensor.new_forecast"


# ---------------------------------------------------------------------------
# build_price_adapter
# ---------------------------------------------------------------------------


class TestBuildPriceAdapter:
    def test_defaults_to_frank_energie_when_no_type(self):
        adapter = build_price_adapter({"prices_entity": "sensor.prices"})
        assert isinstance(adapter, FrankEnergieAdapter)
        assert adapter.source_entity_id == "sensor.prices"

    def test_frank_energie_type_explicit(self):
        config = {"prices_entity": "sensor.prices", "prices_type": "frank_energie"}
        adapter = build_price_adapter(config)
        assert isinstance(adapter, FrankEnergieAdapter)

    def test_nordpool_type_produces_generic_adapter(self):
        config = {"prices_entity": "sensor.prices", "prices_type": "nordpool"}
        adapter = build_price_adapter(config)
        assert isinstance(adapter, GenericPriceAdapter)

    def test_tibber_type_produces_generic_adapter(self):
        config = {"prices_entity": "sensor.prices", "prices_type": "tibber"}
        adapter = build_price_adapter(config)
        assert isinstance(adapter, GenericPriceAdapter)

    def test_awattar_type_produces_generic_adapter(self):
        config = {"prices_entity": "sensor.prices", "prices_type": "awattar"}
        adapter = build_price_adapter(config)
        assert isinstance(adapter, GenericPriceAdapter)

    def test_amber_type_produces_generic_adapter(self):
        config = {"prices_entity": "sensor.prices", "prices_type": "amber"}
        adapter = build_price_adapter(config)
        assert isinstance(adapter, GenericPriceAdapter)

    def test_generic_type_with_custom_fields(self):
        config = {
            "prices_entity": "sensor.prices",
            "prices_type": "generic",
            "prices_attribute": "hourly_prices",
            "prices_period_start_field": "datetime",
            "prices_price_field": "value",
        }
        adapter = build_price_adapter(config)
        assert isinstance(adapter, GenericPriceAdapter)
        assert adapter._field_map.prices_attribute == "hourly_prices"
        assert adapter._field_map.period_start_field == "datetime"
        assert adapter._field_map.price_field == "value"

    def test_generic_type_uses_defaults_for_missing_fields(self):
        config = {"prices_entity": "sensor.prices", "prices_type": "generic"}
        adapter = build_price_adapter(config)
        assert isinstance(adapter, GenericPriceAdapter)
        assert adapter._field_map.prices_attribute == "prices"
        assert adapter._field_map.period_start_field == "from"
        assert adapter._field_map.price_field == "price"

    def test_falls_back_to_legacy_frank_energie_key(self):
        config = {"frank_energie_entity": "sensor.old_prices"}
        adapter = build_price_adapter(config)
        assert adapter.source_entity_id == "sensor.old_prices"

    def test_v2_key_takes_precedence_over_v1(self):
        config = {
            "prices_entity": "sensor.new_prices",
            "frank_energie_entity": "sensor.old_prices",
        }
        adapter = build_price_adapter(config)
        assert adapter.source_entity_id == "sensor.new_prices"
