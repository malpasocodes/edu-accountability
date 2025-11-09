"""Feature flags for gradual rollouts."""

from __future__ import annotations

import os
from pathlib import Path


def _load_env_file(filename: str = ".env") -> None:
    """Load key/value pairs from a project-level .env file if present."""
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / filename
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


_load_env_file()


USE_CANONICAL_GRAD_DATA = _as_bool(
    os.getenv("USE_CANONICAL_GRAD_DATA"),
    default=True,
)
"""Toggle for powering app components with canonical graduation data."""

ENABLE_CANONICAL_IPEDS_SECTION = _as_bool(
    os.getenv("ENABLE_CANONICAL_IPEDS_SECTION"),
    default=False,
)
"""Enables the Canonical IPEDS section in the navigation + UI."""

ENABLE_CANONICAL_SCORECARD_SECTION = _as_bool(
    os.getenv("ENABLE_CANONICAL_SCORECARD_SECTION"),
    default=False,
)
"""Enables the Canonical Scorecard section in the navigation + UI."""
