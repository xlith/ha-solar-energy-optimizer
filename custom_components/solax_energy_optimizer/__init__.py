"""The Solax Energy Optimizer integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import EnergyOptimizerCoordinator

type EnergyOptimizerConfigEntry = ConfigEntry[EnergyOptimizerCoordinator]

_LOGGER = logging.getLogger(__name__)

SERVICE_TRIGGER_OPTIMIZATION = "trigger_optimization"

PLATFORMS: list[str] = [
    "sensor",
    "switch",
    "select",
]


async def async_setup_entry(
    hass: HomeAssistant, entry: EnergyOptimizerConfigEntry
) -> bool:
    """Set up Solax Energy Optimizer from a config entry."""
    _LOGGER.info("Setting up Solax Energy Optimizer (entry_id=%s)", entry.entry_id)
    _LOGGER.info(
        "Configured entities - inverter: %s, solcast: %s, electricity_prices: %s",
        entry.data.get("solax_inverter_entity"),
        entry.data.get("solcast_entity"),
        entry.data.get("frank_energie_entity"),
    )

    coordinator = EnergyOptimizerCoordinator(hass, entry)
    _LOGGER.info("Coordinator created, fetching initial data")

    await coordinator.async_config_entry_first_refresh()
    _LOGGER.info("Initial data fetch complete")

    entry.runtime_data = coordinator

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
    _LOGGER.info("Platforms set up: %s", PLATFORMS)

    async def handle_trigger_optimization(call: ServiceCall) -> None:
        """Handle trigger optimization service call."""
        _LOGGER.info("Manual optimization triggered via service call")
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_TRIGGER_OPTIMIZATION,
        handle_trigger_optimization,
    )

    _LOGGER.info("Solax Energy Optimizer setup complete")
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: EnergyOptimizerConfigEntry
) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Solax Energy Optimizer (entry_id=%s)", entry.entry_id)
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    _LOGGER.info("Unload result: %s", result)
    return result
