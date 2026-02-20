"""Tests for inverter adapters (battery SOC sources)."""
from __future__ import annotations

import pytest

from custom_components.solax_energy_optimizer.adapters.generic_inverter import (
    GenericSocEntityAdapter,
)
from custom_components.solax_energy_optimizer.adapters.solax_modbus import (
    SolaxModbusInverterAdapter,
)


ENTITY_ID = "sensor.battery_soc"


# ---------------------------------------------------------------------------
# SolaxModbusInverterAdapter
# ---------------------------------------------------------------------------


class TestSolaxModbusInverterAdapter:
    def test_source_entity_id(self):
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.source_entity_id == ENTITY_ID

    def test_returns_float_from_state(self, hass):
        hass.set_state(ENTITY_ID, "75.5")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) == 75.5

    def test_returns_integer_state_as_float(self, hass):
        hass.set_state(ENTITY_ID, "80")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) == 80.0

    def test_returns_none_when_entity_missing(self, hass):
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_state_unavailable(self, hass):
        hass.set_state(ENTITY_ID, "unavailable")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_state_unknown(self, hass):
        hass.set_state(ENTITY_ID, "unknown")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_state_empty_string(self, hass):
        hass.set_state(ENTITY_ID, "")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_state_not_numeric(self, hass):
        hass.set_state(ENTITY_ID, "not_a_number")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_boundary_zero(self, hass):
        hass.set_state(ENTITY_ID, "0")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) == 0.0

    def test_boundary_hundred(self, hass):
        hass.set_state(ENTITY_ID, "100")
        adapter = SolaxModbusInverterAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) == 100.0


# ---------------------------------------------------------------------------
# GenericSocEntityAdapter — reading from state
# ---------------------------------------------------------------------------


class TestGenericSocEntityAdapterFromState:
    def test_source_entity_id(self):
        adapter = GenericSocEntityAdapter(ENTITY_ID)
        assert adapter.source_entity_id == ENTITY_ID

    def test_reads_soc_from_state(self, hass):
        hass.set_state(ENTITY_ID, "62.3")
        adapter = GenericSocEntityAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) == 62.3

    def test_returns_none_when_entity_missing(self, hass):
        adapter = GenericSocEntityAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_unavailable(self, hass):
        hass.set_state(ENTITY_ID, "unavailable")
        adapter = GenericSocEntityAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_unknown(self, hass):
        hass.set_state(ENTITY_ID, "unknown")
        adapter = GenericSocEntityAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_for_non_numeric_state(self, hass):
        hass.set_state(ENTITY_ID, "error")
        adapter = GenericSocEntityAdapter(ENTITY_ID)
        assert adapter.get_battery_soc(hass) is None


# ---------------------------------------------------------------------------
# GenericSocEntityAdapter — reading from attribute
# ---------------------------------------------------------------------------


class TestGenericSocEntityAdapterFromAttribute:
    def test_reads_soc_from_attribute(self, hass):
        hass.set_state(ENTITY_ID, "some_state", {"battery_level": "55.0"})
        adapter = GenericSocEntityAdapter(ENTITY_ID, soc_attribute="battery_level")
        assert adapter.get_battery_soc(hass) == 55.0

    def test_attribute_takes_precedence_over_state(self, hass):
        hass.set_state(ENTITY_ID, "99", {"soc": "42"})
        adapter = GenericSocEntityAdapter(ENTITY_ID, soc_attribute="soc")
        assert adapter.get_battery_soc(hass) == 42.0

    def test_returns_none_when_attribute_missing(self, hass):
        hass.set_state(ENTITY_ID, "50", {})
        adapter = GenericSocEntityAdapter(ENTITY_ID, soc_attribute="battery_level")
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_attribute_not_numeric(self, hass):
        hass.set_state(ENTITY_ID, "50", {"battery_level": "bad"})
        adapter = GenericSocEntityAdapter(ENTITY_ID, soc_attribute="battery_level")
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_entity_missing(self, hass):
        adapter = GenericSocEntityAdapter(ENTITY_ID, soc_attribute="battery_level")
        assert adapter.get_battery_soc(hass) is None

    def test_returns_none_when_state_unavailable_with_attribute(self, hass):
        # Even with a valid attribute, if state says unavailable the entity
        # is not in a valid operating state — we still return None.
        hass.set_state(ENTITY_ID, "unavailable", {"battery_level": "60"})
        adapter = GenericSocEntityAdapter(ENTITY_ID, soc_attribute="battery_level")
        # Attribute-based adapter: state guard applies before attribute lookup
        # State is "unavailable" so get_battery_soc returns None
        assert adapter.get_battery_soc(hass) is None
