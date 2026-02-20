# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Initial release of Solax Energy Optimizer
- Four optimization strategies: minimize cost, maximize self-consumption, grid independence, balanced
- Real-time monitoring with sensor entities (next action, last/next update time, daily/monthly cost and savings, decision reason, update count)
- Manual control with switch entities (automation enabled, manual override, dry run mode)
- Strategy selection with select entity
- Dry run mode enabled by default for safe testing
- Integration with Solax Modbus, Solcast Solar, and Frank Energie
- HACS compatibility
- Detailed calculation logging with real numbers for every optimization decision
- Human-readable decision reason sensor explaining each charging/discharging/idle decision

[Unreleased]: https://github.com/xlith/solax-energy-optimizer/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/xlith/solax-energy-optimizer/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/xlith/solax-energy-optimizer/releases/tag/v0.0.1
