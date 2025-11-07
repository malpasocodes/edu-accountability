"""Feature flags for gradual rollouts."""

from __future__ import annotations

import os


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


USE_CANONICAL_GRAD_DATA = _as_bool(
    os.getenv("USE_CANONICAL_GRAD_DATA"),
    default=True,
)
"""Toggle for powering app components with canonical graduation data."""
