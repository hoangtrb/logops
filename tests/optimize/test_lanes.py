import polars as pl
import pytest

from logops.optimize.lanes import classify, scenarios

# Three lanes, one per third. Median margin 0.6, median surcharge rate 0.20.
#   lane  trips  linehaul surcharge  cost   margin   volume third  margin third  action
#   A     200    800      200        300    0.70     3             3             protect
#   B     150    800      200        500    0.50     2             1             review_price
#   C      50    800      200        400    0.60     1             2             monitor
LANES = pl.DataFrame(
    {
        "lane": ["A", "B", "C"],
        "trips": [200, 150, 50],
        "typical_miles": [1000.0, 1000.0, 1000.0],
        "linehaul": [800.0, 800.0, 800.0],
        "surcharge": [200.0, 200.0, 200.0],
        "fsc_rate": [0.30, 0.10, 0.20],
        "measured_cost": [300.0, 500.0, 400.0],
        "miles": [1000.0, 1000.0, 1000.0],
    }
)


def by_lane(df):
    return {r["lane"]: r for r in df.iter_rows(named=True)}


def test_classification_uses_the_dashboard_thirds():
    groups = {r["lane"]: r["group"] for r in classify(LANES).iter_rows(named=True)}
    assert groups == {"A": "protect", "B": "review_price", "C": "monitor"}


def test_tiers_from_the_analysis_layer_are_kept():
    given = LANES.with_columns(volume_tier=pl.lit(1), margin_tier=pl.lit(1))
    assert set(classify(given)["group"]) == {"review_low"}


def test_break_even_driver_cost_per_mile():
    lanes = by_lane(classify(LANES))
    assert lanes["A"]["break_even_driver_cost_per_mile"] == pytest.approx(700 / 1000)
    assert lanes["B"]["break_even_driver_cost_per_mile"] == pytest.approx(500 / 1000)


def test_s1_raises_only_surcharges_below_median():
    result = by_lane(scenarios(LANES, years=1.0))
    # B: (0.20 - 0.10) × 1000 typical miles = +100; A and C at or above the median: 0
    assert result["B"]["s1_uplift"] == pytest.approx(100)
    assert [result[x]["s1_uplift"] for x in "AC"] == [0, 0]


def test_s2_reprices_the_lowest_margin_third_to_median_margin_after_s1():
    result = by_lane(scenarios(LANES, years=1.0))
    # B after S1: revenue 1100, cost 500 → margin 0.545 < 0.6
    # linehaul increase so (R + x - 500) / (R + x) = 0.6 → R + x = 1250 → x = 150
    assert result["B"]["s2_uplift"] == pytest.approx(150)
    assert result["B"]["s2_linehaul_increase_pct"] == pytest.approx(100 * 150 / 800)
    # A and C are not in the lowest margin third (C sits at the median)
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
    assert result["B"]["s2_linehaul_increase_pct"] == pytest.approx(10)
