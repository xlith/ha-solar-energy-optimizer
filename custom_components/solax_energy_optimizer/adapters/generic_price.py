"""Generic electricity price adapter with configurable field mapping."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .base import PriceAdapter


@dataclass
class PriceFieldMap:
    """Maps provider-specific attribute names to the normalized schema.

    Attributes:
        prices_attribute: Name of the entity attribute that holds the price
            list (e.g., "prices", "entries", "hourly_prices").
        period_start_field: Field name within each price item that contains
            the period start datetime (e.g., "from", "start", "datetime").
        price_field: Field name within each price item that contains the
            price value (e.g., "price", "value", "cost").
    """

    prices_attribute: str
    period_start_field: str
    price_field: str


class GenericPriceAdapter(PriceAdapter):
    """Works with Tibber, Nordpool, Awattar, Amber, or any list-of-dicts source."""

    def __init__(self, entity_id: str, field_map: PriceFieldMap) -> None:
        self._entity_id = entity_id
        self._field_map = field_map

    @property
    def source_entity_id(self) -> str:
        return self._entity_id

    def get_prices(self, hass: HomeAssistant) -> list[dict]:
        state = hass.states.get(self._entity_id)
        if state is None or not state.attributes:
            return []
        raw_list = state.attributes.get(self._field_map.prices_attribute, [])
        if not isinstance(raw_list, list):
            return []
        normalized = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            normalized.append({
                "from": item.get(self._field_map.period_start_field),
                "price": item.get(self._field_map.price_field, 0),
            })
        return normalized

    def get_current_price(self, hass: HomeAssistant) -> float | None:
        state = hass.states.get(self._entity_id)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None
