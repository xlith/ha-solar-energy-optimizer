# Contributing to Solar Energy Optimizer

Thank you for considering contributing to Solar Energy Optimizer! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful and constructive in all interactions. We want to maintain a welcoming environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. Check the [existing issues](https://github.com/xlith/ha-solar-energy-optimizer/issues) to avoid duplicates
2. Verify you're using the latest version
3. Check the logs for error messages
4. Try to reproduce the issue in dry run mode

When filing a bug report, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Home Assistant version
- Integration version
- Relevant log output
- Configuration (sanitized)

### Suggesting Features

Feature requests are welcome! When suggesting a feature:
1. Check if it's already been suggested
2. Explain the use case
3. Describe the desired behavior
4. Consider if it benefits other users
5. Provide implementation ideas if you have them

### Pull Requests

1. **Fork the repository** and create a new branch
2. **Make your changes** following the guidelines below
3. **Test thoroughly** in a local Home Assistant instance
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.12+
- Home Assistant 2024.1+
- Git

### Local Development

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ha-solar-energy-optimizer.git
   cd ha-solar-energy-optimizer
   ```

2. Create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Copy to your Home Assistant test instance:
   ```bash
   cp -r custom_components/solax_energy_optimizer /path/to/homeassistant/config/custom_components/
   ```

4. Restart Home Assistant and test

### Testing Locally

Before submitting:
- [ ] Test in dry run mode first
- [ ] Check Home Assistant logs for errors
- [ ] Verify all entities appear correctly
- [ ] Test configuration flow
- [ ] Try different optimization strategies
- [ ] Ensure no new warnings in logs

## Code Guidelines

### Python Style

Follow Home Assistant's coding standards:
- Use type hints
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Home Assistant Specific

- Use `_attr_` properties for entity attributes
- Implement `async` methods properly
- Use coordinator pattern for data updates
- Follow entity naming conventions
- Use translations (`strings.json`)
- Log at appropriate levels (debug, info, warning, error)

### File Structure

When adding new files, follow the standard structure:
```
custom_components/solax_energy_optimizer/
├── __init__.py          # Setup and teardown
├── config_flow.py       # UI configuration
├── const.py            # Constants
├── coordinator.py      # Data management
├── sensor.py           # Sensor entities
├── switch.py           # Switch entities
├── select.py           # Select entities
├── strings.json        # Translations
└── services.yaml       # Service definitions
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add new optimization strategy
fix: correct battery SOC calculation
docs: update installation guide
refactor: simplify coordinator logic
test: add tests for config flow
```

Prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Documentation

Update documentation when:
- Adding new features
- Changing configuration options
- Modifying behavior
- Adding new entities
- Changing requirements

Files to update:
- `README.md` - User-facing documentation
- `INSTALLATION.md` - Setup instructions
- `DEVELOPMENT.md` - Technical details
- `CHANGELOG.md` - Record changes
- `strings.json` - Translations

## Testing

### Manual Testing Checklist

- [ ] Installation from scratch works
- [ ] Configuration flow completes successfully
- [ ] All entities appear and update
- [ ] Strategies work as expected
- [ ] Switches function correctly
- [ ] Services can be called
- [ ] Logs show no errors
- [ ] Dry run mode works
- [ ] Uninstallation is clean

### What to Test

1. **Config Flow**:
   - Valid entity selection
   - Invalid entity handling
   - Field validation
   - Unique ID generation

2. **Coordinator**:
   - Data fetching from source entities
   - Optimization algorithm execution
   - Error handling
   - Update interval

3. **Entities**:
   - State updates
   - Attributes
   - Availability
   - Icons and translations

4. **Services**:
   - Service calls work
   - Parameters validated
   - Error handling

## Release Process

Maintainers follow this process for releases:

1. Update `CHANGELOG.md` with changes
2. Update version in `manifest.json`
3. Create a git tag: `git tag v1.0.0`
4. Push tag: `git push --tags`
5. Create GitHub release
6. GitHub Actions builds and publishes

## Questions?

If you have questions:
1. Check the [documentation](README.md)
2. Look for [existing issues](https://github.com/xlith/ha-solar-energy-optimizer/issues)
3. Ask in [Home Assistant Community](https://community.home-assistant.io/)
4. Open a new issue

## Recognition

Contributors will be recognized in the README and release notes. Thank you for your contributions!
