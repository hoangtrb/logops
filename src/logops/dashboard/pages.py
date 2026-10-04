"""The 8 dashboard pages. Each page only lays out what data.py returns and charts.py draws.

Every chart sits in a card with its title, its unit and a reading note; every table is numbered
and can be filtered by its category columns; findings always come as tabs by level. Layout is
responsive: KPI cards sit in a CSS grid (4 → 2 → 1 columns) and chart pairs in Streamlit columns
that stack on phones.
"""

import datetime as dt
import re

import polars as pl

from logops.analysis import insights
from logops.analysis.operations import ACTION_PRIORITY
from logops.dashboard import charts as ch
from logops.dashboard import data, ui
from logops.dashboard.i18n import DQ_COLUMNS, DQ_RULES, DQ_TABLES, STATES
from logops.dashboard.output import st  # Streamlit, or HTML while a report is built
from logops.dashboard.ui import Kpi
from logops.metrics.kpis import AREAS, TITLES, UNITS
from logops.optimize import report as optimize_report

# ------------------------------------------------------------------ shared pieces


def card(title: str):
    """A white bordered container; the key gives it the `st-key-card-…` class styled in ui.CSS."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "x"
    return st.container(border=True, key=f"card-{slug}")


def show(ctx, fig, title: str, unit: str | None = None, note: str | None = None) -> None:
    """A chart in a card: title and unit on top, the reading note underneath."""
    t = ctx["t"]
    with card(title):
        st.html(ui.chart_header(title, t["unit"].format(u=unit) if unit else None))
        st.plotly_chart(fig, width="stretch", theme=None, config=ch.CONFIG)
        if note:
            st.html(ui.callout(t["explain"], note))


def on_paper() -> bool:
    """True while a report for print is drawn: findings and KPIs then come as text and tables."""
    return bool(getattr(st, "paper", False))


def cards(items: list[Kpi], cols: int = 4) -> None:
    st.html(ui.kpi_text(items) if on_paper() else ui.kpi_grid(items, cols))


def findings(ctx, topics: tuple[str, ...] | None = None, levels=None, note=None) -> None:
    """The page's findings in one card, one tab per level present (priority, watch, reference)."""
    t, lang = ctx["t"], ctx["lang"]
    items = [
        i
        for i in ctx["bundle"]["insights"][lang]
        if (not topics or i["topic"] in topics) and (not levels or i["level"] in levels)
    ]
    if not items:
        return
    by_level = {
        lvl: [i for i in items if i["level"] == lvl]
        for lvl in ui.LEVEL_ORDER
        if any(i["level"] == lvl for i in items)
    }
    counts = " · ".join(
        f"{len(g)} {insights.LEVELS[lang][lvl].lower()}" for lvl, g in by_level.items()
    )
    if on_paper():
        groups = [(lvl, insights.LEVELS[lang][lvl], g) for lvl, g in by_level.items()]
        st.html(ui.findings_text(t["key_points"], groups, insights.PARTS[lang]))
        return
    page = "-".join(topics or ("all",)) + "-" + "-".join(levels or ("all",))
    with st.expander(f"**{t['key_points']}** · {counts}", expanded=True, key=f"card-kp-{page}"):
        if note:
            st.caption(note)
        st.html(ui.tone_legend(insights.TONES[lang], t["tone_legend"]))
        tabs = st.tabs(
            [f"{insights.LEVELS[lang][lvl]} ({len(g)})" for lvl, g in by_level.items()],
            key=f"tabs-{page}",
        )
        for tab, group in zip(tabs, by_level.values(), strict=True):
            with tab:
                st.html(ui.findings_html(group, insights.PARTS[lang]))


def table(
    ctx,
    df: pl.DataFrame,
    key: str,
    filters: tuple[str, ...] = (),
    height: int | str = "auto",
    wide_text: tuple[str, ...] = (),
) -> None:
    """A numbered table with one multi-choice filter per category column (like Excel's filter).

    Numbers stay numeric so columns sort correctly, and are shown in the viewer's number format.
    """
    t = ctx["t"]
    shown = df
    if filters and not ctx.get("static"):
        for col, name in zip(st.columns(len(filters)), filters, strict=True):
            options = sorted(df[name].drop_nulls().unique().to_list())
            chosen = col.multiselect(
                name, options, key=f"{key}-{ctx['lang']}-{name}", placeholder=t["filter_all"]
            )
            if chosen:
                shown = shown.filter(pl.col(name).is_in(chosen))
        st.caption(t["rows_shown"].format(n=shown.height, total=df.height))
    shown = shown.with_row_index(t["row_no"], offset=1)
    numeric = {
        c: st.column_config.NumberColumn(format="localized")
        for c, dtype in shown.schema.items()
        if dtype.is_numeric() and c != t["row_no"]
    }
    wide = {c: st.column_config.TextColumn(width="large") for c in wide_text if c in shown.columns}
    st.dataframe(
        shown, width="stretch", hide_index=True, height=height, column_config=numeric | wide
    )


def change(
    ctx,
    now: float | None,
    before: float | None,
    kind: str = "pct",
    vs: str | None = None,
    higher_is_better: bool = True,
) -> tuple[str | None, str]:
    """(delta text, tone) vs an earlier value: % change, or points for rates."""
    if now is None or before is None or before == 0:
        return None, "flat"
    f, t = ctx["f"], ctx["t"]
    vs = vs or t["vs_last_year"]
    if kind == "points":
        diff = now - before
        text = f"{f.num(abs(diff), 1)} {t['points']}"
    else:
        diff = 100 * (now / before - 1)
        text = f.pct(abs(diff) / 100)
    if round(diff, 1) == 0:
        return f"= {text} {vs}", "flat"
    good = (diff > 0) == higher_is_better
    return f"{'▲' if diff > 0 else '▼'} {text} {vs}", "good" if good else "bad"


def money(ctx, x):
    return ch.money(ctx["f"], ctx["lang"], x)


def pct(ctx, x):
    return "—" if x is None else ctx["f"].pct(x / 100)


def label(ctx, value: str) -> str:
    return ctx["t"]["seg"].get(value, value)


def day(ctx, d: dt.date) -> str:
    return d.strftime("%d/%m/%Y" if ctx["lang"] == "vi" else "%Y-%m-%d")


def state(code: str) -> str:
    return f"{STATES[code]} ({code})" if code in STATES else code


def millions(col: str) -> pl.Expr:
    return (pl.col(col) / 1e6).round(2)


# ------------------------------------------------------------------ 1. overview


def _year_span(ctx, year: int) -> tuple[dt.date, dt.date, bool]:
    """The part of `year` inside the chosen range, and whether that is the whole year."""
    a, z = dt.date(year, 1, 1), dt.date(year, 12, 31)
    lo, hi = max(a, ctx["start"]), min(z, ctx["end"])
    return lo, hi, (lo, hi) == (a, z)


def project_rows(ctx) -> list[tuple[str, str, str | None]]:
    """What the project is about and where its data comes from, for the overview and the report."""
    t, f = ctx["t"], ctx["f"]
    p = data.dataset_profile()
    names = t["proj"]
    return [
        (names["title"], t["proj_title"], None),
        (names["goal"], t["proj_goal"], None),
        (
            names["data"],
            t["proj_data"].format(
                tables=p["tables"],
                rows=f.int(p["rows"]),
                a=day(ctx, p["first"]),
                b=day(ctx, p["last"]),
            ),
            None,
        ),
        (
            names["company"],
            t["proj_company"].format(
                **{k: f.int(p[k]) for k in ("trucks", "drivers", "customers", "routes", "trips")}
            ),
            None,
        ),
        (names["source"], t["proj_source"], optimize_report.DATASET_URL),
    ]


def overview(ctx) -> None:
    t, b, f = ctx["t"], ctx["bundle"], ctx["f"]
    if not ctx.get("static"):  # the report shows it on its cover
        st.html(ui.project_card(project_rows(ctx)))
    years = list(range(ctx["start"].year, ctx["end"].year + 1))
    choice = st.segmented_control(
        t["view_period"],
        ["all", *years],
        default=years[-1] if len(years) == 1 else "all",
        format_func=lambda y: t["all_period"] if y == "all" else str(y),
        key="overview_period",
    )
    choice = choice or "all"
    before, vs = None, None
    if choice == "all":
        a, z = ctx["start"], ctx["end"]
        caption = t["period_only"].format(a=day(ctx, a), b=day(ctx, z))
    else:
        a, z, full = _year_span(ctx, choice)
        pa, pz, prev_full = _year_span(ctx, choice - 1)
        if full and prev_full:  # compare whole years only
            before, vs = data.scorecard(pa, pz), t["vs_year"].format(y=choice - 1)
            caption = t["period_vs"].format(a=day(ctx, a), b=day(ctx, z), y=choice - 1)
        else:
            caption = t["period_only"].format(a=day(ctx, a), b=day(ctx, z))
    st.caption(caption)
    now = data.scorecard(a, z)

    def kpi(key, value, field, kind="pct", higher=True, note=None):
        delta, tone = change(
            ctx, now[field], before and before[field], kind, vs=vs, higher_is_better=higher
        )
        return Kpi(t[f"k_{key}"], value, delta, tone, note or t[f"n_{key}"])

    st.html(ui.group_label(t["g_finance"]))
    cards(
        [
            kpi("revenue", money(ctx, now["revenue"]), "revenue"),
            kpi("op_cost", money(ctx, now["op_cost"]), "op_cost", higher=False),
            kpi("contribution", money(ctx, now["contribution"]), "contribution"),
            kpi("margin", pct(ctx, now["margin_pct"]), "margin_pct", "points"),
            kpi("cost_mile", f.value(now["cost_per_mile"], "usd"), "cost_per_mile", higher=False),
        ],
        cols=5,
    )
    st.html(ui.group_label(t["g_operations"]))
    cards(
        [
            kpi(
                "otd",
                pct(ctx, now["otd_pct"]),
                "otd_pct",
                "points",
                note=t["n_otd"].format(day=pct(ctx, now["otd_by_day_pct"])),
            ),
            kpi(
                "detention",
                f"{f.num(now['avg_detention_min'], 1)} {t['minutes']}",
                "avg_detention_min",
                higher=False,
            ),
            kpi("trips", f.int(now["trips"]), "trips"),
            kpi(
                "fleet_use",
                pct(ctx, now["fleet_use_pct"]),
                "fleet_use_pct",
                "points",
                note=t["n_fleet_use"].format(
                    busy=f.int(now["avg_trucks_busy"]), owned=now["trucks_owned"]
                ),
            ),
        ]
    )
    findings(ctx, note=t["findings_scope"])
    show(
        ctx,
        ch.margin_and_fuel(b["margin_vs_fuel"], ctx["lang"], t),
        t["margin_vs_fuel"],
        t["u_margin_fuel"],
        t["margin_vs_fuel_note"].format(corr=f.num(b["facts"]["margin_fuel_corr"], 2)),
    )


# ------------------------------------------------------------------ 2. financial performance


def profit(ctx) -> None:
    t, b, f, lang = ctx["t"], ctx["bundle"], ctx["f"], ctx["lang"]
    findings(ctx, topics=("profit",), levels=("act", "watch"))
    period = (
        st.segmented_control(
            t["choose_period"],
            ["month", "quarter", "year"],
            default="quarter",
            format_func=lambda x: t[x],
        )
        or "quarter"
    )
    pnl = b["pnl"][period]
    show(
        ctx,
        ch.stacked_revenue(pnl, lang, t),
        t["where_revenue_goes"],
        t["u_musd"],
        t["where_revenue_goes_note"],
    )

    years = [int(y) for y in b["pnl"]["year"]["period"]]
    with card(t["bridge"]):
        st.html(ui.chart_header(t["bridge"], t["unit"].format(u=t["u_musd"])))
        c1, c2 = st.columns(2)
        year_a = c1.selectbox(t["bridge_from"], years, index=0)
        year_b = c2.selectbox(t["bridge_to"], years, index=len(years) - 1)
        st.plotly_chart(
            ch.waterfall(data.profit_bridge(year_a, year_b), t, lang, year_a, year_b),
            width="stretch",
            theme=None,
            config=ch.CONFIG,
        )
        st.html(ui.callout(t["explain"], t["bridge_note"]))

    c1, c2 = st.columns(2)
    with c1:
        show(ctx, ch.ytd_lines(b["pnl"]["month"], lang, t), t["ytd"], t["u_musd"], t["ytd_note"])
    with c2:
        units = b["unit_economics"]
        first, last = units.row(0, named=True), units.row(-1, named=True)
        vs = t["vs_year"].format(y=first["period"])

        def unit(key, col, fmt):
            delta, tone = change(ctx, last[col], first[col], vs=vs)
            return Kpi(t[key], fmt(last[col]), delta, tone)

        st.html(ui.group_label(f"{t['units']} · {last['period']}"))
        cards(
            [
                unit("u_rev_mile", "revenue_per_mile", lambda v: f.value(v, "usd")),
                unit("u_contrib_mile", "contribution_per_mile", lambda v: f.value(v, "usd")),
                unit("u_rev_trip", "revenue_per_trip", lambda v: money(ctx, v)),
                unit(
                    "u_contrib_truck_week",
                    "contribution_per_truck_week",
                    lambda v: money(ctx, v),
                ),
            ],
            cols=2,
        )

    cols = t["pnl_cols"]
    view = pnl.select(
        pl.col("period").alias(cols["period"]),
        pl.col("period").str.slice(0, 4).alias(cols["year"]),
        *[
            millions(c).alias(cols[c])
            for c in ("revenue", "fuel_cost", "maintenance_cost", "claims", "contribution")
        ],
        *[
            pl.col(c).round(1).alias(cols[c])
            for c in ("margin_pct", "contribution_vs_prev_pct", "contribution_yoy_pct")
        ],
    )
    with card(t["pnl_table"]):
        st.html(ui.chart_header(t["pnl_table"]))
        if period == "year":
            table(ctx, view.drop(cols["year"]), "pnl")
        else:
            table(ctx, view, f"pnl-{period}", filters=(cols["year"],))


# ------------------------------------------------------------------ 3. customers & markets


def regions(ctx) -> None:
    t, b, f, lang = ctx["t"], ctx["bundle"], ctx["f"], ctx["lang"]
    findings(ctx, topics=("profit",), levels=("info",))
    side = (
        st.segmented_control(
            t["state_side"],
            ["origin_state", "destination_state"],
            default="origin_state",
            format_func=lambda x: t["origin" if x == "origin_state" else "destination"],
        )
        or "origin_state"
    )
    states = b["dimensions"][side].filter(~pl.col("is_total"))
    side_name = t["origin" if side == "origin_state" else "destination"]
    # a report has no map: its outline would be fetched from the internet
    if ctx.get("static"):
        (c2,) = st.columns(1)
    else:
        c1, c2 = st.columns([3, 2])
        with c1:
            show(
                ctx,
                ch.us_map(
                    states["group"].to_list(),
                    states["contribution"].to_list(),
                    lang,
                    lambda v: money(ctx, v),
                    names=[state(s) for s in states["group"]],
                    unit=t["u_musd"],
                ),
                f"{t['state_map']} · {side_name}",
                t["u_musd"],
                t["state_map_note"],
            )
    with c2:
        ranked = states.sort("contribution_margin_pct")
        lo, hi = ranked.row(0, named=True), ranked.row(-1, named=True)
        show(
            ctx,
            ch.hbar(
                [state(s) for s in states["group"]],
                states["contribution_margin_pct"].to_list(),
                lang,
                lambda v: pct(ctx, v),
            ),
            f"{t['margin_by_state']} · {side_name}",
            t["u_pct"],
            t["state_margin_note"].format(
                hi_state=state(hi["group"]),
                hi=pct(ctx, hi["contribution_margin_pct"]),
                lo_state=state(lo["group"]),
                lo=pct(ctx, lo["contribution_margin_pct"]),
            ),
        )

    c1, c2 = st.columns(2)
    for col, dim, title in ((c1, "customer_type", "segments"), (c2, "load_type", "load_types")):
        with col:
            groups = b["dimensions"][dim].filter(~pl.col("is_total"))
            show(
                ctx,
                ch.hbar(
                    [label(ctx, g) for g in groups["group"]],
                    groups["revenue"].to_list(),
                    lang,
                    lambda v: f.num(v / 1e6, 2),
                    height=220,
                ),
                t[title],
                t["u_musd"],
                (t["segments_def"] + " " if dim == "customer_type" else "")
                + " · ".join(
                    f"{label(ctx, g)}: {t['margin'].lower()} {pct(ctx, m)}"
                    for g, m in zip(groups["group"], groups["contribution_margin_pct"], strict=True)
                ),
            )

    conc = b["concentration"]
    st.html(ui.group_label(t["pareto"]))
    cards(
        [
            Kpi(t["c_largest"], pct(ctx, conc["largest_pct"]), note=t["n_share"]),
            Kpi(t["c_top10"], pct(ctx, conc["top10_pct"]), note=t["n_share"]),
            Kpi(t["c_top20"], pct(ctx, conc["top20_pct"]), note=t["n_share"]),
            Kpi(t["c_n80"], f"{conc['customers_for_80pct']} / {conc['customers']}"),
            Kpi(t["c_hhi"], f.int(conc["hhi"]), note=t["n_hhi"]),
        ],
        cols=5,
    )
    c1, c2 = st.columns(2)
    with c1:
        show(ctx, ch.pareto(conc["pareto"], lang, t), t["pareto_chart"], "%", t["pareto_note"])
    with c2:
        names = data.customer_names()
        top = (
            b["dimensions"]["customer"]
            .filter(~pl.col("is_total"))
            .sort("contribution", descending=True)
            .head(15)
        )
        show(
            ctx,
            ch.hbar(
                [names.get(c, c) for c in top["group"]],
                top["contribution"].to_list(),
                lang,
                lambda v: f.num(v / 1e6, 2),
            ),
            t["top_customers"],
            t["u_musd"],
        )


# ------------------------------------------------------------------ 4. lane performance


def network(ctx) -> None:
    t, b, f, lang = ctx["t"], ctx["bundle"], ctx["f"], ctx["lang"]
    findings(ctx, topics=("network",))
    matrix = b["lane_matrix"]
    show(ctx, ch.lane_bubbles(matrix, lang, t), t["matrix"], t["u_matrix"], t["matrix_note"])

    cols = t["lane_cols"]
    order = {a: i for i, a in enumerate(ACTION_PRIORITY)}
    view = (
        matrix.with_columns(
            rank=pl.col("action").replace_strict(order, return_dtype=pl.Int64),
            ends=pl.col("lane").str.split(" → "),
        )
        .sort(["rank", "margin_gap_pts"])
        .select(
            pl.col("lane").alias(cols["lane"]),
            pl.col("ends").list.first().alias(cols["origin"]),
            pl.col("ends").list.last().alias(cols["destination"]),
            pl.col("trips").alias(cols["trips"]),
            millions("revenue").alias(cols["revenue"]),
            millions("contribution").alias(cols["contribution"]),
            pl.col("margin_pct").round(1).alias(cols["margin_pct"]),
            pl.col("margin_gap_pts").round(1).alias(cols["margin_gap_pts"]),
            pl.col("volume_tier").replace_strict(t["tier"]).alias(cols["volume"]),
            pl.col("margin_tier").replace_strict(t["tier"]).alias(cols["margin_level"]),
            pl.col("action").replace_strict(t["assessments"]).alias(cols["assessment"]),
            pl.col("action").replace_strict(t["actions"]).alias(cols["action"]),
        )
    )
    with card(t["lane_eval"]):
        st.html(ui.chart_header(t["lane_eval"]))
        st.html(ui.callout(t["explain"], t["lane_eval_note"]))
        table(
            ctx,
            view,
            "lanes",
            filters=(cols["action"], cols["origin"], cols["destination"]),
            height=420,
            wide_text=(cols["assessment"], cols["action"]),
        )

    cities = b["balance"]["cities"]
    c1, c2 = st.columns(2)
    with c1:
        show(
            ctx,
            ch.diverging_bars(
                cities["city"].to_list(),
                cities["net"].to_list(),
                lang,
                lambda v: f"{'+' if v > 0 else ''}{f.int(v)}",
                t,
            ),
            t["balance"],
            t["u_loads"],
            t["balance_note"],
        )
    with c2:
        ordered = cities.sort("loads_out", descending=True)
        show(
            ctx,
            ch.grouped_bars(
                ordered["city"].to_list(),
                {
                    t["loads_out"]: ordered["loads_out"].to_list(),
                    t["loads_in"]: ordered["loads_in"].to_list(),
                },
                lang,
                f.int,
                height=max(300, 32 * ordered.height + 60),
                horizontal=True,
                value_title=t["u_loads"],
            ),
            t["out_in"],
            t["u_loads"],
        )

    moves = b["repositioning"]["by_year"]
    show(
        ctx,
        ch.vbars(
            [str(y) for y in moves["yr"]],
            moves["moved_pct"].to_list(),
            lang,
            lambda v: pct(ctx, v),
            height=260,
            category_title=t["year"],
        ),
        t["moves"],
        t["u_pct"],
        t["moves_note"].format(
            moved=pct(ctx, b["repositioning"]["moved_pct"]),
            random=pct(ctx, b["repositioning"]["random_pct"]),
        ),
    )


# ------------------------------------------------------------------ 5. delivery performance


def service(ctx) -> None:
    t, f, lang = ctx["t"], ctx["f"], ctx["lang"]
    timing = data.delivery_timing(ctx["start"], ctx["end"])
    rates = [timing[k] for k in ("window", "not_late", "late_le_2h", "by_day")]
    st.html(ui.group_label(t["standards"]))
    cards(
        [
            Kpi(t["s_window"], pct(ctx, timing["window"]), note=t["n_window"]),
            Kpi(t["s_not_late"], pct(ctx, timing["not_late"]), note=t["n_not_late"]),
            Kpi(t["s_late_2h"], pct(ctx, timing["late_le_2h"]), note=t["n_late_2h"]),
            Kpi(t["s_by_day"], pct(ctx, timing["by_day"]), note=t["n_by_day"]),
        ]
    )
    st.html(
        ui.callout(
            t["explain"],
            t["standards_note"].format(lo=pct(ctx, min(rates)), hi=pct(ctx, max(rates))),
        )
    )

    c1, c2 = st.columns(2)
    with c1:
        spread = timing["spread"]
        hours = spread["hour"].to_list()
        show(
            ctx,
            ch.deviation_bars(
                hours,
                spread["deliveries"].to_list(),
                lang,
                f.int,
                t["spread_x"],
                t["window_band"],
            ),
            t["spread"],
            t["u_deliveries"],
            t["spread_note"].format(
                early=f"{f.num(-timing['min_dev_h'], 0)} {t['hours']}",
                late=f"{f.num(timing['max_dev_h'], 0)} {t['hours']}",
            ),
        )
    with c2:
        by_len = timing["by_length"]
        show(
            ctx,
            ch.grouped_bars(
                [t["bands"][band] for band in by_len["band"]],
                {
                    t["s_window"]: by_len["window_pct"].to_list(),
                    t["s_late_2h"]: by_len["late_le_2h_pct"].to_list(),
                    t["s_by_day"]: by_len["by_day_pct"].to_list(),
                },
                lang,
                lambda v: pct(ctx, v),
                value_title="%",
            ),
            t["by_length"],
            t["u_pct"],
            t["by_length_note"].format(
                **{k: pct(ctx, v) for k, v in zip("abc", by_len["window_pct"], strict=False)}
            ),
        )

    s = data.service_summary(ctx["start"], ctx["end"], 120)
    st.html(ui.group_label(t["detention_title"]))
    cards(
        [
            Kpi(
                t["s_detention"],
                f"{f.num(s['avg_detention_min'], 1)} {t['minutes']}",
                note=t["s_detention_note"],
            ),
            Kpi(
                t["s_detention_hours"],
                f"{f.int(s['detention_hours'])} {t['hours']}",
                note=t["s_detention_hours_note"],
            ),
        ],
        cols=2,
    )
    c1, c2 = st.columns(2)
    with c1:
        det = data.detention(ctx["start"], ctx["end"])
        years = sorted({str(y) for y in det["year"]})
        series = {}
        for event, key in (("Pickup", "pickup"), ("Delivery", "delivery")):
            sub = det.filter(pl.col("event_type") == event).sort("year")
            series[t[key]] = sub["avg_minutes"].to_list()
        show(
            ctx,
            ch.grouped_bars(
                years,
                series,
                lang,
                lambda v: f"{f.num(v, 1)} {t['minutes']}",
                value_title=t["u_minutes"],
                category_title=t["year"],
            ),
            t["detention_type"],
            t["u_minutes"],
            t["detention_note"],
        )
    with c2:
        cities = data.service_by(ctx["start"], ctx["end"], "location_city", 120)
        show(
            ctx,
            ch.hbar(
                cities["group"].to_list(),
                cities["on_time_pct"].to_list(),
                lang,
                lambda v: pct(ctx, v),
            ),
            t["on_time_city"],
            t["u_pct"],
        )

    st.html(ui.group_label(t["sensitivity_title"]))
    window = st.slider(t["window"], 0, 240, 120, 15, help=t["window_help"])
    c1, c2 = st.columns(2)
    with c1:
        sens = data.sensitivity(ctx["start"], ctx["end"])
        fig = ch.line_with_refs(
            sens["window_min"].to_list(),
            sens["on_time_pct"].to_list(),
            lang,
            lambda v: pct(ctx, v),
            [],
            height=320,
            x_title=t["sensitivity_x"],
            y_title=t["sensitivity_y"],
            markers=True,
        )
        fig.add_vline(
            x=120,
            line=dict(color=ch.MUTED, width=1, dash="dash"),
            annotation_text=t["data_window"],
            annotation_position="top left",
        )
        if window != 120:
            fig.add_vline(
                x=window,
                line=dict(color=ch.ORANGE, width=2),
                annotation_text=t["selected_window"],
                annotation_position="bottom right",
            )
        show(ctx, fig, t["sensitivity"], t["u_pct"], t["sensitivity_note"])
    with c2:
        months = data.service_by(ctx["start"], ctx["end"], "month", window)
        show(
            ctx,
            ch.line_with_refs(
                months["group"].to_list(),
                months["on_time_pct"].to_list(),
                lang,
                lambda v: pct(ctx, v),
                [],
                height=320,
                y_title=t["sensitivity_y"],
                dates=True,
            ),
            t["on_time_month"],
            t["u_pct"],
        )


# ------------------------------------------------------------------ 6. fleet capacity


def fleet(ctx) -> None:
    t, b, f, lang = ctx["t"], ctx["bundle"], ctx["f"], ctx["lang"]
    cap = b["capacity"]
    findings(ctx, topics=("fleet",))

    daily = cap["daily"]
    refs = [
        (cap["p95"], f"{t['p95']}: {f.int(cap['p95'])}", ch.AQUA),
        (cap["p99"], f"{t['p99']}: {f.int(cap['p99'])}", ch.ORANGE),
        (cap["trucks_in_use"], f"{t['in_use']}: {cap['trucks_in_use']}", ch.INK2),
        (cap["trucks_owned"], f"{t['owned']}: {cap['trucks_owned']}", ch.RED),
    ]
    show(
        ctx,
        ch.line_with_refs(
            daily["day"].to_list(),
            daily["trucks_busy"].to_list(),
            lang,
            str,
            refs,
            height=380,
            y_title=t["u_trucks"],
            dates=True,
        ),
        t["daily_trucks"],
        t["u_trucks"],
        t["daily_trucks_note"].format(
            avg=f.int(cap["mean"]),
            p95=f.int(cap["p95"]),
            p99=f.int(cap["p99"]),
            max=cap["max"],
            owned=cap["trucks_owned"],
            in_use=cap["trucks_in_use"],
            spare=cap["trucks_owned"] - cap["max"],
        ),
    )

    tables = data.fleet_tables()
    prod = data.fleet_productivity(ctx["start"], ctx["end"])
    score = data.scorecard(ctx["start"], ctx["end"])
    st.html(ui.group_label(t["productivity"]))
    cards(
        [
            Kpi(
                t["f_miles_month"],
                f"{f.int(prod['miles_per_truck_month'])} {t['u_miles']}",
                note=t["n_miles_month"],
            ),
            Kpi(
                t["f_rev_truck_week"],
                money(ctx, score["revenue_per_truck_week"]),
                note=t["n_rev_truck_week"],
            ),
            Kpi(
                t["f_util"],
                pct(ctx, score["fleet_use_pct"]),
                note=t["n_fleet_use"].format(
                    busy=f.int(score["avg_trucks_busy"]), owned=score["trucks_owned"]
                ),
            ),
            Kpi(
                t["f_downtime"],
                f"{f.int(prod['downtime_hours'])} {t['hours']}",
                note=t["n_downtime"],
            ),
        ]
    )

    c1, c2 = st.columns(2)
    with c1:
        show(
            ctx,
            ch.histogram(daily["trucks_busy"].to_list(), lang, t["busy_x"], t["days_y"]),
            t["busy_dist"],
            t["u_days"],
            t["busy_dist_note"].format(avg=f.int(cap["mean"]), p95=f.int(cap["p95"])),
        )
    with c2:
        util = [100 * u for u in tables["trucks"]["avg_utilization"].drop_nulls()]
        show(
            ctx,
            ch.histogram(util, lang, t["util_x"], t["trucks_y"], color=ch.AQUA),
            t["util_dist"],
            t["u_trucks"],
            t["util_note"],
        )

    idle = tables["idle"]
    status = tables["status"]
    names = [
        f"{label(ctx, s)}<br>{t['ran_trips'] if u else t['never_ran']}"
        for s, u in zip(status["status"], status["used"], strict=True)
    ]
    show(
        ctx,
        ch.hbar(names, status["trucks"].to_list(), lang, str, height=260),
        t["status"],
        t["u_trucks"],
    )
    title = t["idle_trucks"].format(n=idle.height)
    cols = t["idle_cols"]
    view = idle.select(
        pl.col("truck_id").alias(cols["truck_id"]),
        pl.col("make").alias(cols["make"]),
        pl.col("model_year").cast(pl.Utf8).alias(cols["model_year"]),
        pl.col("status").replace(t["seg"]).alias(cols["status"]),
        pl.col("maintenance_events").alias(cols["maintenance_events"]),
        pl.col("maintenance_cost").round(0).alias(cols["maintenance_cost"]),
    )
    with card(title):
        st.html(ui.chart_header(title))
        st.html(
            ui.callout(
                t["explain"],
                t["idle_note"].format(cost=money(ctx, idle["maintenance_cost"].sum())),
            )
        )
        table(ctx, view, "idle", filters=(cols["make"], cols["status"]), height=320)


# ------------------------------------------------------------------ 7. fuel management


def fuel(ctx) -> None:
    t, b, f, lang = ctx["t"], ctx["bundle"], ctx["f"], ctx["lang"]
    findings(ctx, topics=("fuel",))
    period = (
        st.segmented_control(
            t["choose_period"],
            ["month", "quarter", "year"],
            default="quarter",
            format_func=lambda x: t[x],
            key="fuel_period",
        )
        or "quarter"
    )
    rows = b["fuel"][period].drop_nulls("gallons_burned")
    periods = rows["period"].to_list()
    show(
        ctx,
        ch.grouped_bars(
            periods,
            {
                t["bought"]: rows["gallons_bought"].to_list(),
                t["burned"]: rows["gallons_burned"].to_list(),
            },
            lang,
            f.int,
            height=340,
            value_title=t["u_gallons"],
        ),
        t["bought_vs_burned"],
        t["u_gallons"],
        t["bought_note"],
    )
    c1, c2 = st.columns(2)
    with c1:
        show(
            ctx,
            ch.line_with_refs(
                periods,
                rows["bought_to_burned"].to_list(),
                lang,
                lambda v: f.num(v, 2),
                [],
                height=300,
                y_title=t["u_times"],
                markers=True,
            ),
            t["ratio"],
            t["u_times"],
            t["ratio_note"],
        )
    with c2:
        show(
            ctx,
            ch.line_with_refs(
                periods,
                rows["avg_price"].to_list(),
                lang,
                lambda v: f.value(v, "usd"),
                [],
                height=300,
                y_title=t["u_usd_gallon"],
                markers=True,
            ),
            t["price_trend"],
            t["u_usd_gallon"],
        )
    show(
        ctx,
        ch.vbars(periods, rows["spend"].to_list(), lang, lambda v: f.num(v / 1e6, 2)),
        t["spend"],
        t["u_musd"],
        t["spend_note"],
    )


# ------------------------------------------------------------------ 8. data quality & KPIs


def _rule_label(lang: str, tbl: str, rule: str, col: str | None) -> str:
    column = DQ_COLUMNS[lang].get(col, col) if col else ""
    issue = DQ_RULES[lang].get(rule, rule).format(col=column).strip()
    return f"{DQ_TABLES[lang].get(tbl, tbl)}: {issue[:1].upper()}{issue[1:]}"


def _kpi_value(ctx, unit: str, value: float | None) -> str:
    f = ctx["f"]
    if value is None:
        return "—"
    if unit == "USD":
        return money(ctx, value)
    if unit == "%":
        return pct(ctx, value)
    if unit == "USD/mile":
        return f.value(value, "usd")
    digits = 2 if abs(value) < 10 else 1 if abs(value) < 1000 else 0
    return f"{f.num(value, digits)} {UNITS[unit][ctx['lang']]}"


def data_page(ctx) -> None:
    t, f, lang = ctx["t"], ctx["f"], ctx["lang"]
    dq = data.data_quality()
    total_rows = sum(dq["rows"].values())
    errors = sum(dq["flagged_error"].values())
    cards(
        [
            Kpi(t["d_tables"], str(len(dq["rows"]))),
            Kpi(t["d_rows"], f.int(total_rows)),
            Kpi(t["d_rules"], str(len(dq["findings"]))),
            Kpi(t["d_errors"], f"{f.int(errors)} ({f.pct(errors / total_rows)})"),
        ]
    )
    hits = [(tbl, rule, col, sev, n) for tbl, rule, col, sev, n, _s in dq["findings"] if n > 0]
    show(
        ctx,
        ch.hbar(
            [_rule_label(lang, tbl, rule, col) for tbl, rule, col, *_ in hits],
            [n for *_, n in hits],
            lang,
            f.int,
            color=[ch.RED if sev == "error" else ch.YELLOW for *_, sev, _n in hits],
        ),
        t["findings"],
        t["u_rows"],
        t["findings_note"],
    )

    with card(t["trust"]):
        st.html(ui.chart_header(t["trust"]))
        st.html(
            ui.html_table(
                t["trust_cols"],
                [[what, ui.level_text(level, cls)] for what, level, cls in t["trust_rows"]],
                nowrap={1},
            )
        )

    cols = t["g_cols"]
    rows = [
        {
            cols["area"]: AREAS[k["area"]][lang],
            cols["kpi"]: TITLES[k["name"]][lang],
            cols["value"]: _kpi_value(ctx, k["unit"], k["value"]),
            cols["unit"]: UNITS[k["unit"]][lang],
            cols["formula"]: k["formula"][lang],
        }
        for k in data.kpi_glossary(ctx["start"], ctx["end"])
    ]
    with card(t["glossary"]):
        st.html(ui.chart_header(t["glossary"]))
        st.html(ui.callout(t["explain"], t["glossary_note"]))
        shown = rows
        if not ctx.get("static"):  # a report has no filter
            areas = sorted({r[cols["area"]] for r in rows})
            chosen = st.multiselect(
                cols["area"], areas, key=f"glossary-{lang}", placeholder=t["filter_all"]
            )
            shown = [r for r in rows if not chosen or r[cols["area"]] in chosen]
            st.caption(t["rows_shown"].format(n=len(shown), total=len(rows)))
        header = list(rows[0])  # same order as the row values
        st.html(
            ui.html_table(
                header,
                [list(r.values()) for r in shown],
                numeric={header.index(cols["value"])},
                nowrap={header.index(cols["unit"])},
            )
        )


# ------------------------------------------------------------------ 9. optimization
# One page: the savings summary first, then each lever in its own group (fleet, lane pricing,
# fuel surcharge, late deliveries, data process) and the levers checked and not recommended.


def growth_label(t: dict, g: float) -> str:
    return t["o_growth_now"] if g == 0 else t["o_growth_up"].format(g=f"{g:g}")


def opt_group(ctx, title: str) -> None:
    st.html(ui.group_label(title))


def scope_note(ctx) -> str | None:
    """The recommendations cover all the data: say so on the dashboard (the sidebar range doesn't
    apply) and in a report only when its period is shorter than the data."""
    t = ctx["t"]
    first, last = data.bounds()
    span = {"a": day(ctx, first), "b": day(ctx, last)}
    if not ctx.get("static"):
        return t["o_scope"].format(**span)
    if (ctx["start"], ctx["end"]) != (first, last):
        return t["o_scope_report"].format(**span)
    return None


def _musd(ctx):
    return lambda x: ctx["f"].value(x, "usd_m")


def savings_tips(ctx, d: dict, rec: pl.DataFrame, tot: dict) -> dict[str, list[str]]:
    """For each savings card, the figures it is made of and what it takes to reach the target."""
    t, f = ctx["t"], ctx["f"]
    musd = _musd(ctx)
    target, m, u = tot["target"], tot["measured"], tot["upper"]

    def items(kind: str) -> list[str]:
        rows = rec.filter(pl.col("impact_type") == kind).iter_rows(named=True)
        return [f"• {r['action']}: {musd(r['annual_impact_usd'])}" for r in rows]

    measured_trucks = int(d["tiers"].filter(pl.col("saving_type") == "measured")["trucks"].sum())
    gap = target - m
    fsc = d["by_cap"][optimize_report.DEFAULT_CAP_PCT][0]
    if gap > 0:
        reach = [
            t["o_tip_gap"].format(
                target=musd(target), m=musd(m), gap=musd(gap), share=f.pct(gap / u)
            ),
            t["o_tip_example"].format(fsc=musd(fsc), fsc_share=f.pct(gap / fsc)),
        ]
    else:
        reach = [t["o_tip_done"].format(target=musd(target))]
    base = target / optimize_report.TARGET_SHARE
    return {
        "target": [line.format(base=musd(base), target=musd(target)) for line in t["o_tip_target"]],
        "measured": [
            t["o_tip_measured"],
            *items("measured"),
            t["o_tip_sum"].format(total=musd(m), pct=f.pct(m / target)),
            t["o_tip_measured_end"].format(n=measured_trucks),
        ],
        "upper": [
            t["o_tip_upper"],
            *items("upper bound"),
            t["o_tip_sum"].format(total=musd(u), pct=f.pct(u / target)),
            t["o_tip_upper_end"],
        ],
        "total": [
            t["o_tip_total"].format(
                m=musd(m), u=musd(u), total=musd(m + u), pct=f.pct((m + u) / target)
            ),
            *reach,
        ],
    }


def optimize(ctx) -> None:
    t, f, lang = ctx["t"], ctx["f"], ctx["lang"]
    musd = _musd(ctx)
    d = data.optimization(0.0)
    if note := scope_note(ctx):
        st.caption(note)
    rec = optimize_report.recommendations(d, lang)
    tot = optimize_report.totals(d)
    target = tot["target"]
    total = tot["measured"] + tot["upper"]
    tips = savings_tips(ctx, d, rec, tot)
    if not on_paper():  # printed, the computation sits under each figure
        st.caption(t["o_tip_hint"])
    cards(
        [
            Kpi(t["o_target"], musd(target), note=t["n_target"], tip=tips["target"]),
            Kpi(
                t["o_measured"],
                musd(tot["measured"]),
                note=t["n_measured"].format(pct=f.pct(tot["measured"] / target)),
                tip=tips["measured"],
            ),
            Kpi(t["o_upper"], musd(tot["upper"]), note=t["n_upper"], tip=tips["upper"]),
            Kpi(
                t["o_total"],
                musd(total),
                note=t["n_total"].format(pct=f.pct(total / target)),
                tip=tips["total"],
            ),
        ]
    )
    unexplained = rec.filter(pl.col("impact_type") == "unexplained")["annual_impact_usd"].sum()
    st.html(ui.callout(t["explain"], t["o_unexplained"].format(amount=musd(unexplained))))

    valued = rec.filter(pl.col("impact_type").is_in(["measured", "upper bound"]))
    show(
        ctx,
        ch.hbar(
            valued["action"].to_list(),
            valued["annual_impact_usd"].to_list(),
            lang,
            lambda v: f.num(v / 1e6, 2),
            color=[
                ch.AQUA if k == "measured" else ch.BLUE for k in valued["impact_type"].to_list()
            ],
        ),
        t["o_chart"],
        t["u_musd"],
        t["o_chart_note"].format(target=musd(target)),
    )

    acted = rec.filter(pl.col("impact_type") != "no signal")
    with card(t["o_table"]):
        st.html(ui.chart_header(t["o_table"]))
        st.html(
            ui.html_table(
                t["o_cols"],
                [
                    [
                        t["o_areas"][r["area"]],
                        r["action"],
                        r["item"],
                        musd(r["annual_impact_usd"]) if r["annual_impact_usd"] else "—",
                        t["o_types"][r["impact_type"]],
                        r["evidence"],
                    ]
                    for r in acted.iter_rows(named=True)
                ],
                numeric={3},
            )
        )

    fleet_plan(ctx)
    lane_pricing(ctx)
    fuel_surcharge(ctx)
    lateness_check(ctx)
    data_gaps(ctx)

    opt_group(ctx, t["o_checked"])
    checked = rec.filter(pl.col("impact_type") == "no signal")
    with card(t["o_checked"]):
        st.html(ui.chart_header(t["o_checked"]))
        st.html(ui.callout(t["explain"], t["o_checked_note"]))
        st.html(
            ui.html_table(
                t["o_checked_cols"],
                [[r["item"], r["evidence"]] for r in checked.iter_rows(named=True)],
            )
        )


def fleet_plan(ctx) -> None:
    """Fleet page: trucks needed per volume scenario and the disposal tiers."""
    t, lang = ctx["t"], ctx["lang"]
    musd = _musd(ctx)
    opt_group(ctx, t["o_fleet"])
    growth = (
        st.segmented_control(
            t["o_growth"],
            [0, 5, 10, 20],
            default=0,
            format_func=lambda g: growth_label(t, g),
            key="opt_growth",
        )
        or 0
    )
    st.caption(t["o_growth_help"])
    d = data.optimization(growth / 100)
    plan = d["plan"]
    now = plan.filter(pl.col("growth_pct") == float(growth)).row(0, named=True)
    trucks = t["u_trucks"]
    cards(
        [
            Kpi(t["o_needed"], f"{now['trucks_needed']} {trucks}", note=t["n_needed"]),
            Kpi(t["o_owned"], f"{now['fleet_size']} {trucks}"),
            Kpi(t["o_in_use"], f"{now['trucks_in_use']} {trucks}"),
            Kpi(t["o_surplus"], f"{now['surplus']} {trucks}"),
        ]
    )
    cc = d["cross_check"]
    c1, c2 = st.columns([2, 3])
    with c1:
        show(
            ctx,
            ch.vbars(
                [growth_label(t, g) for g in plan["growth_pct"]],
                plan["trucks_needed"].to_list(),
                lang,
                str,
                color=[ch.BLUE if g == growth else ch.NEUTRAL for g in plan["growth_pct"]],
                height=300,
                category_title=t["o_growth"],
            ),
            t["o_needed_chart"],
            trucks,
            t["o_needed_note"].format(
                owned=now["fleet_size"],
                in_use=now["trucks_in_use"],
                busiest=cc["busiest_day_trucks"],
                above=cc["days_above_need"],
                days=cc["days"],
            ),
        )
    with c2, card(t["o_tiers"]):
        st.html(ui.chart_header(t["o_tiers"]))
        st.html(
            ui.html_table(
                t["o_tier_cols"],
                [
                    [
                        r["tier"],
                        t["o_tier_status"][r["status"]],
                        r["trucks"],
                        r["return_to_service"],
                        musd(r["maintenance_per_year"]),
                        t["o_types"][r["saving_type"]],
                    ]
                    for r in d["tiers"].iter_rows(named=True)
                ],
                numeric={2, 3, 4},
                numbered=False,
            )
        )
        st.html(ui.callout(t["explain"], t["o_tiers_note"]))


def lane_pricing(ctx) -> None:
    """Lanes page: fuel-surcharge (S1) and rate (S2) scenarios, per lane."""
    t, f = ctx["t"], ctx["f"]
    musd = _musd(ctx)
    opt_group(ctx, t["o_lanes"])
    d = data.optimization(0.0)
    target = optimize_report.totals(d)["target"]
    cap = st.segmented_control(
        t["o_cap"],
        ["5", "10", "none"],
        default="5",
        format_func=lambda c: t["o_cap_none"] if c == "none" else f"+{c}%",
        key="opt_cap",
    )
    cap_value = None if cap == "none" else float(cap or 5)
    s1, s2, loss = d["by_cap"][cap_value]
    cards(
        [
            Kpi(t["o_s1"], musd(s1), note=t["n_s1"]),
            Kpi(t["o_s2"], musd(s2), note=t["n_s2"]),
            Kpi(
                t["o_s12"],
                musd(s1 + s2),
                note=t["n_s12"].format(pct=f.pct((s1 + s2) / target)),
            ),
            Kpi(t["o_loss"], pct(ctx, loss), note=t["n_loss"]),
        ]
    )
    cols = t["o_lane_cols"]
    lanes = d["lane_scenarios"][cap_value]
    view = lanes.sort(["s2_uplift", "s1_uplift"], descending=True).select(
        pl.col("lane").alias(cols["lane"]),
        pl.col("group").replace_strict(t["actions"]).alias(cols["group"]),
        (100 * pl.col("margin")).round(1).alias(cols["margin"]),
        pl.col("fsc_rate").round(3).alias(cols["fsc_rate"]),
        pl.col("s1_uplift").round(0).alias(cols["s1"]),
        pl.col("s2_uplift").round(0).alias(cols["s2"]),
        pl.col("s2_linehaul_increase_pct").round(1).alias(cols["increase"]),
        pl.col("max_volume_loss_pct").round(1).alias(cols["loss"]),
        pl.col("break_even_driver_cost_per_mile").round(3).alias(cols["break_even"]),
    )
    with card(t["o_lane_table"]):
        st.html(ui.chart_header(t["o_lane_table"]))
        st.html(ui.callout(t["explain"], t["o_lane_note"]))
        table(ctx, view, "opt-lanes", filters=(cols["group"],), height=380)


def fuel_surcharge(ctx) -> None:
    """Fuel page: a surcharge that follows the fuel price (S3), simulated."""
    t, f, lang = ctx["t"], ctx["f"], ctx["lang"]
    opt_group(ctx, t["o_s3_group"])
    d = data.optimization(0.0)
    ix = d["indexed_by_year"]
    show(
        ctx,
        ch.grouped_bars(
            [str(y) for y in ix["year"]],
            {
                t["o_s3_actual"]: [v / 1e6 for v in ix["actual"]],
                t["o_s3_indexed"]: [v / 1e6 for v in ix["indexed"]],
            },
            lang,
            lambda v: f.num(v, 2),
            value_title=t["u_musd"],
            category_title=t["year"],
        ),
        t["o_s3"],
        t["u_musd"],
        t["o_s3_note"].format(base=f.value(d["indexed_base"], "usd")),
    )


def lateness_check(ctx) -> None:
    """Delivery page: does lateness repeat by city, customer, hour, lane or driver?"""
    t, f = ctx["t"], ctx["f"]
    opt_group(ctx, t["r_late"])
    d = data.optimization(0.0)
    with card(t["r_late"]):
        st.html(ui.chart_header(t["r_late"]))
        st.html(ui.callout(t["explain"], t["r_late_note"].format(share=pct(ctx, d["late_share"]))))
        st.html(
            ui.html_table(
                t["r_late_cols"],
                [
                    [
                        t["r_dims"][r["dimension"]],
                        r["groups"],
                        "—" if r["spread_pts"] is None else f.num(r["spread_pts"], 1),
                        "—" if r["persistence"] is None else f.num(r["persistence"], 2),
                        t["r_yes"] if r["signal"] else t["r_no"],
                    ]
                    for r in d["lateness"].iter_rows(named=True)
                ],
                numeric={1, 2, 3},
            )
        )


def data_gaps(ctx) -> None:
    """Data page: process and equipment changes that would close the data gaps."""
    t, f, lang = ctx["t"], ctx["f"], ctx["lang"]
    opt_group(ctx, t["o_gaps"])
    d = data.optimization(0.0)
    g = d["gaps"]
    low, high = g.telematics_cost_per_year
    cards(
        [
            Kpi(
                t["o_tele_cost"],
                f"{money(ctx, low)} – {money(ctx, high)}",
                note=t["n_tele_cost"].format(trucks=g.trucks_in_use),
            ),
            Kpi(t["o_tele_break"], f.pct(g.telematics_break_even_share), note=t["n_tele_break"]),
        ],
        cols=2,
    )
    with card(t["o_gaps"]):
        st.html(ui.chart_header(t["o_gaps"]))
        st.html(ui.callout(t["explain"], t["o_gaps_note"]))
        st.html(
            ui.html_table(
                t["o_gap_cols"],
                [
                    [r["gap"], r["evidence"], r["not_doing"], r["tier1"], r["tier2"]]
                    for r in optimize_report.gap_rows(d, lang)
                ],
            )
        )
        sources = " · ".join(text for text, _url in optimize_report.SOURCES.values())
        st.caption(f"{t['o_sources']}: {sources}")


# page key and render function: the dashboard's navigation and the report's tabs, in order
ORDER = [
    ("p_overview", overview),
    ("p_profit", profit),
    ("p_regions", regions),
    ("p_network", network),
    ("p_service", service),
    ("p_fleet", fleet),
    ("p_fuel", fuel),
    ("p_optimize", optimize),
    ("p_data", data_page),
]
