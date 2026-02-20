"""Abstract base classes for provider adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from homeassistant.core import HomeAssistant


class InverterAdapter(ABC):
    """Abstract base for any inverter / battery SOC source."""

    @abstractmethod
    def get_battery_soc(self, hass: HomeAssistant) -> float | None:
        """Return the current battery State-of-Charge as a float in [0, 100].

        Return None if the source entity is unavailable or the value cannot
        be parsed.
        """

    @property
    @abstractmethod
    def source_entity_id(self) -> str:
        """Return the HA entity ID this adapter reads from."""


class SolarForecastAdapter(ABC):
    """Abstract base for any solar forecast source."""

    @abstractmethod
    def get_forecast(self, hass: HomeAssistant) -> list[dict]:
        """Return a list of normalized forecast periods.

        Each dict MUST contain:
          "period_start": datetime   (timezone-aware)
          "pv_estimate":  float      (kW, average over the period)
        """

    @abstractmethod
    def get_solar_today(self, hass: HomeAssistant) -> float | None:
        """Return total expected solar production today in kWh.

        Return None if unavailable.
        """

    @property
    @abstractmethod
    def source_entity_id(self) -> str:
        """Return the HA entity ID this adapter reads from."""


class PriceAdapter(ABC):
    """Abstract base for any electricity price source."""

    @abstractmethod
    def get_prices(self, hass: HomeAssistant) -> list[dict]:
        """Return a list of normalized price periods.

        Each dict MUST contain:
          "from":  datetime   (timezone-aware, period start)
          "price": float      (currency/kWh)
        """

    @abstractmethod
    def get_current_price(self, hass: HomeAssistant) -> float | None:
        """Return the current spot price.

        Return None if unavailable.
        """

    @property
    @abstractmethod
    def source_entity_id(self) -> str:
        """Return the HA entity ID this adapter reads from."""
