"""Select platform for Solax Energy Optimizer."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_CURRENT_STRATEGY, STRATEGIES
from .coordinator import EnergyOptimizerCoordinator

if TYPE_CHECKING:
    from . import EnergyOptimizerConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EnergyOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select platform."""
    coordinator = entry.runtime_data

    async_add_entities([StrategySelect(coordinator, entry)])


class StrategySelect(CoordinatorEntity[EnergyOptimizerCoordinator], SelectEntity):
    """Select entity for choosing optimization strategy."""

    _attr_has_entity_name = True
    _attr_translation_key = "strategy"
    _attr_icon = "mdi:strategy"
    _attr_options = STRATEGIES

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_CURRENT_STRATEGY}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Solax Energy Optimizer",
        }

    @property
    def current_option(self) -> str:
        """Return the current strategy."""
        return self.coordinator.current_strategy

    async def async_select_option(self, option: str) -> None:
        """Change the strategy."""
        self.coordinator.set_strategy(option)
        await self.coordinator.async_request_refresh()
