import datetime as dt

import pytest

from logops.metrics.kpis import CATALOG, FLEET, UNATTRIBUTED, kpi

ALL = (dt.date(2024, 1, 1), dt.date(2024, 12, 31))


def row(table, group):
    (match,) = [r for r in table.iter_rows(named=True) if r["group"] == group]
    return match


def test_fleet_cost_kpis(con):
    fleet = row(kpi(con, *ALL), FLEET)

    assert fleet["revenue"] == pytest.approx(830)
    # fuel 100 + 150 + 100 + $30 March spend with no trips; maintenance 55 + idle T9 40
    assert fleet["measured_cost"] == pytest.approx(380 + 95 + 70)
    assert fleet["cost_per_mile"] == pytest.approx(545 / 310)
    assert fleet["fuel_cost_per_mile"] == pytest.approx(380 / 310)
    assert fleet["contribution"] == pytest.approx(830 - 545)
    assert fleet["out_of_route_pct"] == pytest.approx(100 * 10 / 300)


def test_fleet_fuel_service_asset_safety_kpis(con):
    fleet = row(kpi(con, *ALL), FLEET)

    assert fleet["mpg"] == pytest.approx(310 / 75)
    assert fleet["fuel_purchased_to_burned"] == pytest.approx(91 / 75)
    assert fleet["on_time_pct"] == pytest.approx(100 * 2 / 3)  # +90 and -30 are within ±120
    assert fleet["not_late_pct"] == pytest.approx(100 * 1 / 3)  # only -30
    assert fleet["detention_hours"] == pytest.approx(90 / 60)
    assert fleet["miles_per_truck_month"] == pytest.approx(310 / 3)  # T1-Jan, T2-Jan, T1-Feb
    assert fleet["downtime_hours"] == pytest.approx(13)
    assert fleet["incidents_per_million_miles"] == pytest.approx(1e6 / 310)
    assert fleet["preventable_pct"] == pytest.approx(100)


def test_on_time_window_is_a_parameter(con):
    # |deviation| <= 0 min: +90, +150 and -30 all miss
    assert row(kpi(con, *ALL, on_time_window_min=0), FLEET)["on_time_pct"] == pytest.approx(0)
    assert row(kpi(con, *ALL, on_time_window_min=200), FLEET)["on_time_pct"] == pytest.approx(100)


@pytest.mark.parametrize("by", ["month", "route", "customer", "customer_type", "truck", "driver"])
def test_groups_plus_unattributed_add_up_to_fleet(con, by):
    table = kpi(con, *ALL, by=by)
    groups = [r for r in table.iter_rows(named=True) if r["group"] != FLEET]
    fleet = row(table, FLEET)
    for column in ("revenue", "measured_cost", "contribution"):
        assert sum(r[column] or 0 for r in groups) == pytest.approx(fleet[column]), column


def test_driver_grouping_puts_missing_ids_and_idle_costs_in_unattributed(con):
    table = kpi(con, *ALL, by="driver")
    assert row(table, "D1")["revenue"] == pytest.approx(620)
    unattributed = row(table, UNATTRIBUTED)
    assert unattributed["revenue"] == pytest.approx(210)  # tr2 has no driver
    assert unattributed["measured_cost"] == pytest.approx(150 + 70 + 30 + 40)


def test_date_filter(con):
    january = row(kpi(con, dt.date(2024, 1, 1), dt.date(2024, 1, 31)), FLEET)
    assert january["revenue"] == pytest.approx(530)
    assert january["measured_cost"] == pytest.approx(250 + 95 + 70)  # no March fuel


def test_location_city_only_has_delivery_kpis(con):
    chicago = row(kpi(con, *ALL, by="location_city"), "Chicago")
    assert chicago["on_time_pct"] == pytest.approx(100 * 2 / 3)
    assert chicago["revenue"] is None


def test_catalog_has_21_kpis_with_both_languages():
    assert len(CATALOG) == 21
    for k in CATALOG:
        assert k.formula["en"] and k.formula["vi"], k.name
