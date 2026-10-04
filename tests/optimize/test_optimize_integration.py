"""Fleet and lane results on the real data reconcile with the KPI layer."""

import datetime as dt

import duckdb
import pytest

from logops import config
from logops.analysis.operations import capacity_plan, lane_matrix
from logops.metrics.kpis import FLEET, UNATTRIBUTED, kpi
from logops.optimize.fleet import disposal_tiers, fleet_plan
from logops.optimize.lanes import indexed_surcharge, lane_table, scenarios

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first"),
]
PERIOD = (dt.date(2022, 1, 1), dt.date(2024, 12, 31))


@pytest.fixture(scope="module")
def con():
    con = duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True)
    yield con
    con.close()


def test_lanes_reconcile_with_fleet_kpis(con):
    tiers = lane_matrix(con, *PERIOD).select("lane", "action", "volume_tier", "margin_tier")
    lanes = scenarios(lane_table(con, *PERIOD).join(tiers.drop("action"), on="lane"), years=3.0)
    rows = {r["group"]: r for r in kpi(con, *PERIOD, by="route").iter_rows(named=True)}
    assert lanes["revenue"].sum() == pytest.approx(rows[FLEET]["revenue"])
    # lanes + costs that belong to no trip (unused trucks' maintenance) = fleet contribution
    assert lanes["contribution"].sum() + rows[UNATTRIBUTED]["contribution"] == pytest.approx(
        rows[FLEET]["contribution"]
    )
    assert lanes.height == 58
    # same groups as the dashboard's lane matrix
    joined = lanes.join(tiers, on="lane")
    assert (joined["group"] == joined["action"]).all()


def test_trucks_needed_grow_with_volume_and_stay_below_fleet(con):
    needed = fleet_plan(con)["trucks_needed"].to_list()
    assert needed == sorted(needed)
    assert needed[-1] <= 120


def test_disposal_never_leaves_the_fleet_short(con):
    for growth in (0.0, 0.1, 0.2):
        plan = fleet_plan(con, growths=(growth,))
        tiers = disposal_tiers(con, growth)
        disposed = tiers["trucks"].sum()
        assert 120 - disposed >= plan["trucks_needed"][0], growth


def test_daily_demand_matches_the_dashboard(con):
    from logops.optimize.fleet import daily_demand

    cap = capacity_plan(con, *PERIOD)
    assert daily_demand(con) == cap["daily"]["trucks_busy"].to_list()


def test_late_deliveries_have_no_persistent_cause(con):
    from logops.optimize.lateness import persistence

    result = persistence(con, *PERIOD)
    assert result.height == 5
    assert not result["signal"].any()


def test_indexed_surcharge_is_revenue_neutral(con):
    ix = indexed_surcharge(con)
    assert ix["indexed"].sum() == pytest.approx(ix["actual"].sum(), rel=1e-6)


def test_report_totals_and_docs(con, tmp_path):
    from logops.optimize.report import (
        collect,
        recommendations,
        render_evaluation,
        render_gaps,
        totals,
    )

    data = collect(con)
    rec = recommendations(data)
    t = totals(data)
    measured = data["tiers"].filter(data["tiers"]["saving_type"] == "measured")
    assert t["measured"] == pytest.approx(measured["maintenance_per_year"].sum())
    assert set(rec["impact_type"]) <= {
        "measured",
        "upper bound",
        "risk sharing",
        "unexplained",
        "no signal",
    }
    for lang in ("en", "vi"):
        assert render_evaluation(data, lang) == render_evaluation(data, lang)
        assert "http" in render_gaps(data, lang)  # every device cost cites its source
