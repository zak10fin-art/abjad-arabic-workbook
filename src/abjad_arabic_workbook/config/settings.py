"""Settings for abjad_arabic_workbook.

This module defines a small Settings dataclass and helpers to load
configuration from a JSON file and environment variables. It intentionally
depends only on the standard library so it can be used in minimal
environments.

Environment variable mapping:
- ABJAD_APP_NAME -> app_name
- ABJAD_DEBUG -> debug (true/1/yes -> True)
- ABJAD_DATA_DIR -> data_dir
- ABJAD_OUTPUT_DIR -> output_dir
- ABJAD_LOG_LEVEL -> log_level

Usage:
    from abjad_arabic_workbook.config import load_settings
    settings = load_settings(json_path="/etc/abjad/config.json")

The loading order is: if json_path is provided and exists, start from the
JSON values, then override with any environment variables present.
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
    app_name: str = "abjad_arabic_workbook"
    debug: bool = False
    data_dir: str = "data"
    output_dir: str = "output"
    log_level: str = "INFO"
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Settings":
        # Extract known fields and stash the rest in `extra`.
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
    """Load settings from an optional JSON file then override with env vars.

    Args:
        json_path: Path to a JSON file containing settings (optional).
        env_prefix: Environment variable prefix to use (default: ABJAD_).

    Returns:
        Settings instance.
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

    # Apply environment variables as overrides
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


__all__ = ["Settings", "load_settings"]
