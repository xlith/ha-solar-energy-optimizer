"""Shared pytest fixtures for Solar Energy Optimizer tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class MockState:
    """Minimal stand-in for a Home Assistant State object."""

    def __init__(self, state: str, attributes: dict | None = None) -> None:
        self.state = state
        self.attributes = attributes or {}


class MockHass:
    """Minimal stand-in for homeassistant.core.HomeAssistant.

    Only implements hass.states.get() which is the sole HA API used by
    all provider adapters.
    """

    def __init__(self) -> None:
        self._states: dict[str, MockState] = {}
        self.states = MagicMock()
        self.states.get = self._states_get

    def set_state(
        self,
        entity_id: str,
        state: str,
        attributes: dict | None = None,
    ) -> None:
        """Register a mock entity state."""
        self._states[entity_id] = MockState(state, attributes)

    def _states_get(self, entity_id: str) -> MockState | None:
        return self._states.get(entity_id)


@pytest.fixture
def hass() -> MockHass:
    """Return a fresh MockHass instance for each test."""
    return MockHass()
