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
        _LOGGER.info("--- Update cycle start ---")
        try:
            data = EnergyOptimizerData()

            # --- Battery SOC ---
            inverter_entity = self.config_entry.data[CONF_SOLAX_INVERTER_ENTITY]
            inverter_state = self.hass.states.get(inverter_entity)
            if inverter_state is None:
                _LOGGER.info("[battery] %s: not yet in HA state machine", inverter_entity)
            elif inverter_state.state in ("unavailable", "unknown", None, ""):
                _LOGGER.info("[battery] %s: state=%s (unavailable/unknown)", inverter_entity, inverter_state.state)
            else:
                try:
                    data.battery_soc = float(inverter_state.state)
                    _LOGGER.info("[battery] %s: SOC=%.1f%%", inverter_entity, data.battery_soc)
                except (ValueError, TypeError) as e:
                    _LOGGER.error(
                        "[battery] %s: could not parse state='%s' as float: %s",
                        inverter_entity,
                        inverter_state.state,
                        e,
                    )

            # --- Solar forecast ---
            solcast_entity = self.config_entry.data[CONF_SOLCAST_ENTITY]
            solcast_state = self.hass.states.get(solcast_entity)
            if solcast_state is None:
                _LOGGER.info("[solcast] %s: not yet in HA state machine", solcast_entity)
            elif solcast_state.attributes:
                forecasts = solcast_state.attributes.get("forecasts", [])
                data.solar_forecast = forecasts
                _LOGGER.info("[solcast] %s: state=%s, %d forecast entries", solcast_entity, solcast_state.state, len(forecasts))
            else:
                _LOGGER.info("[solcast] %s: state=%s, no attributes", solcast_entity, solcast_state.state)

            # --- Energy prices ---
            frank_entity = self.config_entry.data[CONF_FRANK_ENERGIE_ENTITY]
            frank_state = self.hass.states.get(frank_entity)
            if frank_state is None:
                _LOGGER.info("[frank] %s: not yet in HA state machine", frank_entity)
            else:
                try:
                    data.current_price = float(frank_state.state)
                    _LOGGER.info("[frank] %s: current_price=%.4f", frank_entity, data.current_price)
                except (ValueError, TypeError) as e:
                    _LOGGER.warning("[frank] %s: could not parse state='%s' as float: %s", frank_entity, frank_state.state, e)

                if frank_state.attributes:
                    prices_raw = frank_state.attributes.get("prices", [])
                    price_count = len(prices_raw) if isinstance(prices_raw, list) else "N/A"
                    _LOGGER.info("[frank] %s: %s price entries in attributes", frank_entity, price_count)
                    data.prices_today = prices_raw if isinstance(prices_raw, list) else []
                else:
                    _LOGGER.warning("[frank] %s: entity has no attributes", frank_entity)

            # --- Optimization ---
            _LOGGER.info(
                "[optimizer] strategy=%s, automation=%s, manual_override=%s, dry_run=%s",
                self._current_strategy,
                self._automation_enabled,
                self._manual_override,
                self._dry_run_mode,
            )

            if self._automation_enabled and not self._manual_override:
                self._run_optimization(data)
                mode = "DRY RUN" if self._dry_run_mode else "LIVE"
                _LOGGER.info(
                    "[optimizer] %s: action=%s, target_soc=%s%%",
                    mode,
                    data.next_action,
                    data.target_soc,
                )
            else:
                _LOGGER.info("[optimizer] skipped (automation=%s, manual_override=%s)", self._automation_enabled, self._manual_override)

            _LOGGER.info("--- Update cycle end ---")
            return data

        except Exception as err:
            _LOGGER.error("Update cycle failed: %s (%s)", err, type(err).__name__, exc_info=True)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    def _run_optimization(self, data: EnergyOptimizerData) -> None:
        """Run optimization algorithm based on current strategy."""
        _LOGGER.info("[optimizer] running strategy: %s", self._current_strategy)

        if self._current_strategy == STRATEGY_MINIMIZE_COST:
            self._optimize_minimize_cost(data)
        elif self._current_strategy == STRATEGY_MAXIMIZE_SELF_CONSUMPTION:
            self._optimize_maximize_self_consumption(data)
        elif self._current_strategy == STRATEGY_GRID_INDEPENDENCE:
            self._optimize_grid_independence(data)
        elif self._current_strategy == STRATEGY_BALANCED:
            self._optimize_balanced(data)

        _LOGGER.info(
            "[optimizer] result: action=%s, target_soc=%s%%, next_action_time=%s",
            data.next_action,
            data.target_soc,
            data.next_action_time,
        )

    def _optimize_minimize_cost(self, data: EnergyOptimizerData) -> None:
        """Optimize to minimize energy costs."""
        if not data.prices_today:
            _LOGGER.info("[minimize_cost] no price data, action=idle")
            data.next_action = ACTION_IDLE
            return

        current_time = datetime.now()
        prices_ahead = []
        for p in data.prices_today:
            try:
                if not isinstance(p, dict):
                    _LOGGER.warning("[minimize_cost] unexpected price entry type %s: %s", type(p).__name__, p)
                    continue
                parsed_naive = self._parse_time(p.get("from", "")).replace(tzinfo=None)
                current_naive = current_time.replace(tzinfo=None)
                if parsed_naive >= current_naive:
                    prices_ahead.append(p)
            except Exception as e:
                _LOGGER.error("[minimize_cost] error processing price entry %s: %s", p, e, exc_info=True)

        if not prices_ahead:
            _LOGGER.info("[minimize_cost] no future prices found, action=idle")
            data.next_action = ACTION_IDLE
            return

        prices_sorted = sorted(prices_ahead, key=lambda x: float(x.get("price", 0)))
        lowest_price = prices_sorted[0]
        highest_price = prices_sorted[-1]

        try:
            lowest_price_val = float(lowest_price.get("price", 0))
            highest_price_val = float(highest_price.get("price", 0))
        except (AttributeError, TypeError, ValueError) as e:
            _LOGGER.error("[minimize_cost] could not read price values: %s", e)
            data.next_action = ACTION_IDLE
            return

        price_range = highest_price_val - lowest_price_val
        low_threshold = lowest_price_val + (price_range * 0.25)
        high_threshold = highest_price_val - (price_range * 0.25)
        current_price = data.current_price or 0
        min_soc = float(self.config_entry.data.get(CONF_MIN_SOC, 20))
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        _LOGGER.info(
            "[minimize_cost] price: current=%.4f, range=[%.4f, %.4f], thresholds=[%.4f, %.4f] | soc=%.1f%%, limits=[%.0f%%, %.0f%%]",
            current_price,
            lowest_price_val,
            highest_price_val,
            low_threshold,
            high_threshold,
            data.battery_soc if data.battery_soc is not None else -1,
            min_soc,
            max_soc,
        )

        if current_price <= low_threshold and data.battery_soc is not None and data.battery_soc < max_soc:
            data.next_action = ACTION_CHARGE
            data.target_soc = max_soc
            data.next_action_time = datetime.now()
            _LOGGER.info("[minimize_cost] decision=CHARGE (price %.4f <= low_threshold %.4f, soc %.1f%% < max %.0f%%)",
                         current_price, low_threshold, data.battery_soc, max_soc)
        elif current_price >= high_threshold and data.battery_soc is not None and data.battery_soc > min_soc:
            data.next_action = ACTION_DISCHARGE
            data.target_soc = min_soc
            data.next_action_time = datetime.now()
            _LOGGER.info("[minimize_cost] decision=DISCHARGE (price %.4f >= high_threshold %.4f, soc %.1f%% > min %.0f%%)",
                         current_price, high_threshold, data.battery_soc, min_soc)
        else:
            data.next_action = ACTION_IDLE
            _LOGGER.info("[minimize_cost] decision=IDLE")

    def _optimize_maximize_self_consumption(self, data: EnergyOptimizerData) -> None:
        """Optimize to maximize self-consumption of solar energy."""
        if not data.solar_forecast:
            _LOGGER.info("[maximize_self_consumption] no solar forecast, action=idle")
            data.next_action = ACTION_IDLE
            return

        current_time = datetime.now()
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        next_solar_period = None
        for forecast in data.solar_forecast:
            forecast_time = self._parse_time(forecast.get("period_end", ""))
            if forecast_time > current_time and forecast.get("pv_estimate", 0) > 1.0:
                next_solar_period = forecast
                break

        if next_solar_period:
            pv = next_solar_period.get("pv_estimate", 0)
            _LOGGER.info("[maximize_self_consumption] next solar period: pv_estimate=%.2f kW at %s",
                         pv, next_solar_period.get("period_end"))
            if data.battery_soc is not None and data.battery_soc > max_soc - 20:
                data.next_action = ACTION_DISCHARGE
                data.target_soc = max_soc - 20
                _LOGGER.info("[maximize_self_consumption] decision=DISCHARGE to make room (soc=%.1f%%)", data.battery_soc)
            else:
                data.next_action = ACTION_IDLE
                _LOGGER.info("[maximize_self_consumption] decision=IDLE (battery has room)")
        else:
            data.next_action = ACTION_IDLE
            _LOGGER.info("[maximize_self_consumption] decision=IDLE (no significant solar expected)")

    def _optimize_grid_independence(self, data: EnergyOptimizerData) -> None:
        """Optimize for grid independence."""
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        if data.battery_soc is not None:
            if data.battery_soc < max_soc:
                data.next_action = ACTION_CHARGE
                data.target_soc = max_soc
                _LOGGER.info("[grid_independence] decision=CHARGE (soc=%.1f%% < max=%.0f%%)", data.battery_soc, max_soc)
            else:
                data.next_action = ACTION_IDLE
                _LOGGER.info("[grid_independence] decision=IDLE (soc=%.1f%% >= max=%.0f%%)", data.battery_soc, max_soc)
        else:
            data.next_action = ACTION_IDLE
            _LOGGER.info("[grid_independence] decision=IDLE (no battery SOC available)")

    def _optimize_balanced(self, data: EnergyOptimizerData) -> None:
        """Optimize with a balanced approach."""
        min_soc = float(self.config_entry.data.get(CONF_MIN_SOC, 20))
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        if not data.prices_today:
            _LOGGER.info("[balanced] no price data, action=idle")
            data.next_action = ACTION_IDLE
            return

        current_time = datetime.now()
        current_naive = current_time.replace(tzinfo=None)
        prices_ahead = []
        for p in data.prices_today:
            parsed_naive = self._parse_time(p.get("from", "")).replace(tzinfo=None)
            if parsed_naive >= current_naive:
                prices_ahead.append(p)

        if not prices_ahead:
            _LOGGER.info("[balanced] no future prices, action=idle")
            data.next_action = ACTION_IDLE
            return

        avg_price = sum(float(p.get("price", 0)) for p in prices_ahead) / len(prices_ahead)
        current_price = data.current_price or 0

        _LOGGER.info(
            "[balanced] current_price=%.4f, avg_price=%.4f, soc=%s%%",
            current_price,
            avg_price,
            data.battery_soc,
        )

        if current_price < avg_price * 0.9 and data.battery_soc is not None and data.battery_soc < max_soc:
            data.next_action = ACTION_CHARGE
            data.target_soc = max_soc
            _LOGGER.info("[balanced] decision=CHARGE")
        elif current_price > avg_price * 1.1 and data.battery_soc is not None and data.battery_soc > min_soc:
            data.next_action = ACTION_DISCHARGE
            data.target_soc = min_soc
            _LOGGER.info("[balanced] decision=DISCHARGE")
        else:
            data.next_action = ACTION_IDLE
            _LOGGER.info("[balanced] decision=IDLE")

    def _parse_time(self, time_str: str | datetime) -> datetime:
        """Parse time string or datetime to datetime."""
        try:
            if isinstance(time_str, datetime):
                return time_str
            if isinstance(time_str, str):
                return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            _LOGGER.warning("Unexpected type for time parsing: %s (%s)", time_str, type(time_str).__name__)
            return datetime.now()
        except (ValueError, AttributeError, TypeError) as e:
            _LOGGER.warning("Could not parse time '%s': %s", time_str, e)
            return datetime.now()
