"""Compatibility configuration for the abjad_production package.

This module provides a simple JSON + environment loader and a
Config compatibility wrapper used by the production engine (generate_workbook.py).
It intentionally uses only the standard library so it has no external
dependencies.

Environment variables (prefix ABJAD_ by default):
- ABJAD_APP_NAME, ABJAD_DEBUG, ABJAD_DATA_DIR, ABJAD_OUTPUT_DIR, ABJAD_LOG_LEVEL

The Config class exposes attributes used across the abjad_production codebase
(e.g. OUTPUT_DIR, OUTPUT_SVG_DIR, OUTPUT_PDF_DIR, OUTPUT_PNG_DIR, DATA_DIR,
DEBUG, LOG_LEVEL) and is constructed with optional json_path and env_prefix
arguments.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    val = value.strip().lower()
    if val in {"1", "true", "yes", "on"}:
        return True
    if val in {"0", "false", "no", "off"}:
        return False
    return None


@dataclass
class Settings:
    app_name: str = "abjad_production"
    debug: bool = False
    data_dir: str = "data"
    output_dir: str = "output"
    log_level: str = "INFO"
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Settings":
        fields = {f.name for f in cls.__dataclass_fields__.values()}
        known: Dict[str, Any] = {}
        extra: Dict[str, Any] = {}
        for k, v in d.items():
            if k in fields:
                known[k] = v
            else:
                extra[k] = v
        return cls(**known, extra=extra)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _env_mapping(prefix: str = "ABJAD_") -> Dict[str, Optional[str]]:
    return {
        "app_name": os.getenv(prefix + "APP_NAME"),
        "debug": os.getenv(prefix + "DEBUG"),
        "data_dir": os.getenv(prefix + "DATA_DIR"),
        "output_dir": os.getenv(prefix + "OUTPUT_DIR"),
        "log_level": os.getenv(prefix + "LOG_LEVEL"),
    }


def load_settings(json_path: Optional[str] = None, env_prefix: str = "ABJAD_") -> Settings:
    """Load settings from optional JSON file then override with env vars.

    Returns a Settings instance.
    """
    data: Dict[str, Any] = {}

    if json_path:
        p = Path(json_path)
        if p.exists():
            try:
                with p.open("r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                if isinstance(loaded, dict):
                    data.update(loaded)
            except Exception:
                # Fail silently and fall back to env-only if JSON is malformed
                pass

    env = _env_mapping(env_prefix)
    if env["app_name"] is not None:
        data["app_name"] = env["app_name"]
    if env["debug"] is not None:
        parsed = _parse_bool(env["debug"])
        if parsed is not None:
            data["debug"] = parsed
    if env["data_dir"] is not None:
        data["data_dir"] = env["data_dir"]
    if env["output_dir"] is not None:
        data["output_dir"] = env["output_dir"]
    if env["log_level"] is not None:
        data["log_level"] = env["log_level"]

    return Settings.from_dict(data)


class Config:
    """Compatibility wrapper used by abjad_production engine.

    Constructor args:
      json_path: optional path to JSON file with settings
      env_prefix: environment variable prefix (default ABJAD_)
    """

    def __init__(self, json_path: Optional[str] = None, env_prefix: str = "ABJAD_"):
        settings = load_settings(json_path=json_path, env_prefix=env_prefix)

        # Core directories
        self.DATA_DIR = settings.data_dir
        self.OUTPUT_DIR = settings.output_dir

        # Backwards-compatible subdirectories used by the engine
        self.OUTPUT_SVG_DIR = str(Path(self.OUTPUT_DIR) / "svg")
        self.OUTPUT_PNG_DIR = str(Path(self.OUTPUT_DIR) / "png")
        self.OUTPUT_PDF_DIR = str(Path(self.OUTPUT_DIR) / "pdf")

        # Other flags / metadata
        self.DEBUG = settings.debug
        self.LOG_LEVEL = settings.log_level

        # Lowercase aliases (some modules may use these)
        self.output_dir = self.OUTPUT_DIR
        self.data_dir = self.DATA_DIR
        self.debug = self.DEBUG
        self.log_level = self.LOG_LEVEL

        # Expose raw settings
        self._raw = settings

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "DATA_DIR": self.DATA_DIR,
            "OUTPUT_DIR": self.OUTPUT_DIR,
            "OUTPUT_SVG_DIR": self.OUTPUT_SVG_DIR,
            "OUTPUT_PNG_DIR": self.OUTPUT_PNG_DIR,
            "OUTPUT_PDF_DIR": self.OUTPUT_PDF_DIR,
            "DEBUG": self.DEBUG,
            "LOG_LEVEL": self.LOG_LEVEL,
        }
        d.update(self._raw.extra)
        return d


__all__ = ["Config", "Settings", "load_settings"]
