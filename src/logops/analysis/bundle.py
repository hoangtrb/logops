"""analysis_bundle(): every table and comment the dashboard and the doc need, computed once."""

import datetime as dt

import duckdb
import polars as pl

from logops.analysis import insights
from logops.analysis.operations import (
    capacity_plan,
    fuel_by_period,
    lane_matrix,
    network_balance,
    repositioning,
)
from logops.analysis.profit import (
    bridge,
    by_dimension,
    concentration,
    margin_vs_fuel,
    pnl,
    unit_economics,
)
from logops.analysis.service import idle_trucks

DEFAULT_RANGE = (dt.date(2022, 1, 1), dt.date(2024, 12, 31))
DIMENSIONS = (
    "customer_type",
    "load_type",
    "origin_state",
    "destination_state",
    "route",
    "customer",
    "truck",
    "driver",
)


def analysis_bundle(
    con: duckdb.DuckDBPyConnection,
    start: dt.date = DEFAULT_RANGE[0],
    end: dt.date = DEFAULT_RANGE[1],
) -> dict:
    years = pnl(con, start, end, "year")
    first, last = years.row(0, named=True), years.row(-1, named=True)
    y_a = (dt.date(int(first["period"]), 1, 1), dt.date(int(first["period"]), 12, 31))
    y_b = (dt.date(int(last["period"]), 1, 1), dt.date(int(last["period"]), 12, 31))
    br = bridge(con, y_a, y_b)
    units = unit_economics(years)
    monthly_margin, fuel_corr = margin_vs_fuel(con, start, end)
    dims = {d: by_dimension(con, start, end, d) for d in DIMENSIONS}
    conc = concentration(con, start, end)
    fuel_years = fuel_by_period(con, start, end, "year")
    cap = capacity_plan(con, start, end)
    matrix = lane_matrix(con, start, end)
    balance = network_balance(con, start, end)
    moves = repositioning(con, start, end)
    idle = idle_trucks(con)  # trucks with no trip in the data, with their maintenance cost

    segments = dims["customer_type"].filter(~pl.col("is_total"))
    states = dims["origin_state"].filter(~pl.col("is_total")).sort("contribution", descending=True)
    top_state = states.row(0, named=True)
    actions = matrix.group_by("action").len()
    count = lambda a: int(actions.filter(pl.col("action") == a)["len"].sum())  # noqa: E731
    delta = br["end"] - br["start"]
    facts = {
        "year_first": first["period"],
        "year_last": last["period"],
        "margin_first": first["margin_pct"],
        "margin_last": last["margin_pct"],
        "trips_first": first["trips"],
        "trips_last": last["trips"],
        "trips_change_pct": 100 * (last["trips"] / first["trips"] - 1),
        "rpm_first": units.row(0, named=True)["revenue_per_mile"],
        "rpm_last": units.row(-1, named=True)["revenue_per_mile"],
        "rpm_change_pct": 100
        * (
            units.row(-1, named=True)["revenue_per_mile"]
            / units.row(0, named=True)["revenue_per_mile"]
            - 1
        ),
        "bridge_delta": delta,
        "bridge_fuel": br["parts"]["fuel_price"],
        "bridge_fuel_share": br["parts"]["fuel_price"] / delta if delta else 0.0,
        "margin_fuel_corr": fuel_corr,
        "segment_margin_min": segments["contribution_margin_pct"].min(),
        "segment_margin_max": segments["contribution_margin_pct"].max(),
        "top_state": top_state["group"],
        "top_state_contribution": top_state["contribution"],
        "top_state_share": top_state["contribution_share_pct"],
        "state_margin_min": states["contribution_margin_pct"].min(),
        "state_margin_max": states["contribution_margin_pct"].max(),
        "largest_customer_pct": conc["largest_pct"],
        "top10_pct": conc["top10_pct"],
        "customers_for_80pct": conc["customers_for_80pct"],
        "customers": conc["customers"],
        "hhi": conc["hhi"],
        "fuel_ratio_min": fuel_years["bought_to_burned"].min(),
        "fuel_ratio_max": fuel_years["bought_to_burned"].max(),
        "cap_p95": cap["p95"],
        "cap_p99": cap["p99"],
        "cap_max": cap["max"],
        "trucks_in_use": cap["trucks_in_use"],
        "trucks_owned": cap["trucks_owned"],
        "lag1": cap["lag1_autocorrelation"],
        "quarter_persistence": cap["quarter_persistence"],
        "yearly_mean_min": cap["yearly_mean_range"][0],
        "yearly_mean_max": cap["yearly_mean_range"][1],
        "lanes_protect": count("protect"),
        "lanes_reprice": count("reprice"),
        "lanes_review_low": count("review_low"),
        "lane_margin_min": matrix["margin_pct"].min(),
        "surplus_pct": balance["inbound_surplus_pct"],
        "surplus": balance["inbound_surplus_loads"],
        "cities_imbalanced": balance["cities_over_20pct"],
        "cities": balance["cities"].height,
        "balance_persistence": balance["persistence"],
        "receive_only_cities": sorted(
            balance["cities"].filter(pl.col("loads_out") == 0)["city"].to_list()
        ),
        "moved_pct": moves["moved_pct"],
        "moved_random_pct": moves["random_pct"],
        "trucks_never_ran": idle.height,
        "never_ran_maintenance": idle["maintenance_cost"].sum(),
    }
    facts["segment_margin_spread"] = facts["segment_margin_max"] - facts["segment_margin_min"]
    rec = lambda lang: insights.generate(facts, lang)  # noqa: E731
    return {
        "range": (start, end),
        "pnl": {p: pnl(con, start, end, p) for p in ("month", "quarter", "year")},
        "bridge": br,
        "unit_economics": units,
        "margin_vs_fuel": monthly_margin,
        "dimensions": dims,
        "concentration": conc,
        "fuel": {p: fuel_by_period(con, start, end, p) for p in ("month", "quarter", "year")},
        "capacity": cap,
        "lane_matrix": matrix,
        "balance": balance,
        "repositioning": moves,
        "facts": facts,
        "insights": {"en": rec("en"), "vi": rec("vi")},
    }
