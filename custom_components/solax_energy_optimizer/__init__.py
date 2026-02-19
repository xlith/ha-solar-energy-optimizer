"""The Solax Energy Optimizer integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import EnergyOptimizerCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

    type EnergyOptimizerConfigEntry = ConfigEntry[EnergyOptimizerCoordinator]

_LOGGER = logging.getLogger(__name__)

SERVICE_TRIGGER_OPTIMIZATION = "trigger_optimization"

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: EnergyOptimizerConfigEntry
) -> bool:
    """Set up Solax Energy Optimizer from a config entry."""
    coordinator = EnergyOptimizerCoordinator(hass, entry)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Register device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="Solax Energy Optimizer",
        manufacturer="Custom",
        model="Energy Optimizer",
        entry_type=dr.DeviceEntryType.SERVICE,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_trigger_optimization(call: ServiceCall) -> None:
        """Handle trigger optimization service call."""
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_TRIGGER_OPTIMIZATION,
        handle_trigger_optimization,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: EnergyOptimizerConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
