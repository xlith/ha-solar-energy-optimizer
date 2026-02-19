"""Switch platform for Solax Energy Optimizer."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_AUTOMATION_ENABLED, ENTITY_MANUAL_OVERRIDE, ENTITY_DRY_RUN
from .coordinator import EnergyOptimizerCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import EnergyOptimizerConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EnergyOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform."""
    coordinator = entry.runtime_data

    async_add_entities(
        [
            AutomationEnabledSwitch(coordinator, entry),
            ManualOverrideSwitch(coordinator, entry),
            DryRunSwitch(coordinator, entry),
        ]
    )


class AutomationEnabledSwitch(
    CoordinatorEntity[EnergyOptimizerCoordinator], SwitchEntity
):
    """Switch to enable/disable automation."""

    _attr_has_entity_name = True
    _attr_translation_key = "automation_enabled"
    _attr_icon = "mdi:auto-mode"

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_AUTOMATION_ENABLED}"
        self._attr_name = "Automation enabled"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def is_on(self) -> bool:
        """Return true if automation is enabled."""
        return self.coordinator.automation_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on automation."""
        self.coordinator.set_automation_enabled(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off automation."""
        self.coordinator.set_automation_enabled(False)
        await self.coordinator.async_request_refresh()


class ManualOverrideSwitch(
    CoordinatorEntity[EnergyOptimizerCoordinator], SwitchEntity
):
    """Switch to enable/disable manual override."""

    _attr_has_entity_name = True
    _attr_translation_key = "manual_override"
    _attr_icon = "mdi:hand-back-right"

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_MANUAL_OVERRIDE}"
        self._attr_name = "Manual override"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def is_on(self) -> bool:
        """Return true if manual override is enabled."""
        return self.coordinator.manual_override

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on manual override."""
        self.coordinator.set_manual_override(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off manual override."""
        self.coordinator.set_manual_override(False)
        await self.coordinator.async_request_refresh()


class DryRunSwitch(CoordinatorEntity[EnergyOptimizerCoordinator], SwitchEntity):
    """Switch to enable/disable dry run mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "dry_run"
    _attr_icon = "mdi:test-tube"

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_DRY_RUN}"
        self._attr_name = "Dry run mode"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def is_on(self) -> bool:
        """Return true if dry run mode is enabled."""
        return self.coordinator.dry_run_mode

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on dry run mode."""
        self.coordinator.set_dry_run_mode(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off dry run mode."""
        self.coordinator.set_dry_run_mode(False)
        await self.coordinator.async_request_refresh()
