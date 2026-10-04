import pytest

from logops.optimize.data_gaps import GAPS, Measures

M = Measures(
    years=2.0,
    trucks_in_use=10,
    fuel_spend_per_year=1_000_000.0,
    gallons_purchased=1300.0,
    gallons_burned=1000.0,
    avg_price=4.0,
    unattributable_fuel_per_year=0.0,
    deliveries_per_year=100.0,
    deliveries_outside_window_per_year=50.0,
    detention_hours_per_year=0.0,
    contribution_margin_pct=60.0,
    weakest_lane_break_even_driver_cost=1.0,
    moved_pct=95.0,
    moved_random_pct=95.0,
    late_share_pct=44.0,
    late_persistence_max=0.1,
)


def test_unreconciled_fuel_value_per_year():
    assert M.unreconciled_gallons == 300
    assert M.unreconciled_value_per_year == pytest.approx(300 * 4 / 2)


def test_misuse_benchmark_is_two_to_five_percent_of_fuel_spend():
    assert M.misuse_benchmark_per_year == pytest.approx((20_000, 50_000))


def test_telematics_cost_and_break_even():
    # 10 trucks × (12 × $20 + $100 / 3 years) and × (12 × $45 + $500 / 3)
    low, high = M.telematics_cost_per_year
    assert low == pytest.approx(10 * (240 + 100 / 3))
    assert high == pytest.approx(10 * (540 + 500 / 3))
    assert M.telematics_break_even_share == pytest.approx(high / 1_000_000)


def test_every_gap_has_both_languages_and_unique_priority():
    assert sorted(g["priority"] for g in GAPS) == list(range(1, len(GAPS) + 1))
    for g in GAPS:
        assert set(g["en"]) == set(g["vi"]), g["id"]
