"""Generic inverter adapter for any battery SOC source."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from .base import InverterAdapter


class GenericSocEntityAdapter(InverterAdapter):
    """Reads battery SOC from an entity state or a named attribute.

    Use this for inverters that expose SOC as an attribute of another sensor
    (e.g., Fronius, SMA, Huawei Solar) rather than as the entity's state.
    """

    def __init__(self, entity_id: str, soc_attribute: str | None = None) -> None:
        """Initialize the adapter.

        Args:
            entity_id: HA entity ID to read from.
            soc_attribute: If None, reads from entity state. If a string,
                reads from the named attribute on the entity.
        """
        self._entity_id = entity_id
        self._soc_attribute = soc_attribute

    @property
    def source_entity_id(self) -> str:
        return self._entity_id

    def get_battery_soc(self, hass: HomeAssistant) -> float | None:
        state = hass.states.get(self._entity_id)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            if self._soc_attribute:
                return float(state.attributes[self._soc_attribute])
            return float(state.state)
        except (ValueError, TypeError, KeyError):
            return None
