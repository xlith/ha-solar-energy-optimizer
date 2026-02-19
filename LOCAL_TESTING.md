# Local Testing Guide

This guide shows you how to test the GitHub Actions workflows locally before pushing to GitHub.

## Prerequisites

Install the following tools:

```bash
# Install act (for running GitHub Actions locally)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Install Python tools for validation
pip install ruff black isort homeassistant voluptuous
```

## Testing GitHub Actions Locally

### 1. Test HACS Validation Workflow

```bash
# Dry run to see what would happen
act -n -W .github/workflows/hacs-validation.yml

# Actually run the workflow
act -W .github/workflows/hacs-validation.yml

# Run specific job
act -j validate -W .github/workflows/hacs-validation.yml
```

### 2. Test Code Quality Workflow

```bash
# Run all quality checks
act -W .github/workflows/quality.yml

# Run specific job
act -j lint -W .github/workflows/quality.yml
act -j validate-python -W .github/workflows/quality.yml
act -j validate-json -W .github/workflows/quality.yml
```

### 3. Test Release Workflow

```bash
# Test release workflow (won't upload to GitHub)
act release -W .github/workflows/release.yml
```

## Manual Validation

### Validate JSON Files

```bash
# Validate manifest.json
python3 -m json.tool custom_components/solax_energy_optimizer/manifest.json

# Validate strings.json
python3 -m json.tool custom_components/solax_energy_optimizer/strings.json

# Validate hacs.json
python3 -m json.tool hacs.json
```

### Check Python Syntax

```bash
# Compile all Python files
python3 -m py_compile custom_components/solax_energy_optimizer/*.py

# Check imports
python3 << 'EOF'
import sys
sys.path.insert(0, 'custom_components/solax_energy_optimizer')
import const
import coordinator
print('✓ All modules can be imported')
EOF
```

### Run Linting

```bash
# Ruff (fast Python linter)
ruff check custom_components/solax_energy_optimizer/

# Black (code formatter)
black --check custom_components/solax_energy_optimizer/

# isort (import sorting)
isort --check-only custom_components/solax_energy_optimizer/
```

### Format Code

```bash
# Format with black
black custom_components/solax_energy_optimizer/

# Sort imports
isort custom_components/solax_energy_optimizer/

# Auto-fix with ruff
ruff check --fix custom_components/solax_energy_optimizer/
```

## Testing in Home Assistant

### 1. Copy Integration to HA

```bash
# Copy to your HA config directory
cp -r custom_components/solax_energy_optimizer /path/to/homeassistant/config/custom_components/

# Or create a symlink for easier development
ln -s $(pwd)/custom_components/solax_energy_optimizer /path/to/homeassistant/config/custom_components/
```

### 2. Restart Home Assistant

```bash
# If using Docker
docker restart homeassistant

# If using systemd
sudo systemctl restart home-assistant@homeassistant
```

### 3. Check Logs

```bash
# Tail the log file
tail -f /path/to/homeassistant/config/home-assistant.log | grep solax_energy_optimizer

# Or use Home Assistant UI:
# Settings → System → Logs → Filter: "solax_energy_optimizer"
```

### 4. Test Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "Solax Energy Optimizer"
4. Fill in the configuration
5. Verify all entities appear

### 5. Test Functionality

```yaml
# Test in Developer Tools → Services

# Trigger optimization
service: solax_energy_optimizer.trigger_optimization
data: {}

# Check entity states
# Developer Tools → States
# Filter: solax_energy_optimizer
```

## Integration Testing Checklist

- [ ] **Installation**
  - [ ] Integration appears in "Add Integration" list
  - [ ] Configuration flow completes without errors
  - [ ] Unique ID is set correctly
  - [ ] Device is created in device registry

- [ ] **Entities**
  - [ ] All 6 sensors appear
  - [ ] All 3 switches appear
  - [ ] Select entity appears
  - [ ] Entity IDs are correct
  - [ ] Entity names are translated

- [ ] **Functionality**
  - [ ] Coordinator fetches data every 5 minutes
  - [ ] Optimization runs when automation is enabled
  - [ ] Dry run mode works (default)
  - [ ] Strategy selection changes behavior
  - [ ] Switches toggle correctly
  - [ ] Service calls work

- [ ] **Dry Run Mode**
  - [ ] Defaults to ON (enabled)
  - [ ] Logs show "DRY RUN MODE: Would execute..."
  - [ ] next_action sensor includes dry_run_mode attribute
  - [ ] Toggling switch changes behavior

- [ ] **Error Handling**
  - [ ] Missing source entities handled gracefully
  - [ ] Invalid data doesn't crash integration
  - [ ] Logs show appropriate warnings
  - [ ] Integration can be reloaded

- [ ] **Uninstallation**
  - [ ] Integration can be removed cleanly
  - [ ] Entities are removed
  - [ ] Device is removed
  - [ ] No errors in logs after removal

## Common Issues

### Integration Won't Load

```bash
# Check for Python syntax errors
python3 -m py_compile custom_components/solax_energy_optimizer/*.py

# Check imports
grep -r "^import\|^from" custom_components/solax_energy_optimizer/*.py

# Check manifest
python3 -c "import json; json.load(open('custom_components/solax_energy_optimizer/manifest.json'))"
```

### Entities Not Appearing

```bash
# Check logs for errors
grep -i "solax_energy_optimizer" /path/to/homeassistant/config/home-assistant.log

# Verify coordinator is updating
grep -i "async_update_data" /path/to/homeassistant/config/home-assistant.log
```

### Coordinator Not Running

```bash
# Check if config entry is loaded
grep -i "async_setup_entry" /path/to/homeassistant/config/home-assistant.log

# Verify update interval
grep -i "update_interval" /path/to/homeassistant/config/home-assistant.log
```

## Debug Logging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.solax_energy_optimizer: debug
    custom_components.solax_energy_optimizer.coordinator: debug
    custom_components.solax_energy_optimizer.sensor: debug
```

## Performance Testing

Monitor resource usage:

```bash
# Check memory usage
grep -i "memory" /path/to/homeassistant/config/home-assistant.log

# Check update times
grep -i "Finished fetching" /path/to/homeassistant/config/home-assistant.log
```

## Before Pushing

Run this checklist before pushing to GitHub:

```bash
# 1. Validate JSON
python3 -m json.tool custom_components/solax_energy_optimizer/manifest.json > /dev/null
python3 -m json.tool custom_components/solax_energy_optimizer/strings.json > /dev/null
python3 -m json.tool hacs.json > /dev/null

# 2. Check Python syntax
python3 -m py_compile custom_components/solax_energy_optimizer/*.py

# 3. Format code
black custom_components/solax_energy_optimizer/
isort custom_components/solax_energy_optimizer/

# 4. Run linting
ruff check custom_components/solax_energy_optimizer/

# 5. Test in Home Assistant
# (Manual step - verify in running HA instance)

# 6. Update CHANGELOG
# (Add your changes to CHANGELOG.md)

# 7. Commit
git add .
git commit -m "feat: your feature description"
git push
```

## Next Steps

After local testing passes:
1. Push to GitHub
2. GitHub Actions will run automatically
3. Review action results in the "Actions" tab
4. Fix any issues found by CI
5. Create a pull request or release

## Tips

- Use `act --list` to see all available workflows
- Use `act -n` for dry runs (shows what would run)
- Use `act -j job_name` to run specific jobs
- Set `GITHUB_TOKEN` for authenticated API calls
- Use `--verbose` for detailed output
- Check `.github/workflows/*.yml` for workflow definitions
