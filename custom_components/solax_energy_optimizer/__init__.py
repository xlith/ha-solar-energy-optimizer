"""The Solax Energy Optimizer integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import Platform
    from homeassistant.core import HomeAssistant, ServiceCall

    from .coordinator import EnergyOptimizerCoordinator

    type EnergyOptimizerConfigEntry = ConfigEntry[EnergyOptimizerCoordinator]

_LOGGER = logging.getLogger(__name__)

SERVICE_TRIGGER_OPTIMIZATION = "trigger_optimization"

PLATFORMS: list[Platform] = [
    "sensor",
    "switch",
    "select",
]


async def async_setup_entry(
    hass: HomeAssistant, entry: EnergyOptimizerConfigEntry
) -> bool:
    """Set up Solax Energy Optimizer from a config entry."""
    import asyncio
    import logging
    from .coordinator import EnergyOptimizerCoordinator
    from .const import (
        CONF_SOLAX_INVERTER_ENTITY,
        CONF_FRANK_ENERGIE_ENTITY,
        CONF_SOLCAST_ENTITY,
    )

    _LOGGER = logging.getLogger(__name__)

    # Wait for dependent entities to be available (max 30 seconds)
    required_entities = [
        entry.data.get(CONF_SOLAX_INVERTER_ENTITY),
        entry.data.get(CONF_FRANK_ENERGIE_ENTITY),
        entry.data.get(CONF_SOLCAST_ENTITY),
    ]

    _LOGGER.info("Waiting for required entities to be available: %s", required_entities)

    for attempt in range(15):  # 15 attempts x 2 seconds = 30 seconds max
        missing = [entity for entity in required_entities if entity and not hass.states.get(entity)]
        if not missing:
            _LOGGER.info("All required entities are available")
            break
        _LOGGER.debug("Waiting for entities (attempt %d/15): %s", attempt + 1, missing)
        await asyncio.sleep(2)
    else:
        _LOGGER.warning(
            "Some entities are still not available after 30 seconds: %s. Integration will continue but may have errors.",
            missing
        )

    coordinator = EnergyOptimizerCoordinator(hass, entry)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Register device
    from homeassistant.helpers import device_registry as dr

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
