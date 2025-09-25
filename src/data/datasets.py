"""Data-loading utilities for processed ACT datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATASETS: Dict[str, Path] = {
    "cost_vs_grad": PROCESSED_DIR / "tuition_vs_graduation.csv",
}


@st.cache_data(show_spinner=False)
def _load_csv(path: str, mtime: float) -> pd.DataFrame:
    return pd.read_csv(path)


def load_processed(name: str) -> pd.DataFrame:
    """Load a named processed dataset from disk."""

    path = PROCESSED_DATASETS[name]
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return _load_csv(str(path), path.stat().st_mtime)
