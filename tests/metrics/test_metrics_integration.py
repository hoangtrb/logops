"""KPIs on the real data reconcile with the raw tables (and so with the DQ report)."""

import datetime as dt

import duckdb
import pytest

from logops import config
from logops.metrics.kpis import FLEET, kpi
from logops.metrics.views import create_views

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first"),
]
# Through 2025: $93,269 of fuel was bought in Jan 2025, a month with no trips (Unattributed).
ALL = (dt.date(2022, 1, 1), dt.date(2025, 12, 31))


@pytest.fixture(scope="module")
def con():
    con = duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True)
    yield con
    con.close()


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def fleet(con, start, end, **kw):
    (row,) = [r for r in kpi(con, start, end, **kw).iter_rows(named=True) if r["group"] == FLEET]
    return row


def test_fleet_totals_match_raw_tables(con):
    f = fleet(con, *ALL)
    raw = scalar(con, "SELECT sum(revenue + fuel_surcharge + accessorial_charges) FROM loads")
    cost = scalar(
        con,
        "SELECT (SELECT sum(total_cost) FROM fuel_purchases)"
        " + (SELECT sum(total_cost) FROM maintenance_records)"
        " + (SELECT sum(claim_amount) FROM safety_incidents)",
    )
    assert f["revenue"] == pytest.approx(raw)
    assert f["measured_cost"] == pytest.approx(cost)
    assert f["mpg"] == pytest.approx(
        scalar(con, "SELECT sum(actual_distance_miles) / sum(fuel_gallons_used) FROM trips")
    )
    flag = scalar(
        con,
        "SELECT 100 * avg(on_time_flag::INT) FROM delivery_events WHERE event_type = 'Delivery'",
    )
    assert f["on_time_pct"] == pytest.approx(flag)  # window 120 = on_time_flag


@pytest.mark.parametrize(
    "by", ["month", "route", "customer", "truck", "driver", "load_type", "origin_state"]
)
def test_groups_reconcile_with_fleet(con, by):
    rows = list(kpi(con, *ALL, by=by).iter_rows(named=True))
    total = [r for r in rows if r["group"] == FLEET][0]
    parts = [r for r in rows if r["group"] != FLEET]
    for column in ("revenue", "measured_cost"):
        assert sum(r[column] or 0 for r in parts) == pytest.approx(total[column]), column


def test_year_filter_matches_raw_2024_totals(con):
    f = fleet(con, dt.date(2024, 1, 1), dt.date(2024, 12, 31))
    raw = scalar(
        con,
        "SELECT sum(l.revenue + l.fuel_surcharge + l.accessorial_charges) FROM loads l "
        "JOIN trips t USING (load_id) WHERE year(t.dispatch_date) = 2024",
    )
    assert f["revenue"] == pytest.approx(raw)
    maintenance = scalar(
        con, "SELECT sum(total_cost) FROM maintenance_records WHERE year(maintenance_date) = 2024"
    )
    assert f["maintenance_cost_per_mile"] * scalar(
        con, "SELECT sum(actual_distance_miles) FROM trips WHERE year(dispatch_date) = 2024"
    ) == pytest.approx(maintenance)


def test_views_exist_after_build(con):
    names = {n for (n,) in con.execute("SELECT view_name FROM duckdb_views()").fetchall()}
    assert {"trip_economics", "delivery_performance", "truck_economics"} <= names
    assert scalar(con, "SELECT count(*) FROM trip_economics") == scalar(
        con, "SELECT count(*) FROM trips"
    )
    _ = create_views  # imported for the build path; views are created by `logops build`
