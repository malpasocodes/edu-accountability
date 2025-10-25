"""
Unit tests for Earnings Premium calculations.

Tests the risk categorization logic, earnings margin calculations,
and data loading functions.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


# Helper function to categorize risk (matches build_ep_metrics.py logic)
def categorize_risk(margin):
    """Categorize risk level based on earnings margin."""
    if pd.isna(margin):
        return 'No Data'
    elif margin > 0.50:
        return 'Low Risk'
    elif margin > 0.20:
        return 'Moderate Risk'
    elif margin > 0:
        return 'High Risk'
    else:
        return 'Critical Risk'


# Test cases for risk categorization
class TestRiskCategorization:
    """Test risk level assignment logic."""

    def test_low_risk_threshold(self):
        """Test low risk boundary (margin > 50%)."""
        assert categorize_risk(0.51) == 'Low Risk'
        assert categorize_risk(0.50001) == 'Low Risk'
        assert categorize_risk(1.0) == 'Low Risk'
        assert categorize_risk(2.0) == 'Low Risk'

    def test_moderate_risk_threshold(self):
        """Test moderate risk boundaries (20% < margin <= 50%)."""
        assert categorize_risk(0.50) == 'Moderate Risk'
        assert categorize_risk(0.40) == 'Moderate Risk'
        assert categorize_risk(0.30) == 'Moderate Risk'
        assert categorize_risk(0.21) == 'Moderate Risk'
        assert categorize_risk(0.20001) == 'Moderate Risk'

    def test_high_risk_threshold(self):
        """Test high risk boundaries (0% < margin <= 20%)."""
        assert categorize_risk(0.20) == 'High Risk'
        assert categorize_risk(0.15) == 'High Risk'
        assert categorize_risk(0.10) == 'High Risk'
        assert categorize_risk(0.05) == 'High Risk'
        assert categorize_risk(0.01) == 'High Risk'
        assert categorize_risk(0.0001) == 'High Risk'

    def test_critical_risk_threshold(self):
        """Test critical risk (margin <= 0%)."""
        assert categorize_risk(0.0) == 'Critical Risk'
        assert categorize_risk(-0.01) == 'Critical Risk'
        assert categorize_risk(-0.10) == 'Critical Risk'
        assert categorize_risk(-0.50) == 'Critical Risk'
        assert categorize_risk(-1.0) == 'Critical Risk'

    def test_no_data_case(self):
        """Test missing data handling."""
        assert categorize_risk(None) == 'No Data'
        assert categorize_risk(np.nan) == 'No Data'
        assert categorize_risk(pd.NA) == 'No Data'

    def test_edge_cases(self):
        """Test exact boundary values."""
        # Exactly at 50% boundary -> Moderate Risk
        assert categorize_risk(0.5) == 'Moderate Risk'

        # Exactly at 20% boundary -> High Risk
        assert categorize_risk(0.2) == 'High Risk'

        # Exactly at 0% boundary -> Critical Risk
        assert categorize_risk(0.0) == 'Critical Risk'


class TestEarningsMarginCalculation:
    """Test earnings margin calculation logic."""

    def test_basic_margin_calculation(self):
        """Test basic margin formula: (earnings - threshold) / threshold."""
        # Example: $50k earnings, $30k threshold
        earnings = 50000
        threshold = 30000
        expected_margin = (50000 - 30000) / 30000  # = 0.6667
        calculated_margin = (earnings - threshold) / threshold

        assert abs(calculated_margin - expected_margin) < 0.0001
        assert abs(calculated_margin - 0.6667) < 0.001

    def test_margin_equals_100_percent(self):
        """Test when earnings are double the threshold (100% margin)."""
        earnings = 60000
        threshold = 30000
        margin = (earnings - threshold) / threshold

        assert abs(margin - 1.0) < 0.0001
        assert categorize_risk(margin) == 'Low Risk'

    def test_margin_equals_zero(self):
        """Test when earnings exactly equal threshold (0% margin)."""
        earnings = 30000
        threshold = 30000
        margin = (earnings - threshold) / threshold

        assert abs(margin - 0.0) < 0.0001
        assert categorize_risk(margin) == 'Critical Risk'

    def test_negative_margin(self):
        """Test when earnings are below threshold (negative margin)."""
        earnings = 25000
        threshold = 30000
        margin = (earnings - threshold) / threshold

        assert margin < 0
        assert abs(margin - (-0.1667)) < 0.001
        assert categorize_risk(margin) == 'Critical Risk'

    def test_percentage_conversion(self):
        """Test converting margin to percentage for display."""
        earnings = 45000
        threshold = 30000
        margin = (earnings - threshold) / threshold
        margin_pct = margin * 100

        assert abs(margin_pct - 50.0) < 0.1
        assert categorize_risk(margin) == 'Moderate Risk'


class TestRealWorldExamples:
    """Test with realistic institution examples."""

    def test_harvard_example(self):
        """Test Harvard-like institution (high earnings, low risk)."""
        # Harvard median earnings ~$95k, CA threshold ~$32k
        earnings = 95000
        threshold = 32476
        margin = (earnings - threshold) / threshold

        assert margin > 1.9  # Over 190% margin
        assert categorize_risk(margin) == 'Low Risk'

    def test_ucla_example(self):
        """Test UCLA-like institution (good earnings, low risk)."""
        # UCLA median earnings ~$70k, CA threshold ~$32k
        earnings = 70700
        threshold = 32476
        margin = (earnings - threshold) / threshold

        assert margin > 1.1  # Over 110% margin
        assert categorize_risk(margin) == 'Low Risk'

    def test_community_college_example(self):
        """Test community college (near threshold, high/critical risk)."""
        # Community college earnings ~$31k, CA threshold ~$32k
        earnings = 31000
        threshold = 32476
        margin = (earnings - threshold) / threshold

        assert margin < 0  # Below threshold
        assert categorize_risk(margin) == 'Critical Risk'

    def test_for_profit_example(self):
        """Test for-profit institution (low earnings, critical risk)."""
        # For-profit earnings ~$28k, FL threshold ~$30k
        earnings = 28400
        threshold = 29609
        margin = (earnings - threshold) / threshold

        assert margin < 0  # Below threshold
        assert categorize_risk(margin) == 'Critical Risk'

    def test_state_threshold_variation(self):
        """Test how different state thresholds affect risk."""
        # Same institution with $35k earnings
        earnings = 35000

        # Mississippi threshold (lowest at $27,362)
        ms_threshold = 27362
        ms_margin = (earnings - ms_threshold) / ms_threshold
        assert categorize_risk(ms_margin) == 'Low Risk'  # 27.9% margin

        # New Hampshire threshold (highest at $37,850)
        nh_threshold = 37850
        nh_margin = (earnings - nh_threshold) / nh_threshold
        assert categorize_risk(nh_margin) == 'Critical Risk'  # -7.5% margin


class TestDataIntegrity:
    """Test data loading and integrity."""

    def test_ep_data_exists(self):
        """Test that EP analysis Parquet file exists."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        assert data_path.exists(), "EP analysis data file not found"

    def test_ep_data_loadable(self):
        """Test that EP data can be loaded."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        assert not df.empty, "EP data is empty"
        assert len(df) > 1000, f"Expected >1000 institutions, got {len(df)}"

    def test_required_columns_present(self):
        """Test that all required columns are present."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        required_cols = [
            'UnitID', 'institution', 'STABBR',
            'median_earnings', 'Threshold', 'earnings_margin', 'earnings_margin_pct',
            'risk_level', 'risk_level_numeric'
        ]

        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"

    def test_risk_levels_valid(self):
        """Test that risk levels are valid categories."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        valid_risk_levels = {'Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk', 'No Data'}
        actual_risk_levels = set(df['risk_level'].unique())

        assert actual_risk_levels.issubset(valid_risk_levels), \
            f"Invalid risk levels found: {actual_risk_levels - valid_risk_levels}"

    def test_earnings_margin_consistency(self):
        """Test that earnings margin matches calculated values."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        # Sample 100 random institutions with data
        sample = df[df['risk_level'] != 'No Data'].sample(min(100, len(df)), random_state=42)

        for _, row in sample.iterrows():
            # Recalculate margin
            expected_margin = (row['median_earnings'] - row['Threshold']) / row['Threshold']

            # Check if calculated margin matches stored margin
            if pd.notna(expected_margin):
                assert abs(row['earnings_margin'] - expected_margin) < 0.001, \
                    f"Margin mismatch for {row['institution']}"

    def test_risk_categorization_consistency(self):
        """Test that risk levels match the categorization logic."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        # Sample institutions and verify risk categorization
        sample = df.sample(min(100, len(df)), random_state=42)

        for _, row in sample.iterrows():
            expected_risk = categorize_risk(row['earnings_margin'])
            actual_risk = row['risk_level']

            assert expected_risk == actual_risk, \
                f"Risk mismatch for {row['institution']}: expected {expected_risk}, got {actual_risk}"


class TestDataQuality:
    """Test data quality and realistic ranges."""

    def test_earnings_in_reasonable_range(self):
        """Test that earnings are in reasonable range."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        earnings_with_data = df[df['median_earnings'].notna()]['median_earnings']

        # Earnings should be between $5k and $200k
        assert earnings_with_data.min() > 5000, f"Unrealistically low earnings: ${earnings_with_data.min()}"
        assert earnings_with_data.max() < 200000, f"Unrealistically high earnings: ${earnings_with_data.max()}"

    def test_thresholds_match_federal_register(self):
        """Test that thresholds are in expected range."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        thresholds = df['Threshold'].dropna()

        # Federal Register 2024 thresholds range: $27,362 (MS) to $37,850 (NH)
        assert thresholds.min() >= 27000, f"Threshold too low: ${thresholds.min()}"
        assert thresholds.max() <= 38000, f"Threshold too high: ${thresholds.max()}"

    def test_reasonable_risk_distribution(self):
        """Test that risk distribution is reasonable (not all in one category)."""
        base_dir = Path(__file__).parent.parent
        data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        df = pd.read_parquet(data_path)

        risk_counts = df['risk_level'].value_counts()

        # Each risk level should have at least some institutions
        # (except possibly "No Data" which might be small)
        for risk_level in ['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk']:
            count = risk_counts.get(risk_level, 0)
            pct = count / len(df) * 100

            # No single category should dominate (>80%)
            assert pct < 80, f"{risk_level} has {pct:.1f}% of institutions (too concentrated)"


if __name__ == '__main__':
    # Run pytest
    pytest.main([__file__, '-v'])
