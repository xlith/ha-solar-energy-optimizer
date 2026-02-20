"""Adapter for Solcast Solar forecast integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from .base import SolarForecastAdapter


class SolcastSolarForecastAdapter(SolarForecastAdapter):
    """Parses the Solcast Solar integration attribute schema.

    Expects:
      - entity state: today's total forecast in kWh
      - attributes["detailedForecast"]: list of dicts with
          "period_start" (ISO 8601 datetime) and "pv_estimate" (kW)
    """

    def __init__(self, entity_id: str) -> None:
        self._entity_id = entity_id

    @property
    def source_entity_id(self) -> str:
        return self._entity_id

    def get_forecast(self, hass: HomeAssistant) -> list[dict]:
        state = hass.states.get(self._entity_id)
        if state is None or not state.attributes:
            return []
        return state.attributes.get("detailedForecast", [])

    def get_solar_today(self, hass: HomeAssistant) -> float | None:
        state = hass.states.get(self._entity_id)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None
