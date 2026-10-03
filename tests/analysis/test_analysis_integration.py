"""Analyses on the real data reconcile with the KPI layer and with themselves."""

import datetime as dt

import duckdb
import polars as pl
import pytest

from logops import config
from logops.analysis.bundle import analysis_bundle
from logops.analysis.doc import render
from logops.metrics.kpis import FLEET, kpi

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first"),
]
RANGE = (dt.date(2022, 1, 1), dt.date(2024, 12, 31))


@pytest.fixture(scope="module")
def bundle():
    with duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) as con:
        b = analysis_bundle(con, *RANGE)
        fleet = [r for r in kpi(con, *RANGE).iter_rows(named=True) if r["group"] == FLEET][0]
    return b, fleet


def test_pnl_reconciles_with_kpi_fleet_totals(bundle):
    b, fleet = bundle
    for period in ("month", "quarter", "year"):
        table = b["pnl"][period]
        assert table["revenue"].sum() == pytest.approx(fleet["revenue"]), period
        assert table["measured_cost"].sum() == pytest.approx(fleet["measured_cost"]), period


def test_bridge_parts_add_up_to_the_change(bundle):
    br = bundle[0]["bridge"]
    assert sum(br["parts"].values()) == pytest.approx(br["end"] - br["start"])


def test_dimensions_reconcile(bundle):
    b, fleet = bundle
    for dim, table in b["dimensions"].items():
        parts = table.filter(pl.col("group") != FLEET)
        assert parts["contribution"].sum() == pytest.approx(fleet["contribution"]), dim


def test_network_and_capacity_facts(bundle):
    b, _ = bundle
    cities = b["balance"]["cities"]
    assert cities["loads_out"].sum() == cities["loads_in"].sum() == b["balance"]["total_loads"]
    cap = b["capacity"]
    assert cap["p95"] <= cap["p99"] <= cap["max"] <= cap["trucks_in_use"]
    assert b["lane_matrix"].height == 58


def test_docs_are_deterministic(bundle):
    b, _ = bundle
    for lang in ("en", "vi"):
        assert render(b, lang) == render(b, lang)
