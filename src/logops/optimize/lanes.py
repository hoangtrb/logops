"""Lane profitability: classify lanes, then price scenarios with their break-even volume loss.

Revenue = linehaul (incl. accessorials) + fuel surcharge. Margins are contribution margins on
measured cost (fuel, maintenance, incidents). Driver pay
isn't in the data, so instead of guessing it each lane gets a break-even driver cost per mile:
the lane loses money if driver cost per mile exceeds it.

Scenarios (annualized, upper bounds that assume volume is kept):
- S1: lanes whose fuel-surcharge rate is below the median rate are raised to the median.
- S2: after S1, lanes in Reprice/Review still below the median margin get a linehaul increase
  that brings them to the median margin.
Each lane also gets the largest volume loss before the change earns less than today:
1 − old contribution ÷ new contribution.
"""

import datetime as dt

import duckdb
import polars as pl

CORE = "Core"
REPRICE = "Reprice"
NICHE = "Profitable niche"
REVIEW = "Review"

_LANES = """
    SELECT te.lane, any_value(r.fuel_surcharge_rate) AS fsc_rate,
           count(*) AS trips, sum(te.miles) AS miles, sum(te.typical_miles) AS typical_miles,
           sum(l.revenue + l.accessorial_charges) AS linehaul,
           sum(l.fuel_surcharge) AS surcharge,
           sum(te.fuel_cost) AS fuel_cost, sum(te.measured_cost) AS measured_cost
    FROM trip_economics te
    JOIN loads l ON l.load_id = te.load_id
    JOIN routes r ON r.route_id = te.route_id
    WHERE te.dispatch_date BETWEEN $start AND $end
    GROUP BY te.lane ORDER BY te.lane
"""


def lane_table(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> pl.DataFrame:
    """Per-lane sums for the period, ready for classify() and scenarios()."""
    cur = con.execute(_LANES, {"start": start, "end": end})
    columns = [d[0] for d in cur.description]
    return pl.DataFrame(cur.fetchall(), schema=columns, orient="row")


def _with_margin(df: pl.DataFrame) -> pl.DataFrame:
    revenue = pl.col("linehaul") + pl.col("surcharge")
    return df.with_columns(
        revenue=revenue,
        contribution=revenue - pl.col("measured_cost"),
        margin=(revenue - pl.col("measured_cost")) / revenue,
        break_even_driver_cost_per_mile=(revenue - pl.col("measured_cost")) / pl.col("miles"),
    )


def classify(df: pl.DataFrame) -> pl.DataFrame:
    """Add margin, contribution, break-even driver cost and the margin × volume group."""
    df = _with_margin(df)
    median_margin = df["margin"].median()
    median_trips = df["trips"].median()
    high_margin = pl.col("margin") >= median_margin
    high_volume = pl.col("trips") >= median_trips
    return df.with_columns(
        group=pl.when(high_margin & high_volume)
        .then(pl.lit(CORE))
        .when(~high_margin & high_volume)
        .then(pl.lit(REPRICE))
        .when(high_margin & ~high_volume)
        .then(pl.lit(NICHE))
        .otherwise(pl.lit(REVIEW)),
        fsc_recovery=pl.col("surcharge") / pl.col("fuel_cost")
        if "fuel_cost" in df.columns
        else pl.lit(None),
    )


def scenarios(df: pl.DataFrame, years: float, cap_pct: float | None = None) -> pl.DataFrame:
    """S1 and S2 per lane, annualized; plus the break-even volume loss of S1+S2.

    cap_pct limits the S2 linehaul increase per lane (e.g. 5 = at most +5%). None = no cap: a
    theoretical upper bound that can imply increases the market won't accept.
    """
    df = classify(df)
    median_rate = df["fsc_rate"].median()
    median_margin = df["margin"].median()
    s1 = (pl.lit(median_rate) - pl.col("fsc_rate")).clip(lower_bound=0) * pl.col("typical_miles")
    df = df.with_columns(s1_total=s1)
    revenue_after_s1 = pl.col("revenue") + pl.col("s1_total")
    target_revenue = pl.col("measured_cost") / (1 - median_margin)
    needs_s2 = pl.col("group").is_in([REPRICE, REVIEW])
    s2 = (
        pl.when(needs_s2).then((target_revenue - revenue_after_s1).clip(lower_bound=0)).otherwise(0)
    )
    if cap_pct is not None:
        s2 = pl.min_horizontal(s2, pl.col("linehaul") * cap_pct / 100)
    df = df.with_columns(s2_total=s2)
    new_contribution = pl.col("contribution") + pl.col("s1_total") + pl.col("s2_total")
    return df.with_columns(
        s1_uplift=pl.col("s1_total") / years,
        s2_uplift=pl.col("s2_total") / years,
        s2_linehaul_increase_pct=100 * pl.col("s2_total") / pl.col("linehaul"),
        max_volume_loss_pct=100 * (1 - pl.col("contribution") / new_contribution),
    ).drop("s1_total", "s2_total")


def indexed_surcharge(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """S3 simulation: a revenue-neutral, fuel-price-indexed surcharge, month by month.

    Surcharge per mile = (month's price − base) ÷ fleet MPG, with the base chosen so that the
    total over the period equals today's surcharge revenue. Shows how price risk would be shared;
    it is not a saving.
    """
    cur = con.execute(
        """
        WITH price AS (
            SELECT date_trunc('month', purchase_date)::DATE AS mth,
                   sum(total_cost) / sum(gallons) AS price
            FROM fuel_purchases GROUP BY ALL
        ),
        trips_m AS (
            SELECT te.month AS mth, sum(te.miles) AS miles, sum(l.fuel_surcharge) AS actual
            FROM trip_economics te JOIN loads l ON l.load_id = te.load_id GROUP BY ALL
        ),
        fleet AS (
            SELECT sum(miles) / sum(gallons_burned) AS mpg FROM trip_economics
        ),
        joined AS (SELECT * FROM trips_m JOIN price USING (mth)),
        base AS (
            SELECT sum(price * miles) / sum(miles)
                   - sum(actual) / sum(miles) * (SELECT mpg FROM fleet) AS base
            FROM joined
        )
        SELECT mth AS month, price, actual,
               greatest(price - (SELECT base FROM base), 0) / (SELECT mpg FROM fleet) * miles
                   AS indexed,
               (SELECT base FROM base) AS base_price
        FROM joined ORDER BY mth
        """
    )
    columns = [d[0] for d in cur.description]
    return pl.DataFrame(cur.fetchall(), schema=columns, orient="row")
