import pytest

from logops.optimize.fleet import (
    availability,
    daily_demand,
    disposal_tiers,
    fleet_plan,
    trucks_needed,
)


def test_daily_demand_counts_busy_trucks_and_truckless_trips(con):
    demand = daily_demand(con)
    assert len(demand) == 10  # every day of the period, idle days included
    assert sorted(demand, reverse=True)[:4] == [2, 2, 1, 1]
    assert demand.count(0) == 6


def test_availability_uses_downtime_of_trucks_in_use(con):
    # A and B over 10 days = 480 h; A was down 24 h
    assert availability(con) == pytest.approx(1 - 24 / 480)


def test_trucks_needed_rounds_up_after_growth_and_availability():
    assert trucks_needed(design_demand=75, availability=0.977) == 77
    assert trucks_needed(design_demand=75 * 1.2, availability=0.977) == 93


def test_fleet_plan_scenarios(con):
    plan = fleet_plan(con, growths=(0.0, 0.5), percentile=1.0)
    rows = {r["growth_pct"]: r for r in plan.iter_rows(named=True)}
    assert rows[0.0]["design_demand"] == pytest.approx(2)
    assert rows[0.0]["trucks_needed"] == 3  # ceil(2 / 0.95)
    assert rows[50.0]["trucks_needed"] == 4  # ceil(3 / 0.95)
    assert rows[0.0]["fleet_size"] == 4
    assert rows[0.0]["trucks_in_use"] == 2
    assert rows[0.0]["surplus"] == 1


def test_disposal_tiers_measure_maintenance_per_year(con):
    # No growth still needs 3 trucks with 2 in use → Maintenance truck D returns, Inactive C goes
    tiers = {r["tier"]: r for r in disposal_tiers(con).iter_rows(named=True)}
    years = 10 / 365.25
    assert tiers[1]["status"] == "Inactive" and tiers[1]["trucks"] == 1
    assert tiers[1]["maintenance_per_year"] == pytest.approx(300 / years)
    assert tiers[2]["status"] == "Maintenance" and tiers[2]["trucks"] == 0
    assert tiers[2]["return_to_service"] == 1


def test_shortfall_returns_maintenance_trucks_before_inactive(con):
    # +50% growth needs 4 trucks; only 2 are in use → D (Maintenance) and C (Inactive) both return
    tiers = {r["tier"]: r for r in disposal_tiers(con, growth=0.5).iter_rows(named=True)}
    assert tiers[2]["return_to_service"] == 1 and tiers[2]["trucks"] == 0
    assert tiers[1]["return_to_service"] == 1 and tiers[1]["trucks"] == 0
    assert tiers[3]["trucks"] == 0
    assert all(t["maintenance_per_year"] == 0 for t in tiers.values())


def test_cross_check(con):
    from logops.optimize.fleet import cross_check

    # needs 3 trucks at no growth; no day needs more than 2 / 0.95 = 2.1
    assert cross_check(con) == {
        "busiest_day_trucks": 2,
        "max_trucks_active_in_a_month": 2,
        "days": 10,
        "days_above_need": 0,
    }
