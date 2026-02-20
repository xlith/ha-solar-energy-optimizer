# Solar Energy Optimizer

[![GitHub Release](https://img.shields.io/github/v/release/xlith/ha-solar-energy-optimizer)](https://github.com/xlith/ha-solar-energy-optimizer/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/xlith/ha-solar-energy-optimizer)](https://github.com/xlith/ha-solar-energy-optimizer/commits/main)
[![License](https://img.shields.io/github/license/xlith/ha-solar-energy-optimizer)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HACS Validation](https://github.com/xlith/ha-solar-energy-optimizer/actions/workflows/hacs-validation.yml/badge.svg)](https://github.com/xlith/ha-solar-energy-optimizer/actions/workflows/hacs-validation.yml)
[![Code Quality](https://github.com/xlith/ha-solar-energy-optimizer/actions/workflows/quality.yml/badge.svg)](https://github.com/xlith/ha-solar-energy-optimizer/actions/workflows/quality.yml)

A Home Assistant custom integration that optimizes energy cycles between grid, battery, and solar panels based on dynamic energy prices, solar production forecasts, and configurable optimization strategies.

## ⚠️ DO NOT USE - Under Development

> **WARNING**: This integration is under active development and **should not be used at this time**.
>
> The code is not yet functional and has not been tested. This repository is being published for development purposes only.
>
> **Do not install or use this integration in any production environment.**
>
> Updates will be posted when the integration reaches a usable state.

## Features

- **Multiple Optimization Strategies**:
  - **Minimize Cost**: Charge when prices are low, discharge when high
  - **Maximize Self-Consumption**: Prioritize using solar energy, minimize grid usage
  - **Grid Independence**: Maximize battery usage, only use grid as backup
  - **Balanced**: Combines cost optimization with self-consumption

- **Real-time Monitoring**:
  - Next action sensor (charge/discharge/idle)
  - Daily and monthly cost/savings tracking
  - Battery state and price information

- **Manual Control**:
  - Automation enable/disable switch
  - Manual override switch
  - Strategy selector

- **Configurable Settings**:
  - Battery capacity and charge/discharge rates
  - Min/max state of charge limits
  - Entity selection for data sources

## Prerequisites

This integration requires the following Home Assistant integrations to be already installed and configured:

1. **Solax Modbus Integration**: [homeassistant-solax-modbus](https://homeassistant-solax-modbus.readthedocs.io/en/latest/)
   - Provides battery state of charge and inverter control

2. **Solcast Solar**: [ha-solcast-solar](https://github.com/BJReplay/ha-solcast-solar)
   - Provides solar production forecasts

3. **Frank Energie**: [home-assistant-frank_energie](https://github.com/HiDiHo01/home-assistant-frank_energie)
   - Provides dynamic electricity prices

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations → ⋮ → Custom repositories
   - Add: `https://github.com/xlith/ha-solar-energy-optimizer`
   - Category: Integration

2. Click "Install" on the Solar Energy Optimizer card

3. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/solax_energy_optimizer` directory to your Home Assistant's `custom_components` directory

2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**

2. Click **+ Add Integration**

3. Search for "Solar Energy Optimizer"

4. Fill in the configuration form:
   - **Solax Inverter Battery SOC Entity**: Select your battery state of charge sensor
   - **Solcast Solar Forecast Entity**: Select your Solcast forecast sensor
   - **Frank Energie Price Entity**: Select your current electricity price sensor
   - **Battery Capacity**: Enter your battery capacity in kWh
   - **Maximum Charge Rate**: Enter max charge rate in kW
   - **Maximum Discharge Rate**: Enter max discharge rate in kW
   - **Min/Max State of Charge**: Set safety limits (default: 20%-95%)

5. Click **Submit**

## Usage

### Entities

The integration creates the following entities:

#### Sensors
- `sensor.solax_energy_optimizer_next_action`: Shows the next recommended action (charge/discharge/idle)
- `sensor.solax_energy_optimizer_next_action_time`: When the next action will occur
- `sensor.solax_energy_optimizer_daily_cost`: Total energy cost today
- `sensor.solax_energy_optimizer_daily_savings`: Savings achieved today
- `sensor.solax_energy_optimizer_monthly_cost`: Total energy cost this month
- `sensor.solax_energy_optimizer_monthly_savings`: Savings achieved this month

#### Switches
- `switch.solax_energy_optimizer_automation_enabled`: Enable/disable automatic optimization
- `switch.solax_energy_optimizer_manual_override`: Temporarily override automation
- `switch.solax_energy_optimizer_dry_run`: Enable/disable dry run mode (testing without actual control)

#### Select
- `select.solax_energy_optimizer_strategy`: Choose optimization strategy

### Dry Run Mode

**IMPORTANT**: The integration starts in **dry run mode** by default for safety.

In dry run mode:
- ✅ All optimization logic runs normally
- ✅ Sensors show recommended actions
- ✅ Logs show what would be executed
- ❌ No actual battery control commands are sent

To enable actual battery control:
1. Test the integration in dry run mode first
2. Verify the recommended actions make sense
3. Turn off the dry run switch: `switch.solax_energy_optimizer_dry_run`
4. Monitor the system closely

**Note**: Currently, the integration only provides recommendations. To implement actual battery control, you'll need to add Solax Modbus service calls (see DEVELOPMENT.md).

### Services

#### `solax_energy_optimizer.trigger_optimization`
Manually trigger an immediate optimization cycle.

### Automations

The integration works autonomously, but you can create automations to:

1. **Notify on action changes**:
```yaml
automation:
  - alias: "Energy Action Notification"
    trigger:
      - platform: state
        entity_id: sensor.solax_energy_optimizer_next_action
    action:
      - service: notify.mobile_app
        data:
          message: "Energy optimizer action: {{ states('sensor.solax_energy_optimizer_next_action') }}"
```

2. **Adjust strategy based on conditions**:
```yaml
automation:
  - alias: "Night Mode - Grid Independence"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.solax_energy_optimizer_strategy
        data:
          option: "grid_independence"
```

## How It Works

The integration:

1. **Monitors** data from the three source integrations every 5 minutes
2. **Analyzes** current battery state, solar forecasts, and electricity prices
3. **Calculates** optimal charge/discharge actions based on the selected strategy
4. **Provides** recommendations through sensor entities
5. **Tracks** costs and savings based on actual usage

### Optimization Strategies

#### Minimize Cost
- Charges battery during low-price periods (bottom 25% of prices)
- Discharges battery during high-price periods (top 25% of prices)
- Remains idle during moderate price periods

#### Maximize Self-Consumption
- Ensures battery has capacity before solar production periods
- Prioritizes storing solar energy in battery
- Minimizes grid usage

#### Grid Independence
- Keeps battery charged to maximum safe level
- Only uses grid when battery and solar are insufficient
- Prioritizes battery and solar over grid

#### Balanced
- Charges when prices are below average by 10%
- Discharges when prices are above average by 10%
- Balances cost savings with self-consumption

## Troubleshooting

### Integration Not Loading
- Verify all prerequisite integrations are installed and working
- Check Home Assistant logs for errors
- Ensure entity IDs are correct in configuration

### No Optimization Actions
- Verify source entities have valid data
- Check that automation is enabled
- Ensure manual override is disabled

### Incorrect Cost Tracking
- Verify Frank Energie entity provides correct price data
- Check that battery capacity and charge/discharge rates are accurate

## Support

For issues, feature requests, or questions:
- Open an issue on [GitHub](https://github.com/xlith/ha-solar-energy-optimizer/issues)

## Contributing

Contributions are welcome! Please open a pull request with your changes.

## License

MIT License - see LICENSE file for details

## Disclaimer

This integration provides optimization recommendations based on available data. Actual energy savings may vary based on:
- Accuracy of solar forecasts
- Price volatility
- Household energy consumption patterns
- Battery and inverter characteristics

Always monitor your system's behavior and adjust settings as needed.
