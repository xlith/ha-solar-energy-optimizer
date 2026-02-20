# Installation Guide

## Prerequisites

Before installing Solar Energy Optimizer, you must have these integrations installed and configured:

### 1. Solax Modbus Integration
**Installation**: [Documentation](https://homeassistant-solax-modbus.readthedocs.io/en/latest/)

This provides:
- Battery state of charge (SOC) sensor
- Inverter status
- Power flow information

**Required Entity**: A sensor showing battery SOC (e.g., `sensor.solax_battery_soc`)

### 2. Solcast Solar
**Installation**: Via HACS or [GitHub](https://github.com/BJReplay/ha-solcast-solar)

This provides:
- Solar production forecasts
- Half-hourly estimates
- Multiple forecast scenarios

**Required Entity**: A Solcast forecast sensor (e.g., `sensor.solcast_pv_forecast_today`)

### 3. Frank Energie
**Installation**: Via HACS or [GitHub](https://github.com/HiDiHo01/home-assistant-frank_energie)

This provides:
- Current electricity prices
- Hourly price forecasts
- Price history

**Required Entity**: Current price sensor (e.g., `sensor.current_electricity_price`)

## Installation Methods

### Option 1: HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu (⋮) in the top right
4. Select "Custom repositories"
5. Add this repository:
   - **URL**: `https://github.com/xlith/ha-solar-energy-optimizer`
   - **Category**: Integration
6. Click "Add"
7. Find "Solar Energy Optimizer" in the integrations list
8. Click "Download"
9. Restart Home Assistant

### Option 2: Manual Installation

1. Download the latest release from GitHub
2. Extract the files
3. Copy the `custom_components/solax_energy_optimizer` folder to your Home Assistant's `custom_components` directory:
   ```
   /config/custom_components/solax_energy_optimizer/
   ```
4. Restart Home Assistant

## Configuration

### Step 1: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for "Solar Energy Optimizer"
4. Click on it to start configuration

### Step 2: Configure Entities

Fill in the configuration form:

#### Entity Selection
- **Solax Inverter Battery SOC Entity**:
  - Select the sensor that shows your battery's state of charge
  - Usually something like `sensor.solax_battery_soc`
  - Must be a percentage value (0-100)

- **Solcast Solar Forecast Entity**:
  - Select your Solcast forecast sensor
  - Usually `sensor.solcast_pv_forecast_today`
  - Should have forecast data in attributes

- **Frank Energie Price Entity**:
  - Select the current electricity price sensor
  - Usually `sensor.current_electricity_price`
  - Should be in EUR per kWh

#### Battery Configuration
- **Battery Capacity** (kWh):
  - Enter your battery's total capacity
  - Example: 10.0 kWh

- **Maximum Charge Rate** (kW):
  - Maximum power at which your battery can charge
  - Check your inverter specifications
  - Example: 5.0 kW

- **Maximum Discharge Rate** (kW):
  - Maximum power at which your battery can discharge
  - Check your inverter specifications
  - Example: 5.0 kW

#### Safety Limits
- **Minimum State of Charge** (%):
  - Default: 20%
  - Safety buffer to protect battery
  - Don't set too low (< 10%)

- **Maximum State of Charge** (%):
  - Default: 95%
  - Protect battery health
  - Don't set to 100%

### Step 3: Submit

Click **Submit** to create the integration.

## Post-Installation

### Verify Installation

1. Check that the integration appears in **Settings** → **Devices & Services**
2. Click on the integration to see all entities
3. Verify all sensors show data

### Expected Entities

You should see:

#### Sensors
- `sensor.solax_energy_optimizer_next_action`
- `sensor.solax_energy_optimizer_next_action_time`
- `sensor.solax_energy_optimizer_daily_cost`
- `sensor.solax_energy_optimizer_daily_savings`
- `sensor.solax_energy_optimizer_monthly_cost`
- `sensor.solax_energy_optimizer_monthly_savings`

#### Switches
- `switch.solax_energy_optimizer_automation_enabled`
- `switch.solax_energy_optimizer_manual_override`
- `switch.solax_energy_optimizer_dry_run`

#### Select
- `select.solax_energy_optimizer_strategy`

### Initial Setup

**IMPORTANT**: The integration starts in **dry run mode** for safety!

1. **Test in Dry Run Mode** (Recommended):
   - Verify `switch.solax_energy_optimizer_dry_run` is ON
   - Choose a strategy (start with "Minimize Cost")
   - Observe recommended actions for 24-48 hours
   - Check logs to see what would be executed:
     ```
     Settings → System → Logs
     Filter: "solax_energy_optimizer"
     Look for: "DRY RUN MODE: Would execute..."
     ```

2. **Verify Behavior**:
   - Ensure recommendations make sense
   - Compare with actual price/solar data
   - Adjust strategy if needed

3. **Enable Production Mode** (Optional):
   - Only after testing and when inverter control is implemented
   - Turn OFF `switch.solax_energy_optimizer_dry_run`
   - Monitor closely for the first few cycles

4. **Enable Automation**:
   - Ensure `switch.solax_energy_optimizer_automation_enabled` is ON
   - Ensure `switch.solax_energy_optimizer_manual_override` is OFF

5. **Monitor**:
   - Watch the `next_action` sensor
   - Check logs regularly
   - Verify battery behaves as expected

## Troubleshooting

### Integration Won't Install

**Problem**: Integration doesn't appear in the list

**Solution**:
1. Clear browser cache
2. Restart Home Assistant
3. Check `custom_components/solax_energy_optimizer/` exists
4. Check file permissions

### Configuration Fails

**Problem**: "Entity not found" error

**Solution**:
1. Verify prerequisite integrations are installed
2. Check entity IDs in Developer Tools → States
3. Copy exact entity ID (case-sensitive)

### No Data in Sensors

**Problem**: Sensors show "unknown" or "unavailable"

**Solution**:
1. Check source entities have valid data
2. Wait 5 minutes for first update
3. Check logs: Settings → System → Logs
4. Filter for `solax_energy_optimizer`

### Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.solax_energy_optimizer: debug
```

Restart Home Assistant to apply.

## Next Steps

1. **Add to Dashboard**:
   - Create cards for monitoring
   - Use entity cards for quick control

2. **Create Automations**:
   - See `examples/automations.yaml`
   - Customize for your needs

3. **Optimize Settings**:
   - Adjust min/max SOC based on results
   - Try different strategies
   - Fine-tune for your situation

## Getting Help

If you encounter issues:

1. Check the logs for error messages
2. Review the [README.md](README.md) for detailed information
3. See [DEVELOPMENT.md](DEVELOPMENT.md) for technical details
4. Open an issue on [GitHub](https://github.com/xlith/ha-solar-energy-optimizer/issues)

## Uninstalling

To remove the integration:

1. Go to **Settings** → **Devices & Services**
2. Find "Solar Energy Optimizer"
3. Click the three dots menu (⋮)
4. Select "Delete"
5. Confirm deletion
6. (Optional) Remove files from `custom_components/` directory
7. Restart Home Assistant
