"""Number platform for Solax Energy Optimizer."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EnergyOptimizerConfigEntry
from .const import (
    CONF_MAX_SOC,
    CONF_MIN_SOC,
    DEFAULT_MAX_SOC,
    DEFAULT_MIN_SOC,
    DOMAIN,
    ENTITY_MAX_SOC,
    ENTITY_MIN_SOC,
)
from .coordinator import EnergyOptimizerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EnergyOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number platform."""
    coordinator = entry.runtime_data
    async_add_entities([
        MinSocNumber(coordinator, entry),
        MaxSocNumber(coordinator, entry),
    ])


class MinSocNumber(CoordinatorEntity[EnergyOptimizerCoordinator], NumberEntity):
    """Minimum state of charge control."""

    _attr_has_entity_name = True
    _attr_name = "Minimum SOC"
    _attr_icon = "mdi:battery-low"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_MIN_SOC}"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def native_value(self) -> float:
        """Return current minimum SOC."""
        return self.coordinator.min_soc

    async def async_set_native_value(self, value: float) -> None:
        """Set new minimum SOC."""
        self.coordinator.set_min_soc(value)
        self.async_write_ha_state()


class MaxSocNumber(CoordinatorEntity[EnergyOptimizerCoordinator], NumberEntity):
    """Maximum state of charge control."""

    _attr_has_entity_name = True
    _attr_name = "Maximum SOC"
    _attr_icon = "mdi:battery-high"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_MAX_SOC}"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def native_value(self) -> float:
        """Return current maximum SOC."""
        return self.coordinator.max_soc

    async def async_set_native_value(self, value: float) -> None:
        """Set new maximum SOC."""
        self.coordinator.set_max_soc(value)
        self.async_write_ha_state()
