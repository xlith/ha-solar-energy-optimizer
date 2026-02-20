"""Generic solar forecast adapter with configurable field mapping."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .base import SolarForecastAdapter


@dataclass
class ForecastFieldMap:
    """Maps provider-specific attribute names to the normalized schema.

    Attributes:
        forecast_attribute: Name of the entity attribute that holds the
            forecast list (e.g., "detailedForecast", "forecasts", "periods").
        period_start_field: Field name within each forecast item that contains
            the period start datetime (e.g., "period_start", "time", "start_time").
        pv_estimate_field: Field name within each forecast item that contains
            the power estimate in kW (e.g., "pv_estimate", "value", "power_kw").
        today_total_from_state: If True, read today's total kWh from the entity
            state. If False, sum the pv_estimate values from the forecast list
            (assuming 30-minute intervals).
    """

    forecast_attribute: str
    period_start_field: str
    pv_estimate_field: str
    today_total_from_state: bool = True


class GenericForecastAdapter(SolarForecastAdapter):
    """Works with any integration that exposes forecast as an attribute list."""

    def __init__(self, entity_id: str, field_map: ForecastFieldMap) -> None:
        self._entity_id = entity_id
        self._field_map = field_map

    @property
    def source_entity_id(self) -> str:
        return self._entity_id

    def get_forecast(self, hass: HomeAssistant) -> list[dict]:
        state = hass.states.get(self._entity_id)
        if state is None or not state.attributes:
            return []
        raw_list = state.attributes.get(self._field_map.forecast_attribute, [])
        if not isinstance(raw_list, list):
            return []
        normalized = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            normalized.append({
                "period_start": item.get(self._field_map.period_start_field),
                "pv_estimate": item.get(self._field_map.pv_estimate_field, 0),
            })
        return normalized

    def get_solar_today(self, hass: HomeAssistant) -> float | None:
        state = hass.states.get(self._entity_id)
        if state is None:
            return None
        if self._field_map.today_total_from_state:
            if state.state in ("unavailable", "unknown", ""):
                return None
            try:
                return float(state.state)
            except (ValueError, TypeError):
                return None
        # Sum pv_estimate from list (assumes 30-minute intervals: kW * 0.5h = kWh)
        forecast = self.get_forecast(hass)
        if not forecast:
            return None
        return sum(float(f.get("pv_estimate", 0)) for f in forecast) * 0.5
