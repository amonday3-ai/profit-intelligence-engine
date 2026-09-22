"""Core analysis functions for the Profit Intelligence Engine portfolio demo."""

from .analysis import analyze_inventory, scenario_table
from .demo_data import build_demo_data

__all__ = [
    "analyze_inventory",
    "scenario_table",
    "build_demo_data",
]
