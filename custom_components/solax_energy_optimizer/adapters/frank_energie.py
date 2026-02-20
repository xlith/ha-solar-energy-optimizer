"""Adapter for Frank Energie electricity price integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from .base import PriceAdapter


class FrankEnergieAdapter(PriceAdapter):
    """Parses the Frank Energie integration attribute schema.

    Expects:
      - entity state: current price in currency/kWh
      - attributes["prices"]: list of dicts with "from" (ISO 8601 datetime)
          and "price" (float, currency/kWh)
    """

    def __init__(self, entity_id: str) -> None:
        self._entity_id = entity_id

    @property
    def source_entity_id(self) -> str:
        return self._entity_id

    def get_prices(self, hass: HomeAssistant) -> list[dict]:
        state = hass.states.get(self._entity_id)
        if state is None or not state.attributes:
            return []
        price_entries = state.attributes.get("prices", [])
        return price_entries if isinstance(price_entries, list) else []

    def get_current_price(self, hass: HomeAssistant) -> float | None:
        state = hass.states.get(self._entity_id)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None
