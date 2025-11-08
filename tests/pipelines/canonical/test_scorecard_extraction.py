"""Minimal tests for ScorecardExtractor end-to-end on a synthetic MERGED csv."""

from pathlib import Path
import zipfile
import io

import pandas as pd

from src.pipelines.canonical.scorecard.extraction import (
    ScorecardExtractionConfig,
    ScorecardExtractor,
)


def _make_zip_with_merged(tmp_path: Path) -> Path:
    # Create a small MERGED2023_24_PP.csv content
    df = pd.DataFrame(
        {
            "UNITID": [111100, 222200],
            "INSTNM": ["Alpha", "Beta"],
            "STABBR": ["CA", "NY"],
            "CONTROL": [1, 2],
            "PREDDEG": [3, 2],
            "GRAD_DEBT_MDN": [31553, 28000],
            "BBRR3_FED_UG_DFLT": [0.11, 0.08],
            "BBRR3_FED_UG_DLNQ": [0.05, 0.06],
            "BBRR3_FED_UG_FBR": [0.32, 0.35],
            "BBRR3_FED_UG_DFR": [0.13, 0.10],
            "BBRR3_FED_UG_NOPROG": [0.28, 0.30],
            "BBRR3_FED_UG_MAKEPROG": [0.07, 0.08],
            "BBRR3_FED_UG_PAIDINFULL": [0.02, 0.02],
            "BBRR3_FED_UG_DISCHARGE": [0.01, 0.01],
        }
    )
    csv_bytes = df.to_csv(index=False).encode()
    zip_path = tmp_path / "College_Scorecard_Raw_Data_05192025.zip"
    # Place under a folder with expected structure
    inner_name = "College_Scorecard_Raw_Data_05192025/MERGED2023_24_PP.csv"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(inner_name, csv_bytes)
    return zip_path


def test_extractor_builds_long_table(tmp_path):
    zpath = _make_zip_with_merged(tmp_path)
    output = tmp_path / "scorecard_long.parquet"
    cfg = ScorecardExtractionConfig(zip_path=zpath, output_path=output)
    df = ScorecardExtractor(cfg).run(write_output=True)

    assert not df.empty
    assert set(df["year"].unique()) == {2024}
    assert "median_debt_completers" in df.columns
    assert "repay_3yr_forbearance" in df.columns
    assert output.exists()

