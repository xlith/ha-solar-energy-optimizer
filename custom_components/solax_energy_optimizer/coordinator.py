"""Data update coordinator for Solax Energy Optimizer."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    ACTION_CHARGE,
    ACTION_DISCHARGE,
    ACTION_IDLE,
    CONF_ELECTRICITY_PRICES_ENTITY,
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
        self.current_price: float | None = None
        self.prices_today: list[dict[str, Any]] = []
        self.prices_tomorrow: list[dict[str, Any]] = []
        self.solar_forecast: list[dict[str, Any]] = []
        self.next_action: str = ACTION_IDLE
        self.last_action_time: datetime | None = None
        self.next_update_time: datetime | None = None
        self.target_soc: float | None = None
        self.decision_reason: str = ""
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
        self._update_count: int = 0

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

    @property
    def update_count(self) -> int:
        """Return total number of completed update cycles."""
        return self._update_count

    async def _async_update_data(self) -> EnergyOptimizerData:
        """Fetch data from dependencies and run optimization."""
        self._update_count += 1
        _LOGGER.info("=== Update cycle #%d start ===", self._update_count)
        try:
            data = EnergyOptimizerData()
            data.next_update_time = dt_util.now() + DEFAULT_UPDATE_INTERVAL

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
                forecasts = solcast_state.attributes.get("detailedForecast", [])
                data.solar_forecast = forecasts
                # Log the next 3 non-zero solar periods for context
                upcoming = [
                    f for f in forecasts
                    if self._parse_datetime(f.get("period_start", "")) > dt_util.now()
                    and f.get("pv_estimate", 0) > 0
                ][:3]
                upcoming_str = ", ".join(
                    f"{self._parse_datetime(f.get('period_start', '')).strftime('%H:%M')}={f.get('pv_estimate', 0):.2f}kW"
                    for f in upcoming
                ) or "none"
                _LOGGER.info(
                    "[solcast] %s: today_total=%.3f kWh, %d forecast entries, next non-zero: %s",
                    solcast_entity,
                    float(solcast_state.state) if solcast_state.state not in ("unavailable", "unknown") else 0,
                    len(forecasts),
                    upcoming_str,
                )
            else:
                _LOGGER.info("[solcast] %s: state=%s, no attributes", solcast_entity, solcast_state.state)

            # --- Electricity prices ---
            prices_entity = self.config_entry.data[CONF_ELECTRICITY_PRICES_ENTITY]
            prices_state = self.hass.states.get(prices_entity)
            if prices_state is None:
                _LOGGER.info("[prices] %s: not yet in HA state machine", prices_entity)
            else:
                try:
                    data.current_price = float(prices_state.state)
                except (ValueError, TypeError) as e:
                    _LOGGER.warning("[prices] %s: could not parse state='%s' as float: %s", prices_entity, prices_state.state, e)

                if prices_state.attributes:
                    price_entries = prices_state.attributes.get("prices", [])
                    data.prices_today = price_entries if isinstance(price_entries, list) else []
                    _LOGGER.info(
                        "[prices] %s: current=€%.4f/kWh, %d price entries loaded",
                        prices_entity,
                        data.current_price if data.current_price is not None else 0,
                        len(data.prices_today),
                    )
                else:
                    _LOGGER.warning("[prices] %s: entity has no attributes", prices_entity)

            # --- Optimization ---
            _LOGGER.info(
                "[optimizer] #%d | strategy=%s | automation=%s | manual_override=%s | dry_run=%s",
                self._update_count,
                self._current_strategy,
                self._automation_enabled,
                self._manual_override,
                self._dry_run_mode,
            )

            if self._automation_enabled and not self._manual_override:
                self._run_optimization(data)
                mode = "DRY RUN" if self._dry_run_mode else "LIVE"
                _LOGGER.info(
                    "[optimizer] %s | action=%s | target_soc=%s%% | reason: %s",
                    mode,
                    data.next_action,
                    data.target_soc,
                    data.decision_reason,
                )
            else:
                reason = "automation disabled" if not self._automation_enabled else "manual override active"
                data.decision_reason = reason
                _LOGGER.info("[optimizer] skipped — %s", reason)

            _LOGGER.info("=== Update cycle #%d end ===", self._update_count)
            return data

        except Exception as err:
            _LOGGER.error("Update cycle #%d failed: %s (%s)", self._update_count, err, type(err).__name__, exc_info=True)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    def _run_optimization(self, data: EnergyOptimizerData) -> None:
        """Run optimization algorithm based on current strategy."""
        min_soc = float(self.config_entry.data.get(CONF_MIN_SOC, 20))

        # Safety override: charge immediately if SOC is below the configured minimum
        if data.battery_soc is not None and data.battery_soc < min_soc:
            data.next_action = ACTION_CHARGE
            data.target_soc = min_soc
            data.last_action_time = dt_util.now()
            data.decision_reason = (
                f"Safety override — SOC {data.battery_soc:.1f}% is below minimum {min_soc:.0f}%"
            )
            _LOGGER.info(
                "[optimizer] SAFETY OVERRIDE | SOC=%.1f%% < min=%.0f%% | action=CHARGE to %.0f%%",
                data.battery_soc,
                min_soc,
                min_soc,
            )
            return

        if self._current_strategy == STRATEGY_MINIMIZE_COST:
            self._optimize_minimize_cost(data)
        elif self._current_strategy == STRATEGY_MAXIMIZE_SELF_CONSUMPTION:
            self._optimize_maximize_self_consumption(data)
        elif self._current_strategy == STRATEGY_GRID_INDEPENDENCE:
            self._optimize_grid_independence(data)
        elif self._current_strategy == STRATEGY_BALANCED:
            self._optimize_balanced(data)

    def _optimize_minimize_cost(self, data: EnergyOptimizerData) -> None:
        """Optimize to minimize energy costs."""
        if not data.prices_today:
            data.next_action = ACTION_IDLE
            data.decision_reason = "No price data available"
            _LOGGER.info("[minimize_cost] no price data → idle")
            return

        now = dt_util.now()
        future_prices = []
        for p in data.prices_today:
            try:
                if not isinstance(p, dict):
                    _LOGGER.warning("[minimize_cost] unexpected price entry type %s: %s", type(p).__name__, p)
                    continue
                if self._parse_datetime(p.get("from", "")) >= now:
                    future_prices.append(p)
            except Exception as e:
                _LOGGER.error("[minimize_cost] error processing price entry %s: %s", p, e, exc_info=True)

        if not future_prices:
            data.next_action = ACTION_IDLE
            data.decision_reason = "No future price entries found"
            _LOGGER.info("[minimize_cost] no future prices → idle")
            return

        prices_by_value = sorted(future_prices, key=lambda x: float(x.get("price", 0)))
        lowest_price_val = float(prices_by_value[0].get("price", 0))
        highest_price_val = float(prices_by_value[-1].get("price", 0))

        price_range = highest_price_val - lowest_price_val
        cheap_price_threshold = lowest_price_val + (price_range * 0.25)
        expensive_price_threshold = highest_price_val - (price_range * 0.25)
        current_price = data.current_price or 0
        min_soc = float(self.config_entry.data.get(CONF_MIN_SOC, 20))
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        _LOGGER.info(
            "[minimize_cost] inputs:"
            " current_price=€%.4f"
            " | price_range=[€%.4f, €%.4f]"
            " | cheap_threshold=€%.4f (bottom 25%%)"
            " | expensive_threshold=€%.4f (top 25%%)"
            " | SOC=%.1f%%"
            " | SOC_limits=[%.0f%%, %.0f%%]"
            " | future_prices=%d",
            current_price,
            lowest_price_val,
            highest_price_val,
            cheap_price_threshold,
            expensive_price_threshold,
            data.battery_soc if data.battery_soc is not None else -1,
            min_soc,
            max_soc,
            len(future_prices),
        )

        if current_price <= cheap_price_threshold and data.battery_soc is not None and data.battery_soc < max_soc:
            data.next_action = ACTION_CHARGE
            data.target_soc = max_soc
            data.last_action_time = dt_util.now()
            data.decision_reason = (
                f"Price €{current_price:.4f} ≤ cheap threshold €{cheap_price_threshold:.4f} "
                f"and SOC {data.battery_soc:.1f}% < max {max_soc:.0f}%"
            )
            _LOGGER.info(
                "[minimize_cost] CHARGE | €%.4f ≤ cheap_threshold €%.4f | SOC %.1f%% < max %.0f%%",
                current_price, cheap_price_threshold, data.battery_soc, max_soc,
            )
        elif current_price >= expensive_price_threshold and data.battery_soc is not None and data.battery_soc > min_soc:
            data.next_action = ACTION_DISCHARGE
            data.target_soc = min_soc
            data.last_action_time = dt_util.now()
            data.decision_reason = (
                f"Price €{current_price:.4f} ≥ expensive threshold €{expensive_price_threshold:.4f} "
                f"and SOC {data.battery_soc:.1f}% > min {min_soc:.0f}%"
            )
            _LOGGER.info(
                "[minimize_cost] DISCHARGE | €%.4f ≥ expensive_threshold €%.4f | SOC %.1f%% > min %.0f%%",
                current_price, expensive_price_threshold, data.battery_soc, min_soc,
            )
        else:
            data.next_action = ACTION_IDLE
            # Explain exactly why idle was chosen
            if current_price > cheap_price_threshold and current_price < expensive_price_threshold:
                reason = (
                    f"Price €{current_price:.4f} is in moderate range "
                    f"(€{cheap_price_threshold:.4f}–€{expensive_price_threshold:.4f})"
                )
            elif data.battery_soc is None:
                reason = "Battery SOC unavailable"
            elif current_price <= cheap_price_threshold and data.battery_soc is not None and data.battery_soc >= max_soc:
                reason = f"Price is cheap but battery already at max SOC ({data.battery_soc:.1f}%)"
            elif current_price >= expensive_price_threshold and data.battery_soc is not None and data.battery_soc <= min_soc:
                reason = f"Price is expensive but battery already at min SOC ({data.battery_soc:.1f}%)"
            else:
                reason = (
                    f"Price €{current_price:.4f} in moderate range "
                    f"(cheap=€{cheap_price_threshold:.4f}, expensive=€{expensive_price_threshold:.4f})"
                )
            data.decision_reason = reason
            _LOGGER.info("[minimize_cost] IDLE | %s", reason)

    def _optimize_maximize_self_consumption(self, data: EnergyOptimizerData) -> None:
        """Optimize to maximize self-consumption of solar energy."""
        if not data.solar_forecast:
            data.next_action = ACTION_IDLE
            data.decision_reason = "No solar forecast data available"
            _LOGGER.info("[maximize_self_consumption] no solar forecast → idle")
            return

        now = dt_util.now()
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        next_solar_period = None
        for forecast in data.solar_forecast:
            forecast_time = self._parse_datetime(forecast.get("period_start", ""))
            if forecast_time > now and forecast.get("pv_estimate", 0) > 1.0:
                next_solar_period = forecast
                break

        if next_solar_period:
            pv = next_solar_period.get("pv_estimate", 0)
            period_start = next_solar_period.get("period_start", "?")
            _LOGGER.info(
                "[maximize_self_consumption] inputs: next_solar_period=%s pv_estimate=%.2f kW | SOC=%.1f%% | max_soc=%.0f%% | headroom_threshold=%.0f%%",
                period_start, pv,
                data.battery_soc if data.battery_soc is not None else -1,
                max_soc,
                max_soc - 20,
            )
            if data.battery_soc is not None and data.battery_soc > max_soc - 20:
                data.next_action = ACTION_DISCHARGE
                data.target_soc = max_soc - 20
                data.decision_reason = (
                    f"Solar expected {pv:.2f} kW at {period_start[11:16]} — "
                    f"discharging to {max_soc - 20:.0f}% to make room (SOC {data.battery_soc:.1f}% > headroom threshold {max_soc - 20:.0f}%)"
                )
                _LOGGER.info(
                    "[maximize_self_consumption] DISCHARGE to %.0f%% | SOC %.1f%% > headroom threshold %.0f%% | solar=%.2f kW at %s",
                    max_soc - 20, data.battery_soc, max_soc - 20, pv, period_start[11:16],
                )
            else:
                data.next_action = ACTION_IDLE
                data.decision_reason = (
                    f"Solar expected {pv:.2f} kW at {period_start[11:16]} — "
                    f"battery has enough room (SOC {data.battery_soc:.1f}% ≤ {max_soc - 20:.0f}%)"
                )
                _LOGGER.info(
                    "[maximize_self_consumption] IDLE | battery has room | SOC=%.1f%% ≤ headroom_threshold=%.0f%%",
                    data.battery_soc if data.battery_soc is not None else -1,
                    max_soc - 20,
                )
        else:
            data.next_action = ACTION_IDLE
            data.decision_reason = "No significant solar production expected (all periods < 1.0 kW)"
            _LOGGER.info("[maximize_self_consumption] IDLE | no solar period > 1.0 kW found in forecast")

    def _optimize_grid_independence(self, data: EnergyOptimizerData) -> None:
        """Optimize for grid independence."""
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        _LOGGER.info(
            "[grid_independence] inputs: SOC=%s%% | max_soc=%.0f%%",
            f"{data.battery_soc:.1f}" if data.battery_soc is not None else "unavailable",
            max_soc,
        )

        if data.battery_soc is not None:
            if data.battery_soc < max_soc:
                data.next_action = ACTION_CHARGE
                data.target_soc = max_soc
                data.decision_reason = (
                    f"Grid independence — charging to max {max_soc:.0f}% (SOC {data.battery_soc:.1f}% < {max_soc:.0f}%)"
                )
                _LOGGER.info("[grid_independence] CHARGE to %.0f%% | SOC %.1f%% < max %.0f%%", max_soc, data.battery_soc, max_soc)
            else:
                data.next_action = ACTION_IDLE
                data.decision_reason = f"Battery already at max SOC ({data.battery_soc:.1f}% ≥ {max_soc:.0f}%)"
                _LOGGER.info("[grid_independence] IDLE | SOC %.1f%% ≥ max %.0f%%", data.battery_soc, max_soc)
        else:
            data.next_action = ACTION_IDLE
            data.decision_reason = "Battery SOC unavailable"
            _LOGGER.info("[grid_independence] IDLE | battery SOC unavailable")

    def _optimize_balanced(self, data: EnergyOptimizerData) -> None:
        """Optimize with a balanced approach."""
        min_soc = float(self.config_entry.data.get(CONF_MIN_SOC, 20))
        max_soc = float(self.config_entry.data.get(CONF_MAX_SOC, 95))

        if not data.prices_today:
            data.next_action = ACTION_IDLE
            data.decision_reason = "No price data available"
            _LOGGER.info("[balanced] no price data → idle")
            return

        now = dt_util.now()
        future_prices = [
            p for p in data.prices_today
            if self._parse_datetime(p.get("from", "")) >= now
        ]

        if not future_prices:
            data.next_action = ACTION_IDLE
            data.decision_reason = "No future price entries found"
            _LOGGER.info("[balanced] no future prices → idle")
            return

        avg_price = sum(float(p.get("price", 0)) for p in future_prices) / len(future_prices)
        current_price = data.current_price or 0
        charge_threshold = avg_price * 0.9
        discharge_threshold = avg_price * 1.1

        _LOGGER.info(
            "[balanced] inputs:"
            " current_price=€%.4f"
            " | avg_price=€%.4f (over %d future periods)"
            " | charge_threshold=€%.4f (avg×0.9)"
            " | discharge_threshold=€%.4f (avg×1.1)"
            " | SOC=%.1f%%"
            " | SOC_limits=[%.0f%%, %.0f%%]",
            current_price,
            avg_price,
            len(future_prices),
            charge_threshold,
            discharge_threshold,
            data.battery_soc if data.battery_soc is not None else -1,
            min_soc,
            max_soc,
        )

        if current_price < charge_threshold and data.battery_soc is not None and data.battery_soc < max_soc:
            data.next_action = ACTION_CHARGE
            data.target_soc = max_soc
            data.decision_reason = (
                f"Price €{current_price:.4f} < charge threshold €{charge_threshold:.4f} (avg €{avg_price:.4f} × 0.9) "
                f"and SOC {data.battery_soc:.1f}% < max {max_soc:.0f}%"
            )
            _LOGGER.info("[balanced] CHARGE | €%.4f < charge_threshold €%.4f | SOC %.1f%% < max %.0f%%",
                         current_price, charge_threshold, data.battery_soc, max_soc)
        elif current_price > discharge_threshold and data.battery_soc is not None and data.battery_soc > min_soc:
            data.next_action = ACTION_DISCHARGE
            data.target_soc = min_soc
            data.decision_reason = (
                f"Price €{current_price:.4f} > discharge threshold €{discharge_threshold:.4f} (avg €{avg_price:.4f} × 1.1) "
                f"and SOC {data.battery_soc:.1f}% > min {min_soc:.0f}%"
            )
            _LOGGER.info("[balanced] DISCHARGE | €%.4f > discharge_threshold €%.4f | SOC %.1f%% > min %.0f%%",
                         current_price, discharge_threshold, data.battery_soc, min_soc)
        else:
            data.next_action = ACTION_IDLE
            reason = (
                f"Price €{current_price:.4f} in moderate range "
                f"(charge=€{charge_threshold:.4f}, discharge=€{discharge_threshold:.4f}, avg=€{avg_price:.4f})"
            )
            data.decision_reason = reason
            _LOGGER.info("[balanced] IDLE | %s", reason)

    def _parse_datetime(self, time_str: str | datetime) -> datetime:
        """Parse an ISO 8601 string or passthrough an existing datetime."""
        try:
            if isinstance(time_str, datetime):
                return time_str
            if isinstance(time_str, str):
                return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            _LOGGER.warning("Unexpected type for datetime parsing: %s (%s)", time_str, type(time_str).__name__)
            return dt_util.now()
        except (ValueError, AttributeError, TypeError) as e:
            _LOGGER.warning("Could not parse datetime '%s': %s", time_str, e)
            return dt_util.now()
