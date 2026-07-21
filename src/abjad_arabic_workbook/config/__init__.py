"""Configuration package for abjad_arabic_workbook.

This package provides a lightweight Settings dataclass that can be
constructed from environment variables or a JSON file. The implementation
uses only the Python standard library so it has no external dependencies.
"""

from .settings import Settings, load_settings

__all__ = ["Settings", "load_settings"]
