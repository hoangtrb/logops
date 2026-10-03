import polars as pl
import pytest

from logops.optimize.lanes import CORE, NICHE, REPRICE, REVIEW, classify, scenarios

# Four lanes, one per group. Median margin 0.6 and median trips 100 (by construction).
#   lane  trips  linehaul surcharge  cost   margin
#   A     200    800      200        300    0.70   high margin, high volume  → Core
#   B     200    800      200        500    0.50   low margin,  high volume  → Reprice
#   C      50    800      200        300    0.70   high margin, low volume   → Niche
#   D      50    800      200        500    0.50   low margin,  low volume   → Review
LANES = pl.DataFrame(
    {
        "lane": ["A", "B", "C", "D"],
        "trips": [200, 200, 50, 50],
        "typical_miles": [1000.0, 1000.0, 1000.0, 1000.0],
        "linehaul": [800.0, 800.0, 800.0, 800.0],
        "surcharge": [200.0, 200.0, 200.0, 200.0],
        "fsc_rate": [0.30, 0.10, 0.20, 0.20],  # median 0.20
        "measured_cost": [300.0, 500.0, 300.0, 500.0],
        "miles": [1000.0, 1000.0, 1000.0, 1000.0],
    }
)


def by_lane(df):
    return {r["lane"]: r for r in df.iter_rows(named=True)}


def test_classification_uses_median_margin_and_volume():
    groups = {r["lane"]: r["group"] for r in classify(LANES).iter_rows(named=True)}
    assert groups == {"A": CORE, "B": REPRICE, "C": NICHE, "D": REVIEW}


def test_break_even_driver_cost_per_mile():
    lanes = by_lane(classify(LANES))
    assert lanes["A"]["break_even_driver_cost_per_mile"] == pytest.approx(700 / 1000)
    assert lanes["B"]["break_even_driver_cost_per_mile"] == pytest.approx(500 / 1000)


def test_s1_raises_only_surcharges_below_median():
    result = by_lane(scenarios(LANES, years=1.0))
    # B: (0.20 - 0.10) × 1000 typical miles = +100; A, C, D at or above the median: 0
    assert result["B"]["s1_uplift"] == pytest.approx(100)
    assert [result[x]["s1_uplift"] for x in "ACD"] == [0, 0, 0]


def test_s2_reprices_low_margin_lanes_to_median_margin_after_s1():
    result = by_lane(scenarios(LANES, years=1.0))
    # B after S1: revenue 1100, cost 500 → margin 0.545 < 0.6
    # linehaul increase so (R + x - 500) / (R + x) = 0.6 → R + x = 1250 → x = 150
    assert result["B"]["s2_uplift"] == pytest.approx(150)
    assert result["B"]["s2_linehaul_increase_pct"] == pytest.approx(100 * 150 / 800)
    # D: no S1, revenue 1000 → x = 250
    assert result["D"]["s2_uplift"] == pytest.approx(250)
    assert result["A"]["s2_uplift"] == 0 and result["C"]["s2_uplift"] == 0


def test_break_even_volume_loss():
    b = by_lane(scenarios(LANES, years=1.0))["B"]
    # old contribution 500, new 500 + 100 + 150 = 750 → can lose 1 - 500/750 = 33.3% of volume
    assert b["max_volume_loss_pct"] == pytest.approx(100 * (1 - 500 / 750))


def test_amounts_are_annualized():
    result = by_lane(scenarios(LANES, years=2.0))
    assert result["B"]["s1_uplift"] == pytest.approx(50)


def test_cap_limits_the_linehaul_increase():
    result = by_lane(scenarios(LANES, years=1.0, cap_pct=10))
    assert result["B"]["s2_uplift"] == pytest.approx(80)  # 10% of 800, below the 150 needed
    assert result["D"]["s2_uplift"] == pytest.approx(80)
    assert result["B"]["s2_linehaul_increase_pct"] == pytest.approx(10)
