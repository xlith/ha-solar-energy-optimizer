"""Tests for solar forecast adapters."""
from __future__ import annotations

import pytest

from custom_components.solax_energy_optimizer.adapters.generic_forecast import (
    ForecastFieldMap,
    GenericForecastAdapter,
)
from custom_components.solax_energy_optimizer.adapters.solcast import (
    SolcastSolarForecastAdapter,
)


ENTITY_ID = "sensor.solar_forecast"

SOLCAST_FORECAST = [
    {"period_start": "2024-06-01T06:00:00+00:00", "pv_estimate": 0.5},
    {"period_start": "2024-06-01T06:30:00+00:00", "pv_estimate": 1.2},
    {"period_start": "2024-06-01T07:00:00+00:00", "pv_estimate": 2.1},
]


# ---------------------------------------------------------------------------
# SolcastSolarForecastAdapter
# ---------------------------------------------------------------------------


class TestSolcastSolarForecastAdapter:
    def test_source_entity_id(self):
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.source_entity_id == ENTITY_ID

    def test_get_forecast_returns_detailed_forecast(self, hass):
        hass.set_state(ENTITY_ID, "8.5", {"detailedForecast": SOLCAST_FORECAST})
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        result = adapter.get_forecast(hass)
        assert result == SOLCAST_FORECAST

    def test_get_forecast_returns_empty_when_entity_missing(self, hass):
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_forecast(hass) == []

    def test_get_forecast_returns_empty_when_no_attributes(self, hass):
        hass.set_state(ENTITY_ID, "8.5")
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_forecast(hass) == []

    def test_get_forecast_returns_empty_when_attribute_missing(self, hass):
        hass.set_state(ENTITY_ID, "8.5", {"other_attr": []})
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_forecast(hass) == []

    def test_get_solar_today_parses_state(self, hass):
        hass.set_state(ENTITY_ID, "8.5", {"detailedForecast": SOLCAST_FORECAST})
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_solar_today(hass) == 8.5

    def test_get_solar_today_returns_none_when_entity_missing(self, hass):
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_solar_today(hass) is None

    def test_get_solar_today_returns_none_when_unavailable(self, hass):
        hass.set_state(ENTITY_ID, "unavailable")
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_solar_today(hass) is None

    def test_get_solar_today_returns_none_when_unknown(self, hass):
        hass.set_state(ENTITY_ID, "unknown")
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_solar_today(hass) is None

    def test_get_solar_today_returns_none_for_non_numeric_state(self, hass):
        hass.set_state(ENTITY_ID, "not_a_number")
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_solar_today(hass) is None

    def test_get_solar_today_zero(self, hass):
        hass.set_state(ENTITY_ID, "0.0")
        adapter = SolcastSolarForecastAdapter(ENTITY_ID)
        assert adapter.get_solar_today(hass) == 0.0


# ---------------------------------------------------------------------------
# GenericForecastAdapter — reading today total from state
# ---------------------------------------------------------------------------


GENERIC_FORECAST_RAW = [
    {"start": "2024-06-01T06:00:00+00:00", "power": 0.5},
    {"start": "2024-06-01T06:30:00+00:00", "power": 1.2},
    {"start": "2024-06-01T07:00:00+00:00", "power": 2.1},
]

FIELD_MAP_STATE = ForecastFieldMap(
    forecast_attribute="forecasts",
    period_start_field="start",
    pv_estimate_field="power",
    today_total_from_state=True,
)

FIELD_MAP_SUM = ForecastFieldMap(
    forecast_attribute="forecasts",
    period_start_field="start",
    pv_estimate_field="power",
    today_total_from_state=False,
)


class TestGenericForecastAdapterFromState:
    def test_source_entity_id(self):
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        assert adapter.source_entity_id == ENTITY_ID

    def test_get_forecast_normalizes_field_names(self, hass):
        hass.set_state(ENTITY_ID, "5.0", {"forecasts": GENERIC_FORECAST_RAW})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        result = adapter.get_forecast(hass)
        assert len(result) == 3
        assert result[0] == {"period_start": "2024-06-01T06:00:00+00:00", "pv_estimate": 0.5}
        assert result[1] == {"period_start": "2024-06-01T06:30:00+00:00", "pv_estimate": 1.2}
        assert result[2] == {"period_start": "2024-06-01T07:00:00+00:00", "pv_estimate": 2.1}

    def test_get_forecast_returns_empty_when_entity_missing(self, hass):
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        assert adapter.get_forecast(hass) == []

    def test_get_forecast_returns_empty_when_attribute_missing(self, hass):
        hass.set_state(ENTITY_ID, "5.0", {})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        assert adapter.get_forecast(hass) == []

    def test_get_forecast_skips_non_dict_items(self, hass):
        hass.set_state(ENTITY_ID, "5.0", {"forecasts": [{"start": "2024-06-01T06:00:00+00:00", "power": 1.0}, "bad_item", 42]})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        result = adapter.get_forecast(hass)
        assert len(result) == 1

    def test_get_forecast_returns_empty_when_attribute_not_list(self, hass):
        hass.set_state(ENTITY_ID, "5.0", {"forecasts": "not_a_list"})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        assert adapter.get_forecast(hass) == []

    def test_get_forecast_missing_field_defaults_to_zero(self, hass):
        hass.set_state(ENTITY_ID, "5.0", {"forecasts": [{"start": "2024-06-01T06:00:00+00:00"}]})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        result = adapter.get_forecast(hass)
        assert result[0]["pv_estimate"] == 0

    def test_get_solar_today_reads_from_state(self, hass):
        hass.set_state(ENTITY_ID, "6.75", {"forecasts": GENERIC_FORECAST_RAW})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        assert adapter.get_solar_today(hass) == 6.75

    def test_get_solar_today_returns_none_when_entity_missing(self, hass):
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        assert adapter.get_solar_today(hass) is None

    def test_get_solar_today_returns_none_when_unavailable(self, hass):
        hass.set_state(ENTITY_ID, "unavailable")
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_STATE)
        assert adapter.get_solar_today(hass) is None


# ---------------------------------------------------------------------------
# GenericForecastAdapter — summing from forecast list
# ---------------------------------------------------------------------------


class TestGenericForecastAdapterFromSum:
    def test_get_solar_today_sums_from_list(self, hass):
        # Three 30-min periods: 0.5 + 1.2 + 2.1 = 3.8 kW × 0.5h = 1.9 kWh
        hass.set_state(ENTITY_ID, "irrelevant", {"forecasts": GENERIC_FORECAST_RAW})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_SUM)
        result = adapter.get_solar_today(hass)
        assert result == pytest.approx(1.9)

    def test_get_solar_today_returns_none_when_forecast_empty(self, hass):
        hass.set_state(ENTITY_ID, "0.0", {"forecasts": []})
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_SUM)
        assert adapter.get_solar_today(hass) is None

    def test_get_solar_today_returns_none_when_entity_missing(self, hass):
        adapter = GenericForecastAdapter(ENTITY_ID, FIELD_MAP_SUM)
        assert adapter.get_solar_today(hass) is None
