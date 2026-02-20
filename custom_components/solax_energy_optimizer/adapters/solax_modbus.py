"""Adapter for Solax Modbus inverter integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from .base import InverterAdapter


class SolaxModbusInverterAdapter(InverterAdapter):
    """Reads battery SOC directly from a Solax Modbus entity state."""

    def __init__(self, entity_id: str) -> None:
        self._entity_id = entity_id

    @property
    def source_entity_id(self) -> str:
        return self._entity_id

    def get_battery_soc(self, hass: HomeAssistant) -> float | None:
        state = hass.states.get(self._entity_id)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None
