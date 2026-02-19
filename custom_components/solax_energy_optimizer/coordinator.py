"""Data update coordinator for Solax Energy Optimizer."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from .const import (
    ACTION_CHARGE,
    ACTION_DISCHARGE,
    ACTION_IDLE,
    CONF_FRANK_ENERGIE_ENTITY,
    CONF_MAX_SOC,
    CONF_MIN_SOC,
    CONF_SOLCAST_ENTITY,
    CONF_SOLAX_INVERTER_ENTITY,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    STRATEGY_BALANCED,
    STRATEGY_GRID_INDEPENDENCE,
    STRATEGY_MAXIMIZE_SELF_CONSUMPTION,
    STRATEGY_MINIMIZE_COST,
)

_LOGGER = logging.getLogger(__name__)


class EnergyOptimizerData:
    """Data class for energy optimizer."""

    def __init__(self) -> None:
        """Initialize data."""
        self.battery_soc: float | None = None
        self.solar_production: float | None = None
        self.current_price: float | None = None
        self.prices_today: list[dict[str, Any]] = []
        self.prices_tomorrow: list[dict[str, Any]] = []
        self.solar_forecast: list[dict[str, Any]] = []
        self.next_action: str = ACTION_IDLE
        self.next_action_time: datetime | None = None
        self.target_soc: float | None = None
        self.daily_cost: float = 0.0
        self.daily_savings: float = 0.0
        self.monthly_cost: float = 0.0
        self.monthly_savings: float = 0.0


class EnergyOptimizerCoordinator(DataUpdateCoordinator[EnergyOptimizerData]):
    """Class to manage fetching data and running optimization."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.config_entry = entry
        self._current_strategy = STRATEGY_MINIMIZE_COST
        self._automation_enabled = True
        self._manual_override = False
        self._dry_run_mode = True  # Default to dry run for safety

    @property
    def current_strategy(self) -> str:
        """Return current optimization strategy."""
        return self._current_strategy

    def set_strategy(self, strategy: str) -> None:
        """Set optimization strategy."""
        self._current_strategy = strategy
        _LOGGER.info("Strategy changed to: %s", strategy)

    @property
    def automation_enabled(self) -> bool:
        """Return automation enabled state."""
        return self._automation_enabled

    def set_automation_enabled(self, enabled: bool) -> None:
        """Set automation enabled state."""
        self._automation_enabled = enabled
        _LOGGER.info("Automation enabled: %s", enabled)

    @property
    def manual_override(self) -> bool:
        """Return manual override state."""
        return self._manual_override

    def set_manual_override(self, override: bool) -> None:
        """Set manual override state."""
        self._manual_override = override
        _LOGGER.info("Manual override: %s", override)

    @property
    def dry_run_mode(self) -> bool:
        """Return dry run mode state."""
        return self._dry_run_mode

    def set_dry_run_mode(self, dry_run: bool) -> None:
        """Set dry run mode state."""
        self._dry_run_mode = dry_run
        _LOGGER.info("Dry run mode: %s", dry_run)

    async def _async_update_data(self) -> EnergyOptimizerData:
        """Fetch data from dependencies and run optimization."""
        _LOGGER.debug("Starting data update cycle")
        try:
            data = EnergyOptimizerData()

            # Get battery SOC
            inverter_entity = self.config_entry.data[CONF_SOLAX_INVERTER_ENTITY]
            inverter_state = self.hass.states.get(inverter_entity)
            if inverter_state:
                try:
                    state_value = inverter_state.state
                    _LOGGER.debug("Battery SOC entity %s has state: %s (type: %s)", inverter_entity, state_value, type(state_value))

                    # Skip unavailable/unknown states
                    if state_value in ("unavailable", "unknown", None, ""):
                        _LOGGER.warning("Battery SOC entity %s is unavailable", inverter_entity)
                    else:
                        data.battery_soc = float(state_value)
                except (ValueError, TypeError) as e:
                    _LOGGER.error(
                        "Could not parse battery SOC from %s: state='%s', type=%s, error=%s",
                        inverter_entity,
                        inverter_state.state,
                        type(inverter_state.state).__name__,
                        str(e),
                    )
            else:
                _LOGGER.warning("Battery SOC entity %s not found", inverter_entity)

            # Get solar forecast
            solcast_entity = self.config_entry.data[CONF_SOLCAST_ENTITY]
            solcast_state = self.hass.states.get(solcast_entity)
            if solcast_state and solcast_state.attributes:
                # Extract forecast data from attributes
                data.solar_forecast = solcast_state.attributes.get("forecasts", [])

            # Get energy prices
            frank_entity = self.config_entry.data[CONF_FRANK_ENERGIE_ENTITY]
            _LOGGER.debug("Looking for Frank Energie entity: %s", frank_entity)

            frank_state = self.hass.states.get(frank_entity)
            if frank_state:
                _LOGGER.debug("Frank Energie entity found, state: %s", frank_state.state)
                _LOGGER.debug("Frank Energie attributes keys: %s", list(frank_state.attributes.keys()) if frank_state.attributes else "No attributes")

                try:
                    data.current_price = float(frank_state.state)
                    _LOGGER.debug("Current price set to: %s", data.current_price)
                except (ValueError, TypeError) as e:
                    _LOGGER.warning("Could not parse current price from %s: %s", frank_entity, str(e))

                if frank_state.attributes:
                    # Extract price data from attributes
                    prices_raw = frank_state.attributes.get("prices", [])
                    _LOGGER.info(
                        "Frank Energie prices - type: %s, count: %s",
                        type(prices_raw).__name__,
                        len(prices_raw) if isinstance(prices_raw, list) else "N/A",
                    )
                    if isinstance(prices_raw, list) and len(prices_raw) > 0:
                        _LOGGER.debug("Sample price entry: %s", prices_raw[0])
                    data.prices_today = prices_raw
                else:
                    _LOGGER.warning("Frank Energie entity has no attributes")
            else:
                _LOGGER.error("Frank Energie entity not found: %s", frank_entity)

            # Log current state before optimization
            _LOGGER.debug(
                "Optimization state - Automation: %s, Manual override: %s, Dry run: %s",
                self._automation_enabled,
                self._manual_override,
                self._dry_run_mode,
            )

            # Run optimization if automation is enabled and not in manual override
            if self._automation_enabled and not self._manual_override:
                self._run_optimization(data)

                # Log dry run status
                if self._dry_run_mode:
                    _LOGGER.info(
                        "DRY RUN MODE: Would execute %s (target SOC: %s%%)",
                        data.next_action,
                        data.target_soc,
                    )
                else:
                    # In production mode, would call inverter control here
                    _LOGGER.info(
                        "PRODUCTION MODE: Executing %s (target SOC: %s%%)",
                        data.next_action,
                        data.target_soc,
                    )
            else:
                _LOGGER.debug(
                    "Optimization skipped - Automation enabled: %s, Manual override: %s",
                    self._automation_enabled,
                    self._manual_override,
                )
                    # TODO: Implement actual inverter control
                    # await self._execute_action(data.next_action, data.target_soc)

            return data

        except Exception as err:
            _LOGGER.error(
                "Error in _async_update_data: %s (type: %s)",
                str(err),
                type(err).__name__,
                exc_info=True,
            )
            raise UpdateFailed(f"Error fetching data: {err}") from err

    def _run_optimization(self, data: EnergyOptimizerData) -> None:
        """Run optimization algorithm based on current strategy."""
        _LOGGER.info("Running optimization with strategy: %s", self._current_strategy)

        if self._current_strategy == STRATEGY_MINIMIZE_COST:
            self._optimize_minimize_cost(data)
        elif self._current_strategy == STRATEGY_MAXIMIZE_SELF_CONSUMPTION:
            self._optimize_maximize_self_consumption(data)
        elif self._current_strategy == STRATEGY_GRID_INDEPENDENCE:
            self._optimize_grid_independence(data)

        elif self._current_strategy == STRATEGY_BALANCED:
            self._optimize_balanced(data)

        _LOGGER.info(
            "Optimization complete - Action: %s, Target SOC: %s%%, Next action time: %s",
            data.next_action,
            data.target_soc,
            data.next_action_time,
        )

    def _optimize_minimize_cost(self, data: EnergyOptimizerData) -> None:
        """Optimize to minimize energy costs."""
        # Find lowest and highest prices in the next 24 hours
        if not data.prices_today:
            _LOGGER.warning("No price data available - setting action to idle")
            data.next_action = ACTION_IDLE
            return

        # Debug log the price data structure
        _LOGGER.debug("Price data available: %d entries", len(data.prices_today))
        _LOGGER.debug("Price data structure: %s", data.prices_today[:2] if len(data.prices_today) >= 2 else data.prices_today)

        current_hour = datetime.now().hour
        prices_ahead = []
        for p in data.prices_today:
            try:
                if not isinstance(p, dict):
                    _LOGGER.warning("Expected dict in prices_today, got %s: %s", type(p).__name__, p)
                    continue
                time_from = p.get("from", "")
                parsed_time = self._parse_time(time_from)
                if parsed_time.hour >= current_hour:
                    prices_ahead.append(p)
            except Exception as e:
                _LOGGER.error("Error processing price entry %s: %s", p, str(e), exc_info=True)
                continue

        if not prices_ahead:
            _LOGGER.warning("No future prices found - setting action to idle")
            data.next_action = ACTION_IDLE
            return

        _LOGGER.debug("Found %d future price entries", len(prices_ahead))

        # Sort by price
        prices_sorted = sorted(prices_ahead, key=lambda x: float(x.get("price", 0)))
        lowest_price = prices_sorted[0] if prices_sorted else None
        highest_price = prices_sorted[-1] if prices_sorted else None

        if not lowest_price or not highest_price:
            _LOGGER.warning("Could not determine price range - setting action to idle")
            data.next_action = ACTION_IDLE
            return

        current_price = data.current_price or 0
        min_soc = float(self.config_entry.data.get(CONF_MIN_SOC, 20))
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        # Calculate price thresholds (bottom 25% and top 25%)
        try:
            lowest_price_val = float(lowest_price.get("price", 0))
            highest_price_val = float(highest_price.get("price", 0))
        except (AttributeError, TypeError, ValueError) as e:
            _LOGGER.error(
                "Error accessing price values: lowest_price=%s, highest_price=%s, error=%s",
                lowest_price,
                highest_price,
                str(e),
            )
            data.next_action = ACTION_IDLE
            return

        price_range = highest_price_val - lowest_price_val
        low_threshold = lowest_price_val + (price_range * 0.25)
        high_threshold = highest_price_val - (price_range * 0.25)

        _LOGGER.info(
            "Price analysis - Current: %.2f, Range: %.2f to %.2f, Low threshold: %.2f, High threshold: %.2f",
            current_price,
            lowest_price_val,
            highest_price_val,
            low_threshold,
            high_threshold,
        )

        _LOGGER.info(
            "Battery state - SOC: %s%%, Min: %s%%, Max: %s%%",
            data.battery_soc,
            min_soc,
            max_soc,
        )

        # Decision logic
        if current_price <= low_threshold and data.battery_soc and data.battery_soc < max_soc:
            # Charge when price is low
            data.next_action = ACTION_CHARGE
            data.target_soc = max_soc
            data.next_action_time = datetime.now()
            _LOGGER.info("Decision: CHARGE (price %.2f <= low threshold %.2f, SOC %s%% < max %s%%)",
                        current_price, low_threshold, data.battery_soc, max_soc)
        elif current_price >= high_threshold and data.battery_soc and data.battery_soc > min_soc:
            # Discharge when price is high
            data.next_action = ACTION_DISCHARGE
            data.target_soc = min_soc
            data.next_action_time = datetime.now()
            _LOGGER.info("Decision: DISCHARGE (price %.2f >= high threshold %.2f, SOC %s%% > min %s%%)",
                        current_price, high_threshold, data.battery_soc, min_soc)
        else:
            # Idle in moderate price range
            data.next_action = ACTION_IDLE
            _LOGGER.info("Decision: IDLE (price in moderate range or battery constraints not met)")

    def _optimize_maximize_self_consumption(self, data: EnergyOptimizerData) -> None:
        """Optimize to maximize self-consumption of solar energy."""
        # Check if there's solar production forecast
        if not data.solar_forecast:
            data.next_action = ACTION_IDLE
            return

        current_time = datetime.now()
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        # Find next significant solar production period
        next_solar_period = None
        for forecast in data.solar_forecast:
            forecast_time = self._parse_time(forecast.get("period_end", ""))
            if forecast_time > current_time and forecast.get("pv_estimate", 0) > 1.0:
                next_solar_period = forecast
                break

        if next_solar_period:
            # If solar production is expected, ensure battery has space
            if data.battery_soc and data.battery_soc > max_soc - 20:
                data.next_action = ACTION_DISCHARGE
                data.target_soc = max_soc - 20
            else:
                data.next_action = ACTION_IDLE
        else:
            # No solar expected, maintain current state
            data.next_action = ACTION_IDLE

    def _optimize_grid_independence(self, data: EnergyOptimizerData) -> None:
        """Optimize for grid independence."""
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        # Always try to keep battery charged when solar is available
        if data.battery_soc:
            if data.battery_soc < max_soc:
                data.next_action = ACTION_CHARGE
                data.target_soc = max_soc
            else:
                data.next_action = ACTION_IDLE
        else:
            data.next_action = ACTION_IDLE

    def _optimize_balanced(self, data: EnergyOptimizerData) -> None:
        """Optimize with a balanced approach."""
        # Combine cost optimization with self-consumption
        # Simplified: charge during low prices or high solar, discharge during high prices
        min_soc = float(self.config_entry.data.get(CONF_MIN_SOC, 20))
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        if not data.prices_today:
            data.next_action = ACTION_IDLE
            return

        current_hour = datetime.now().hour
        prices_ahead = [p for p in data.prices_today if self._parse_time(p.get("from", "")).hour >= current_hour]

        if not prices_ahead:
            data.next_action = ACTION_IDLE
            return

        avg_price = sum(float(p.get("price", 0)) for p in prices_ahead) / len(prices_ahead)
        current_price = data.current_price or 0

        if current_price < avg_price * 0.9 and data.battery_soc and data.battery_soc < max_soc:
            data.next_action = ACTION_CHARGE
            data.target_soc = max_soc
        elif current_price > avg_price * 1.1 and data.battery_soc and data.battery_soc > min_soc:
            data.next_action = ACTION_DISCHARGE
            data.target_soc = min_soc
        else:
            data.next_action = ACTION_IDLE

    def _parse_time(self, time_str: str | datetime) -> datetime:
        """Parse time string or datetime to datetime."""
        try:
            # If already a datetime object, return it directly
            if isinstance(time_str, datetime):
                return time_str

            # If it's a string, parse it
            if isinstance(time_str, str):
                return datetime.fromisoformat(time_str.replace("Z", "+00:00"))

            # If neither string nor datetime, log and return current time
            _LOGGER.warning("Expected string or datetime for time parsing, got %s: %s", type(time_str).__name__, time_str)
            return datetime.now()
        except (ValueError, AttributeError, TypeError) as e:
            _LOGGER.warning("Could not parse time '%s': %s", time_str, str(e))
            return datetime.now()
