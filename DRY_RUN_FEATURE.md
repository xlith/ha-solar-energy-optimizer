# Dry Run Feature

## Overview

The dry run feature allows you to test the energy optimization logic **without actually controlling your battery**. This is essential for:
- Testing the integration safely
- Verifying optimization decisions
- Debugging strategy behavior
- Understanding what actions would be taken

## Default Behavior

**IMPORTANT**: The integration starts in **dry run mode by default** for safety.

## How It Works

### When Dry Run is Enabled (Default)

1. ✅ All optimization algorithms run normally
2. ✅ Sensors show recommended actions
3. ✅ Next action and target SOC are calculated
4. ✅ Logs show what **would** be executed
5. ❌ No battery control commands are sent

### When Dry Run is Disabled

1. ✅ All optimization algorithms run normally
2. ✅ Sensors show recommended actions
3. ✅ Battery control commands **would** be sent (when implemented)
4. ⚠️ **Use with caution** - only after thorough testing

## Using Dry Run Mode

### Entity

- **Switch**: [`switch.solax_energy_optimizer_dry_run`](custom_components/solax_energy_optimizer/switch.py#L109-L145)
- **Default**: ON (enabled)
- **Icon**: mdi:test-tube

### Checking Dry Run Status

#### 1. Via Entity State
```yaml
# Check if dry run is enabled
{{ states('switch.solax_energy_optimizer_dry_run') }}
# Returns: 'on' or 'off'
```

#### 2. Via Sensor Attribute
The `next_action` sensor includes a `dry_run_mode` attribute:
```yaml
{{ state_attr('sensor.solax_energy_optimizer_next_action', 'dry_run_mode') }}
# Returns: true or false
```

#### 3. Via Logs
Settings → System → Logs, filter for `solax_energy_optimizer`:

**Dry Run Mode**:
```
INFO: DRY RUN MODE: Would execute charge (target SOC: 95%)
```

**Production Mode**:
```
INFO: PRODUCTION MODE: Executing charge (target SOC: 95%)
```

## Testing Workflow

### Step 1: Initial Testing (24-48 hours)

1. Keep dry run mode **enabled** (default)
2. Configure your settings
3. Choose a strategy
4. Monitor the logs and sensor states
5. Verify recommendations make sense

### Step 2: Analysis

1. Compare recommendations with:
   - Actual electricity prices
   - Solar forecast data
   - Battery state
2. Check if actions would be beneficial
3. Try different strategies
4. Adjust min/max SOC if needed

### Step 3: Production (Optional)

**Only proceed if**:
- You've tested for at least 24-48 hours
- Recommendations are sensible
- You've implemented inverter control (see DEVELOPMENT.md)

To enable production mode:
1. Turn off dry run: `switch.solax_energy_optimizer_dry_run`
2. Monitor closely for the first few cycles
3. Be ready to re-enable dry run if issues occur

## Code Implementation

### Files Modified

1. **[const.py](custom_components/solax_energy_optimizer/const.py)**:
   - Added `ENTITY_DRY_RUN` constant
   - Added `ATTR_DRY_RUN_MODE` attribute

2. **[coordinator.py](custom_components/solax_energy_optimizer/coordinator.py)**:
   - Added `_dry_run_mode` property (default: True)
   - Added `dry_run_mode` getter
   - Added `set_dry_run_mode()` setter
   - Added logging for dry run status
   - Added TODO for actual control implementation

3. **[switch.py](custom_components/solax_energy_optimizer/switch.py)**:
   - Added `DryRunSwitch` class
   - Integrated with coordinator

4. **[sensor.py](custom_components/solax_energy_optimizer/sensor.py)**:
   - Added dry_run_mode to next_action attributes

5. **[strings.json](custom_components/solax_energy_optimizer/strings.json)**:
   - Added "dry_run" translation

6. **Documentation**:
   - Updated [README.md](README.md)
   - Updated [INSTALLATION.md](INSTALLATION.md)
   - Updated [DEVELOPMENT.md](DEVELOPMENT.md)

### Code Locations

**Coordinator dry run check** ([coordinator.py:148-165](custom_components/solax_energy_optimizer/coordinator.py#L148-L165)):
```python
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
        # TODO: Implement actual inverter control
        # await self._execute_action(data.next_action, data.target_soc)
```

## Example Automation

### Alert When Dry Run is Disabled

```yaml
automation:
  - alias: "Alert - Dry Run Disabled"
    description: "Notify when dry run mode is turned off"
    trigger:
      - platform: state
        entity_id: switch.solax_energy_optimizer_dry_run
        to: "off"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Energy Optimizer Alert"
          message: "Dry run mode has been disabled. Battery control is now active!"
          data:
            priority: high
            tag: "energy_optimizer_dry_run"
```

### Re-enable Dry Run at Startup

```yaml
automation:
  - alias: "Enable Dry Run on Startup"
    description: "Ensure dry run mode is enabled when HA starts"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.solax_energy_optimizer_dry_run
```

## Benefits

1. **Safety**: Test without risking battery damage
2. **Debugging**: Understand optimization logic
3. **Validation**: Verify strategies work as expected
4. **Learning**: See what actions would be taken before enabling control
5. **Development**: Implement and test inverter control safely

## Next Steps

1. **Test thoroughly** in dry run mode
2. **Implement inverter control** (see [DEVELOPMENT.md](DEVELOPMENT.md))
3. **Test control in dry run** with logging
4. **Gradually disable dry run** with monitoring
5. **Monitor production** mode closely

## FAQ

**Q: Can I use the integration without disabling dry run?**
A: Yes! It will provide valuable recommendations even without actual control.

**Q: What happens if I disable dry run without implementing inverter control?**
A: Nothing changes - the TODO comment will just log "PRODUCTION MODE" but no control commands are sent yet.

**Q: Should I ever disable dry run?**
A: Only after:
1. Testing for 24-48 hours minimum
2. Verifying recommendations are sensible
3. Implementing actual inverter control code
4. Being ready to monitor closely

**Q: How do I implement actual inverter control?**
A: See [DEVELOPMENT.md](DEVELOPMENT.md) section 3 for implementation details.

## Safety Notes

- ⚠️ Dry run mode is a safety feature, not a guarantee
- ⚠️ Always test thoroughly before disabling
- ⚠️ Monitor logs and behavior continuously
- ⚠️ Be prepared to re-enable dry run if issues occur
- ⚠️ Understand your battery and inverter specifications
- ⚠️ Consider battery health and warranty implications
