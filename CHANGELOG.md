# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-21

### Added
- Provider-agnostic adapter layer (`adapters/` package) with abstract base classes
  `InverterAdapter`, `SolarForecastAdapter`, and `PriceAdapter`
- Built-in adapters for Solax Modbus, Solcast Solar, and Frank Energie
- Generic adapters (`GenericSocEntityAdapter`, `GenericForecastAdapter`,
  `GenericPriceAdapter`) supporting any inverter, solar forecast, or price
  provider via configurable field mapping
- Config flow expanded to 4 steps with provider type selection; supports
  Solax Modbus, Nordpool, Tibber, aWATTar, Amber Electric, and generic providers
- `async_migrate_entry` for automatic silent migration from v1 config entries
- 92 unit tests covering all adapters and factory functions

### Changed
- Renamed integration from "Solax Energy Optimizer" to "Solar Energy Optimizer"
- Config entry schema bumped to VERSION 2 (auto-migrated from v1)
- Removed `after_dependencies` lock-in from `manifest.json`; integration no
  longer requires Solax Modbus, Solcast, or Frank Energie to be installed
- UI setup flow is now multi-step (inverter → forecast → prices → battery specs)

## [0.0.4] - 2026-02-20

### Added

### Changed

### Fixed

### Security

## [0.0.3] - 2026-02-20

### Added

### Changed

### Fixed

### Security

## [0.0.2] - 2026-02-20

### Added

### Changed

### Fixed

### Security

## [0.0.1] - 2026-02-20

### Added
- Initial release of Solar Energy Optimizer
- Four optimization strategies: minimize cost, maximize self-consumption, grid independence, balanced
- Real-time monitoring with sensor entities (next action, last/next update time, daily/monthly cost and savings, decision reason, update count)
- Manual control with switch entities (automation enabled, manual override, dry run mode)
- Strategy selection with select entity
- Dry run mode enabled by default for safe testing
- Integration with Solax Modbus, Solcast Solar, and Frank Energie
- HACS compatibility
- Detailed calculation logging with real numbers for every optimization decision
- Human-readable decision reason sensor explaining each charging/discharging/idle decision

[Unreleased]: https://github.com/xlith/ha-solar-energy-optimizer/compare/v0.0.4...HEAD
[0.0.4]: https://github.com/xlith/ha-solar-energy-optimizer/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/xlith/ha-solar-energy-optimizer/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/xlith/ha-solar-energy-optimizer/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/xlith/ha-solar-energy-optimizer/releases/tag/v0.0.1
