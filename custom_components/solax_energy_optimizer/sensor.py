"""Sensor platform for Solax Energy Optimizer."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_BATTERY_SOC,
    ATTR_CURRENT_PRICE,
    ATTR_DRY_RUN_MODE,
    DOMAIN,
    ENTITY_DAILY_COST,
    ENTITY_DAILY_SAVINGS,
    ENTITY_DECISION_REASON,
    ENTITY_LAST_ACTION_TIME,
    ENTITY_MONTHLY_COST,
    ENTITY_MONTHLY_SAVINGS,
    ENTITY_NEXT_ACTION,
    ENTITY_NEXT_UPDATE_TIME,
    ENTITY_UPDATE_COUNT,
)
from .coordinator import EnergyOptimizerCoordinator, EnergyOptimizerData
from . import EnergyOptimizerConfigEntry


@dataclass(frozen=True, kw_only=True)
class EnergyOptimizerSensorDescription(SensorEntityDescription):
    """Describes Energy Optimizer sensor entity."""

    value_fn: Callable[[EnergyOptimizerData], str | float | datetime | None]


SENSORS: tuple[EnergyOptimizerSensorDescription, ...] = (
    EnergyOptimizerSensorDescription(
        key=ENTITY_NEXT_ACTION,
        translation_key="next_action",
        name="Next action",
        icon="mdi:flash-auto",
        value_fn=lambda data: data.next_action,
    ),
    EnergyOptimizerSensorDescription(
        key=ENTITY_LAST_ACTION_TIME,
        translation_key="last_action_time",
        name="Last action time",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.last_action_time,
    ),
    EnergyOptimizerSensorDescription(
        key=ENTITY_NEXT_UPDATE_TIME,
        translation_key="next_update_time",
        name="Next update time",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.next_update_time,
    ),
    EnergyOptimizerSensorDescription(
        key=ENTITY_DAILY_COST,
        translation_key="daily_cost",
        name="Daily cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: round(data.daily_cost, 2),
    ),
    EnergyOptimizerSensorDescription(
        key=ENTITY_DAILY_SAVINGS,
        translation_key="daily_savings",
        name="Daily savings",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:piggy-bank",
        value_fn=lambda data: round(data.daily_savings, 2),
    ),
    EnergyOptimizerSensorDescription(
        key=ENTITY_MONTHLY_COST,
        translation_key="monthly_cost",
        name="Monthly cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: round(data.monthly_cost, 2),
    ),
    EnergyOptimizerSensorDescription(
        key=ENTITY_MONTHLY_SAVINGS,
        translation_key="monthly_savings",
        name="Monthly savings",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:piggy-bank",
        value_fn=lambda data: round(data.monthly_savings, 2),
    ),
    EnergyOptimizerSensorDescription(
        key=ENTITY_DECISION_REASON,
        translation_key="decision_reason",
        name="Decision reason",
        icon="mdi:comment-question",
        value_fn=lambda data: data.decision_reason,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EnergyOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator = entry.runtime_data

    entities: list[SensorEntity] = [
        EnergyOptimizerSensor(coordinator, description, entry)
        for description in SENSORS
    ]
    entities.append(UpdateCountSensor(coordinator, entry))
    async_add_entities(entities)


class EnergyOptimizerSensor(
    CoordinatorEntity[EnergyOptimizerCoordinator], SensorEntity
):
    """Representation of an Energy Optimizer sensor."""

    entity_description: EnergyOptimizerSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        description: EnergyOptimizerSensorDescription,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def native_value(self) -> str | float | datetime | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.entity_description.key == ENTITY_NEXT_ACTION:
            return {
                ATTR_BATTERY_SOC: self.coordinator.data.battery_soc,
                ATTR_CURRENT_PRICE: self.coordinator.data.current_price,
                "target_soc": self.coordinator.data.target_soc,
                "strategy": self.coordinator.current_strategy,
                ATTR_DRY_RUN_MODE: self.coordinator.dry_run_mode,
            }
        if self.entity_description.key == ENTITY_DECISION_REASON:
            return {
                ATTR_BATTERY_SOC: self.coordinator.data.battery_soc,
                ATTR_CURRENT_PRICE: self.coordinator.data.current_price,
                "target_soc": self.coordinator.data.target_soc,
                "strategy": self.coordinator.current_strategy,
                "update_count": self.coordinator.update_count,
                "last_action_time": self.coordinator.data.last_action_time,
            }
        return {}


class UpdateCountSensor(CoordinatorEntity[EnergyOptimizerCoordinator], SensorEntity):
    """Sensor that counts how many update cycles have completed."""

    _attr_has_entity_name = True
    _attr_name = "Update count"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = None

    def __init__(
        self,
        coordinator: EnergyOptimizerCoordinator,
        entry: EnergyOptimizerConfigEntry,
    ) -> None:
        """Initialize the update count sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_UPDATE_COUNT}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def native_value(self) -> int:
        """Return the number of completed update cycles."""
        return self.coordinator.update_count
