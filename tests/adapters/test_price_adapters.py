"""Tests for electricity price adapters."""
from __future__ import annotations

import pytest

from custom_components.solax_energy_optimizer.adapters.frank_energie import (
    FrankEnergieAdapter,
)
from custom_components.solax_energy_optimizer.adapters.generic_price import (
    GenericPriceAdapter,
    PriceFieldMap,
)


ENTITY_ID = "sensor.electricity_price"

FRANK_PRICES = [
    {"from": "2024-06-01T00:00:00+00:00", "price": 0.21},
    {"from": "2024-06-01T01:00:00+00:00", "price": 0.18},
    {"from": "2024-06-01T02:00:00+00:00", "price": 0.15},
]


# ---------------------------------------------------------------------------
# FrankEnergieAdapter
# ---------------------------------------------------------------------------


class TestFrankEnergieAdapter:
    def test_source_entity_id(self):
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.source_entity_id == ENTITY_ID

    def test_get_prices_returns_list(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {"prices": FRANK_PRICES})
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_prices(hass) == FRANK_PRICES

    def test_get_prices_returns_empty_when_entity_missing(self, hass):
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_prices(hass) == []

    def test_get_prices_returns_empty_when_no_attributes(self, hass):
        hass.set_state(ENTITY_ID, "0.21")
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_prices(hass) == []

    def test_get_prices_returns_empty_when_attribute_missing(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {"other": []})
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_prices(hass) == []

    def test_get_prices_returns_empty_when_attribute_not_list(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {"prices": "not_a_list"})
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_prices(hass) == []

    def test_get_current_price_parses_state(self, hass):
        hass.set_state(ENTITY_ID, "0.2134", {"prices": FRANK_PRICES})
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_current_price(hass) == pytest.approx(0.2134)

    def test_get_current_price_returns_none_when_entity_missing(self, hass):
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_current_price(hass) is None

    def test_get_current_price_returns_none_when_unavailable(self, hass):
        hass.set_state(ENTITY_ID, "unavailable")
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_current_price(hass) is None

    def test_get_current_price_returns_none_when_unknown(self, hass):
        hass.set_state(ENTITY_ID, "unknown")
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_current_price(hass) is None

    def test_get_current_price_returns_none_for_non_numeric(self, hass):
        hass.set_state(ENTITY_ID, "error")
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_current_price(hass) is None

    def test_get_current_price_negative_price(self, hass):
        hass.set_state(ENTITY_ID, "-0.05")
        adapter = FrankEnergieAdapter(ENTITY_ID)
        assert adapter.get_current_price(hass) == pytest.approx(-0.05)


# ---------------------------------------------------------------------------
# GenericPriceAdapter
# ---------------------------------------------------------------------------


GENERIC_PRICES_RAW = [
    {"start": "2024-06-01T00:00:00+00:00", "cost": 0.21},
    {"start": "2024-06-01T01:00:00+00:00", "cost": 0.18},
    {"start": "2024-06-01T02:00:00+00:00", "cost": 0.15},
]

FIELD_MAP = PriceFieldMap(
    prices_attribute="entries",
    period_start_field="start",
    price_field="cost",
)


class TestGenericPriceAdapter:
    def test_source_entity_id(self):
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.source_entity_id == ENTITY_ID

    def test_get_prices_normalizes_field_names(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {"entries": GENERIC_PRICES_RAW})
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        result = adapter.get_prices(hass)
        assert len(result) == 3
        assert result[0] == {"from": "2024-06-01T00:00:00+00:00", "price": 0.21}
        assert result[1] == {"from": "2024-06-01T01:00:00+00:00", "price": 0.18}

    def test_get_prices_returns_empty_when_entity_missing(self, hass):
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.get_prices(hass) == []

    def test_get_prices_returns_empty_when_attribute_missing(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {})
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.get_prices(hass) == []

    def test_get_prices_returns_empty_when_attribute_not_list(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {"entries": {"not": "a list"}})
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.get_prices(hass) == []

    def test_get_prices_skips_non_dict_items(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {"entries": [{"start": "2024-06-01T00:00:00+00:00", "cost": 0.21}, "bad", 99]})
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        result = adapter.get_prices(hass)
        assert len(result) == 1

    def test_get_prices_missing_price_field_defaults_to_zero(self, hass):
        hass.set_state(ENTITY_ID, "0.21", {"entries": [{"start": "2024-06-01T00:00:00+00:00"}]})
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        result = adapter.get_prices(hass)
        assert result[0]["price"] == 0

    def test_get_current_price_reads_from_state(self, hass):
        hass.set_state(ENTITY_ID, "0.195", {"entries": GENERIC_PRICES_RAW})
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.get_current_price(hass) == pytest.approx(0.195)

    def test_get_current_price_returns_none_when_entity_missing(self, hass):
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.get_current_price(hass) is None

    def test_get_current_price_returns_none_when_unavailable(self, hass):
        hass.set_state(ENTITY_ID, "unavailable")
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.get_current_price(hass) is None

    def test_get_current_price_returns_none_for_non_numeric(self, hass):
        hass.set_state(ENTITY_ID, "n/a")
        adapter = GenericPriceAdapter(ENTITY_ID, FIELD_MAP)
        assert adapter.get_current_price(hass) is None
