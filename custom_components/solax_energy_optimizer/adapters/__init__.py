"""Provider adapters for the Solar Energy Optimizer integration.

This package provides an abstraction layer between Home Assistant entity states
and the optimizer's normalized data model. Three adapter types exist:

- InverterAdapter   — supplies battery State-of-Charge (0–100 %)
- SolarForecastAdapter — supplies solar production forecasts
- PriceAdapter      — supplies electricity price schedules

Built-in adapters cover Solax Modbus, Solcast, and Frank Energie out of the
box. Generic adapters (GenericSocEntityAdapter, GenericForecastAdapter,
GenericPriceAdapter) work with any integration via configurable field mapping.

To add support for a new provider:
1. Create a new file in this package implementing the relevant ABC from base.py
2. Add a type constant to const.py
3. Add a factory branch in factory.py
4. Register the option in config_flow.py and strings.json
"""
from .base import InverterAdapter, PriceAdapter, SolarForecastAdapter
from .factory import build_forecast_adapter, build_inverter_adapter, build_price_adapter
from .frank_energie import FrankEnergieAdapter
from .generic_forecast import ForecastFieldMap, GenericForecastAdapter
from .generic_inverter import GenericSocEntityAdapter
from .generic_price import GenericPriceAdapter, PriceFieldMap
from .solax_modbus import SolaxModbusInverterAdapter
from .solcast import SolcastSolarForecastAdapter

__all__ = [
    "InverterAdapter",
    "SolarForecastAdapter",
    "PriceAdapter",
    "SolaxModbusInverterAdapter",
    "GenericSocEntityAdapter",
    "SolcastSolarForecastAdapter",
    "GenericForecastAdapter",
    "ForecastFieldMap",
    "FrankEnergieAdapter",
    "GenericPriceAdapter",
    "PriceFieldMap",
    "build_inverter_adapter",
    "build_forecast_adapter",
    "build_price_adapter",
]
