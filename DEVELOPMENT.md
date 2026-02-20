# Development Guide

## Project Structure

```
solax-energie/
├── custom_components/
│   └── solax_energy_optimizer/
│       ├── __init__.py              # Integration setup and service registration
│       ├── manifest.json            # Integration metadata
│       ├── const.py                 # Constants and configuration keys
│       ├── config_flow.py           # UI configuration flow
│       ├── coordinator.py           # Data coordinator with optimization logic
│       ├── sensor.py                # Sensor entities
│       ├── switch.py                # Switch entities
│       ├── select.py                # Select entity for strategy
│       ├── services.yaml            # Service definitions
│       └── strings.json             # Translations
├── examples/
│   └── automations.yaml             # Example automations
├── hacs.json                        # HACS configuration
├── info.md                          # HACS info page
├── README.md                        # Main documentation
├── LICENSE                          # MIT License
└── .gitignore                       # Git ignore rules
```

## Integration Architecture

### Data Flow

1. **Coordinator** (`coordinator.py`):
   - Fetches data from source entities every 5 minutes
   - Runs optimization algorithm based on selected strategy
   - Stores results in `EnergyOptimizerData` object

2. **Entities** subscribe to coordinator:
   - **Sensors**: Display optimization results and cost tracking
   - **Switches**: Control automation and manual override
   - **Select**: Choose optimization strategy

3. **Services**: Provide manual control options

### Optimization Strategies

#### 1. Minimize Cost
- Analyzes 24-hour price forecast
- Charges during bottom 25% price periods
- Discharges during top 25% price periods
- Remains idle during moderate prices

#### 2. Maximize Self-Consumption
- Analyzes solar production forecast
- Ensures battery capacity before solar periods
- Prioritizes storing solar energy
- Minimizes grid dependency

#### 3. Grid Independence
- Maintains maximum safe battery charge
- Prioritizes battery and solar over grid
- Only uses grid as backup

#### 4. Balanced
- Combines cost and self-consumption strategies
- Charges when price < 90% of average
- Discharges when price > 110% of average

## Next Steps

### 1. Testing

The integration is ready for testing. To test:

1. Install the integration in Home Assistant:
   ```bash
   # Copy to your HA config directory
   cp -r custom_components/solax_energy_optimizer /config/custom_components/
   ```

2. Restart Home Assistant

3. Add the integration via UI:
   - Settings → Devices & Services → Add Integration
   - Search for "Solar Energy Optimizer"

4. Configure with your entity IDs

5. Monitor logs for any errors:
   ```bash
   tail -f /config/home-assistant.log | grep solax_energy_optimizer
   ```

### 2. Dry Run Mode

**Default State**: The integration starts in **dry run mode** for safety.

In dry run mode:
- All optimization logic runs
- Recommended actions are logged
- No actual battery control is executed
- Safe for testing and validation

**Implementation Details**:
- Dry run state stored in coordinator: `self._dry_run_mode`
- Switch entity: `switch.solax_energy_optimizer_dry_run`
- Logs show: "DRY RUN MODE: Would execute {action}"
- Attribute in next_action sensor: `dry_run_mode`

**Disabling Dry Run**:
Only disable after:
1. Testing for 24-48 hours
2. Verifying recommendations are sensible
3. Implementing actual inverter control (see next section)

### 3. Integration with Solax Modbus

The current implementation **monitors** battery state but does not yet **control** the inverter. To add control:

1. Research Solax Modbus services:
   - Find services for setting charge/discharge modes
   - Identify service parameters (power level, mode, etc.)

2. Implement control in coordinator (`coordinator.py:160`):
   ```python
   async def _execute_action(self, action: str, target_soc: float) -> None:
       """Execute battery control action via Solax Modbus."""
       if self._dry_run_mode:
           # Already logged, just return
           return

       if action == ACTION_CHARGE:
           await self.hass.services.async_call(
               "solax",
               "set_charge_mode",
               {"power": self.config_entry.data[CONF_MAX_CHARGE_RATE]}
           )
       elif action == ACTION_DISCHARGE:
           await self.hass.services.async_call(
               "solax",
               "set_discharge_mode",
               {"power": self.config_entry.data[CONF_MAX_DISCHARGE_RATE]}
           )
       # ... etc
   ```

3. Uncomment the TODO in `_async_update_data` (line ~165):
   ```python
   # TODO: Implement actual inverter control
   # await self._execute_action(data.next_action, data.target_soc)
   ```

### 4. Enhanced Cost Tracking

Currently, cost tracking sensors show `0.0`. To implement:

1. Store historical data in coordinator
2. Track actual charge/discharge events
3. Calculate costs based on prices at time of action
4. Compare with baseline (no optimization) scenario

### 5. Advanced Features

Consider adding:

1. **Weather integration**: Adjust strategy based on weather forecasts
2. **Load prediction**: Learn household consumption patterns
3. **Multi-battery support**: Coordinate multiple battery systems
4. **Price threshold configuration**: Let users set custom thresholds
5. **Notifications**: Alert on significant price changes or actions
6. **Statistics**: Long-term cost/savings analysis
7. **Export data**: CSV export for external analysis

### 6. Testing & Validation

Create tests for:
- Config flow validation
- Coordinator optimization logic
- Entity state updates
- Service calls

Example test structure:
```python
# tests/test_coordinator.py
async def test_minimize_cost_strategy():
    """Test cost minimization strategy."""
    # Setup mock data
    data = EnergyOptimizerData()
    data.battery_soc = 50
    data.current_price = 0.10
    data.prices_today = [...]

    # Run optimization
    coordinator._optimize_minimize_cost(data)

    # Assert expected action
    assert data.next_action == ACTION_CHARGE
```

## Deployment

### Via HACS

1. Create GitHub repository
2. Push code to GitHub
3. Add repository to HACS as custom repository
4. Users can install via HACS

### Manual Installation

Users can copy `custom_components/solax_energy_optimizer` to their Home Assistant config directory.

## Configuration Tips

### Finding Entity IDs

Help users find correct entity IDs:

1. **Battery SOC**: Usually `sensor.solax_battery_soc` or similar
2. **Solcast**: Usually `sensor.solcast_pv_forecast_*`
3. **Frank Energie**: Usually `sensor.current_electricity_price`

### Optimal Settings

Recommended starting values:
- Min SOC: 20% (safety buffer)
- Max SOC: 95% (battery health)
- Update interval: 5 minutes
- Strategy: Start with "Minimize Cost"

## Troubleshooting

### Common Issues

1. **Integration won't load**:
   - Check all prerequisite integrations are installed
   - Verify entity IDs are correct
   - Check HA logs for errors

2. **No optimization actions**:
   - Verify source entities have data
   - Check automation is enabled
   - Ensure manual override is off

3. **Unexpected behavior**:
   - Review strategy logic in coordinator.py
   - Check logs for debug messages
   - Verify battery limits are reasonable

### Debug Logging

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.solax_energy_optimizer: debug
```

## Contributing

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Future Enhancements

### Phase 2 - Control Implementation
- Direct inverter control via Solax Modbus
- Automatic mode switching
- Power level optimization

### Phase 3 - Learning & Prediction
- Machine learning for consumption prediction
- Historical pattern analysis
- Adaptive strategy tuning

### Phase 4 - Multi-system Support
- Support for other inverter brands
- Multiple battery systems
- Grid feed-in optimization

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [Solax Modbus Documentation](https://homeassistant-solax-modbus.readthedocs.io/)
- [Solcast Solar](https://github.com/BJReplay/ha-solcast-solar)
- [Frank Energie](https://github.com/HiDiHo01/home-assistant-frank_energie)
