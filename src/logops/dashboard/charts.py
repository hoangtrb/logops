"""Plotly figure builders: one visual language for every chart, responsive by default.

Palette: the dataviz reference instance (validated categorical order, single-hue sequential,
blue↔red diverging, reserved status colors). Rules applied: one y-axis per chart (stacked
small multiples instead of dual axes), ≤ 3 hues on bubble/map forms, thin marks, legends on top,
hover tooltips everywhere. Values are pre-formatted in the viewer's language for tooltips.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from logops.data_platform.dq_report import NumberFormatter

# categorical slots in fixed order (never cycled)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
BLUE, ORANGE, AQUA, YELLOW = SERIES[:4]
RED = "#e34948"
TIER = {1: "#86b6ef", 2: "#2a78d6", 3: "#104281"}  # ordinal blue ramp (steps 250/450/650)
SEQUENTIAL = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]
NEUTRAL = "#c3c2b7"
INK, INK2, MUTED, GRID, AXIS, SURFACE = (
    "#0b0b0b",
    "#52514e",
    "#898781",
    "#e1e0d9",
    "#c3c2b7",
    "#ffffff",  # charts sit on white cards
)
STATUS = {"act": "#d03b3b", "watch": "#fab219", "info": BLUE}
FONT = "'Source Sans', 'Source Sans Pro', system-ui, sans-serif"  # the font Streamlit ships
CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
}


def fmt(lang: str) -> NumberFormatter:
    return NumberFormatter(lang)


def money(f: NumberFormatter, lang: str, x: float) -> str:
    """$1.23M / 1,23 tr USD for millions; $1,234 / 1.234 USD below."""
    if x is None:
        return "—"
    if abs(x) >= 1e6:
        return f.value(x, "usd_m")
    return f"${f.int(x)}" if lang == "en" else f"{f.int(x)} USD"


def base(fig: go.Figure, lang: str, height: int = 340, hover: str = "closest") -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=28, b=8),
        font=dict(family=FONT, size=13, color=INK2),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        separators=",." if lang == "vi" else ".,",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title=None, font=dict(size=12)),
        hovermode=hover,
        hoverlabel=dict(font=dict(family=FONT, size=13)),
        bargap=0.25,
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=AXIS,
        tickcolor=AXIS,
        automargin=True,
        title_font=dict(size=12, color=MUTED),
        tickfont=dict(color=MUTED),
    )
    fig.update_yaxes(
        gridcolor=GRID,
        zeroline=False,
        automargin=True,
        title_font=dict(size=12, color=MUTED),
        tickfont=dict(color=MUTED),
    )
    return fig


def date_ticks(fig: go.Figure, lang: str) -> go.Figure:
    """Plotly has no Vietnamese month names, so VI date axes show numeric months."""
    if lang == "vi":
        fig.update_xaxes(tickformat="%m/%Y")
    return fig


def _pad_range(values, share: float = 0.25) -> list[float]:
    """Axis range with room beyond each bar end for an outside value label."""
    lo, hi = min(0, *values), max(0, *values)
    room = share * ((hi - lo) or 1)
    return [lo - room if lo < 0 else 0, hi + room if hi > 0 else 0]


def margin_and_fuel(months, lang, labels) -> go.Figure:
    """Two stacked panels sharing the time axis (never a dual-axis chart)."""
    f = fmt(lang)
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(labels["monthly_margin"], labels["fuel_price"]),
    )
    x = months["period"].to_list()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=months["margin_pct"].to_list(),
            mode="lines",
            line=dict(color=BLUE, width=2),
            name=labels["monthly_margin"],
            customdata=[f.pct(v / 100) for v in months["margin_pct"]],
            hovertemplate="%{x}: %{customdata}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=months["avg_fuel_price"].to_list(),
            mode="lines",
            line=dict(color=ORANGE, width=2),
            name=labels["fuel_price"],
            customdata=[f.value(v, "usd") for v in months["avg_fuel_price"]],
            hovertemplate="%{x}: %{customdata}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    base(fig, lang, height=420, hover="x unified")
    fig.update_layout(showlegend=False, margin=dict(t=36))
    fig.update_annotations(font=dict(size=13, color=INK2), x=0, xanchor="left")
    return date_ticks(fig, lang)


def stacked_revenue(table, lang, labels) -> go.Figure:
    """Revenue split into fuel, maintenance, claims and contribution, per period."""
    f = fmt(lang)
    fig = go.Figure()
    for i, (col, key) in enumerate(
        (
            ("fuel_cost", "fuel"),
            ("maintenance_cost", "maintenance"),
            ("claims", "claims"),
            ("contribution", "contribution"),
        )
    ):
        values = table[col].to_list()
        fig.add_trace(
            go.Bar(
                x=table["period"].to_list(),
                y=[v / 1e6 for v in values],
                name=labels[key],
                marker=dict(color=SERIES[[1, 3, 7, 0][i]], line=dict(color=SURFACE, width=1)),
                customdata=[money(f, lang, v) for v in values],
                hovertemplate=f"{labels[key]}: %{{customdata}}<extra></extra>",
            )
        )
    base(fig, lang, height=360, hover="x unified")
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="tr USD" if lang == "vi" else "USD millions")
    return fig


def waterfall(br, labels, lang, year_a, year_b) -> go.Figure:
    f = fmt(lang)
    parts = ("volume", "rate", "fuel_price", "fuel_consumption", "maintenance", "claims")
    names = (
        [labels["b_start"].format(y=year_a)]
        + [labels[f"b_{p}"] for p in parts]
        + [labels["b_end"].format(y=year_b)]
    )
    values = [br["start"]] + [br["parts"][p] for p in parts] + [br["end"]]
    fig = go.Figure(
        go.Waterfall(
            x=names,
            y=[v / 1e6 for v in values],
            measure=["absolute"] + ["relative"] * len(parts) + ["total"],
            text=[money(f, lang, v) for v in values],
            textposition="outside",
            increasing=dict(marker=dict(color=BLUE)),
            decreasing=dict(marker=dict(color=RED)),
            totals=dict(marker=dict(color=NEUTRAL)),
            connector=dict(line=dict(color=AXIS, width=1)),
            hovertemplate="%{x}: %{text}<extra></extra>",
        )
    )
    base(fig, lang, height=380)
    low = min(br["start"], br["end"]) / 1e6
    fig.update_yaxes(
        range=[low * 0.9, max(br["start"], br["end"]) / 1e6 * 1.05],
        title_text="tr USD" if lang == "vi" else "USD millions",
    )
    fig.update_layout(showlegend=False)
    return fig


def ytd_lines(months, lang, labels) -> go.Figure:
    f = fmt(lang)
    fig = go.Figure()
    rows = months.with_columns()
    years = sorted({p[:4] for p in rows["period"].to_list()})
    for i, year in enumerate(years[-3:]):
        sub = rows.filter(rows["period"].str.starts_with(year))
        fig.add_trace(
            go.Scatter(
                x=[int(p[5:7]) for p in sub["period"]],
                y=[v / 1e6 for v in sub["contribution_ytd"]],
                mode="lines+markers",
                name=year,
                line=dict(color=SERIES[i], width=2),
                marker=dict(size=8, line=dict(color=SURFACE, width=2)),
                customdata=[money(f, lang, v) for v in sub["contribution_ytd"]],
                hovertemplate=f"{year} · %{{x}}: %{{customdata}}<extra></extra>",
            )
        )
    base(fig, lang, height=320, hover="x unified")
    fig.update_xaxes(title_text=labels["month"], dtick=1)
    fig.update_yaxes(title_text="tr USD" if lang == "vi" else "USD millions")
    return fig


def hbar(names, values, lang, value_fmt, color=BLUE, height=None) -> go.Figure:
    """Horizontal bars, largest on top. Labels sit inside the bar end when they fit, otherwise
    just outside; the axis is padded in proportion to the longest label so none is cut off.

    `color` is one color or one per bar (in the order given)."""
    colors = color if isinstance(color, list) else [color] * len(names)
    triples = sorted(zip(names, values, colors, strict=True), key=lambda p: p[1])
    pairs = [(n, v) for n, v, _ in triples]
    text = [value_fmt(v) for _, v in pairs]
    room = min(0.7, 0.035 * max((len(x) for x in text), default=0))
    fig = go.Figure(
        go.Bar(
            x=[v for _, v in pairs],
            y=[n for n, _ in pairs],
            orientation="h",
            marker=dict(color=[c for *_, c in triples]),
            text=text,
            textposition="auto",
            insidetextanchor="end",
            insidetextfont=dict(color="#ffffff"),
            outsidetextfont=dict(color=INK2),
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    base(fig, lang, height=height or max(260, 26 * len(pairs) + 60))
    fig.update_layout(showlegend=False, uniformtext=dict(minsize=10, mode="show"))
    fig.update_yaxes(ticksuffix="  ")  # keep category names off the bars
    fig.update_xaxes(
        showticklabels=False, showgrid=False, range=_pad_range([v for _, v in pairs], room)
    )
    return fig


def us_map(states, values, lang, value_fmt, names=None, unit="") -> go.Figure:
    """Choropleth of US states; `values` in USD, shaded in millions."""
    fig = go.Figure(
        go.Choropleth(
            locations=states,
            z=[v / 1e6 for v in values],
            locationmode="USA-states",
            colorscale=[[i / (len(SEQUENTIAL) - 1), c] for i, c in enumerate(SEQUENTIAL)],
            marker_line_color=SURFACE,
            marker_line_width=1,
            text=[value_fmt(v) for v in values],
            customdata=names or states,
            hovertemplate="%{customdata}: %{text}<extra></extra>",
            colorbar=dict(
                thickness=10,
                len=0.7,
                tickfont=dict(color=MUTED),
                title=dict(text=unit, font=dict(size=11, color=MUTED)),
            ),
        )
    )
    base(fig, lang, height=380)
    fig.update_layout(
        geo=dict(scope="usa", bgcolor=SURFACE, lakecolor=SURFACE, showlakes=False),
        margin=dict(l=0, r=0, t=8, b=0),
    )
    return fig


def grouped_bars(
    categories,
    series: dict,
    lang,
    value_fmt,
    height=320,
    horizontal=False,
    value_title="",
    category_title="",
) -> go.Figure:
    """Side-by-side bars. Horizontal keeps every category label readable on a phone."""
    fig = go.Figure()
    cats = list(reversed(categories)) if horizontal else categories
    # horizontal bars stack traces bottom-up, so add them reversed to read top-down
    items = list(enumerate(series.items()))
    for i, (name, values) in reversed(items) if horizontal else items:
        vals = list(reversed(values)) if horizontal else values
        fig.add_trace(
            go.Bar(
                x=vals if horizontal else cats,
                y=cats if horizontal else vals,
                orientation="h" if horizontal else "v",
                name=name,
                marker=dict(color=SERIES[i]),
                customdata=[value_fmt(v) for v in vals],
                hovertemplate=f"{name}: %{{customdata}}<extra></extra>",
            )
        )
    base(fig, lang, height=height, hover="y unified" if horizontal else "x unified")
    fig.update_layout(barmode="group", bargroupgap=0.08)
    if horizontal:
        fig.update_layout(legend_traceorder="reversed")
        fig.update_xaxes(showgrid=True, gridcolor=GRID, title_text=value_title)
        fig.update_yaxes(showgrid=False, title_text=category_title)
    else:
        fig.update_yaxes(title_text=value_title)
        fig.update_xaxes(title_text=category_title)
    return fig


def pareto(cumulative, lang, labels) -> go.Figure:
    f = fmt(lang)
    n = len(cumulative)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(1, n + 1)),
            y=cumulative,
            mode="lines",
            line=dict(color=BLUE, width=2),
            name=labels["pareto_y"],
            customdata=[f.pct(v / 100) for v in cumulative],
            hovertemplate="%{x}: %{customdata}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[1, n],
            y=[100 / n, 100],
            mode="lines",
            line=dict(color=NEUTRAL, width=1, dash="dot"),
            name="=" if lang == "en" else "=",
            hoverinfo="skip",
            showlegend=False,
        )
    )
    base(fig, lang, height=320)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text=labels["pareto_x"])
    fig.update_yaxes(title_text=labels["pareto_y"], range=[0, 101])
    return fig


def lane_bubbles(matrix, lang, labels) -> go.Figure:
    """Volume × margin bubbles colored by margin tier (3 ordinal blues), 3×3 grid lines."""
    f = fmt(lang)
    fig = go.Figure()
    for tier in (1, 2, 3):
        sub = matrix.filter(matrix["margin_tier"] == tier)
        fig.add_trace(
            go.Scatter(
                x=sub["trips"].to_list(),
                y=sub["margin_pct"].to_list(),
                mode="markers",
                name=f"{labels['margin_tier']}: {labels['tier'][tier]}",
                marker=dict(
                    size=sub["revenue"].to_list(),
                    sizemode="area",
                    sizeref=2.0 * matrix["revenue"].max() / (46**2),
                    sizemin=6,
                    color=TIER[tier],
                    line=dict(color=SURFACE, width=2),
                    opacity=0.9,
                ),
                customdata=[
                    [lane, money(f, lang, rev), f.pct(m / 100), labels["actions"][a]]
                    for lane, rev, m, a in zip(
                        sub["lane"], sub["revenue"], sub["margin_pct"], sub["action"], strict=True
                    )
                ],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>%{x} "
                    + labels["trips"].lower()
                    + " · %{customdata[2]}<br>%{customdata[1]} · %{customdata[3]}"
                    "<extra></extra>"
                ),
            )
        )
    for col, axis in (("trips", "x"), ("margin_pct", "y")):
        tier_col = "volume_tier" if col == "trips" else "margin_tier"
        for t in (1, 2):
            cut = (
                matrix.filter(matrix[tier_col] == t)[col].max()
                + matrix.filter(matrix[tier_col] == t + 1)[col].min()
            ) / 2
            line = dict(color=NEUTRAL, width=1, dash="dot")
            if axis == "x":
                fig.add_vline(x=cut, line=line)
            else:
                fig.add_hline(y=cut, line=line)
    base(fig, lang, height=460)
    fig.update_xaxes(title_text=labels["matrix_x"], showgrid=False)
    fig.update_yaxes(title_text=labels["matrix_y"])
    return fig


def diverging_bars(names, values, lang, value_fmt, labels) -> go.Figure:
    pairs = sorted(zip(names, values, strict=True), key=lambda p: p[1])
    fig = go.Figure(
        go.Bar(
            x=[v for _, v in pairs],
            y=[n for n, _ in pairs],
            orientation="h",
            marker=dict(color=[BLUE if v >= 0 else RED for _, v in pairs]),
            text=[value_fmt(v) for _, v in pairs],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    base(fig, lang, height=max(300, 24 * len(pairs) + 60))
    fig.add_vline(x=0, line=dict(color=AXIS, width=1))
    fig.update_xaxes(
        title_text=labels["net_loads"], zeroline=False, range=_pad_range([v for _, v in pairs])
    )
    fig.update_layout(showlegend=False)
    return fig


def line_with_refs(
    x,
    y,
    lang,
    value_fmt,
    refs: list[tuple[float, str, str]],
    height=360,
    y_title="",
    x_title="",
    markers=False,
    dates=False,
) -> go.Figure:
    """A single line plus horizontal reference lines (value, label, color).

    References are named in the legend, highest first, so close values never print on top of
    each other or under the data line.
    """
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers" if markers else "lines",
            line=dict(color=BLUE, width=2),
            marker=dict(size=8, line=dict(color=SURFACE, width=2)),
            customdata=[value_fmt(v) for v in y],
            hovertemplate="%{x}: %{customdata}<extra></extra>",
            showlegend=False,
        )
    )
    for value, label, color in sorted(refs, reverse=True):
        fig.add_trace(
            go.Scatter(
                x=[x[0], x[-1]],
                y=[value, value],
                mode="lines",
                line=dict(color=color, width=1.5, dash="dash"),
                name=label,
                hoverinfo="skip",
            )
        )
    base(fig, lang, height=height)
    fig.update_layout(showlegend=bool(refs))
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    return date_ticks(fig, lang) if dates else fig


def deviation_bars(hours, counts, lang, value_fmt, x_title, window_label) -> go.Figure:
    """Deliveries per hour of deviation from the appointment, on a real hour axis.

    Each bar spans its hour (e.g. -3 to -2); the ±2 h window is shaded and labelled, bars inside
    it are blue, late beyond it red, early beyond it grey.
    """
    fig = go.Figure(
        go.Bar(
            x=[h + 0.5 for h in hours],
            y=counts,
            width=0.92,
            marker=dict(
                color=[RED if h >= 2 else BLUE if h >= -2 else NEUTRAL for h in hours],
            ),
            text=[value_fmt(c) for c in counts],
            textposition="outside",
            cliponaxis=False,
            customdata=[f"{h:+d} … {h + 1:+d}" for h in hours],
            hovertemplate="%{customdata} h: %{text}<extra></extra>",
        )
    )
    fig.add_vrect(
        x0=-2,
        x1=2,
        fillcolor="#e6effb",
        opacity=0.6,
        layer="below",
        line_width=0,
        annotation_text=window_label,
        annotation_position="top left",
        annotation_font=dict(size=11, color=INK2),
    )
    base(fig, lang, height=320)
    fig.update_layout(showlegend=False, bargap=0)
    lo, hi = min(hours), max(hours) + 1
    fig.update_xaxes(
        title_text=x_title, tickmode="array", tickvals=list(range(lo, hi + 1)), zeroline=False
    )
    fig.update_yaxes(showticklabels=False, showgrid=False, range=[0, max(counts) * 1.25])
    fig.add_vline(x=0, line=dict(color=INK2, width=1, dash="dot"))
    return fig


def histogram(values, lang, x_title, y_title, color=BLUE) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=values,
            marker=dict(color=color, line=dict(color=SURFACE, width=1)),
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    )
    base(fig, lang, height=300)
    fig.update_layout(showlegend=False, bargap=0.05)
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    return fig


def vbars(
    categories, values, lang, value_fmt, color=BLUE, height=300, category_title=""
) -> go.Figure:
    """Vertical bars with their value on top; `color` is one color or one per bar."""
    fig = go.Figure(
        go.Bar(
            x=categories,
            y=values,
            marker=dict(color=color),
            text=[value_fmt(v) for v in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}: %{text}<extra></extra>",
        )
    )
    base(fig, lang, height=height)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(showticklabels=False, showgrid=False)
    fig.update_xaxes(title_text=category_title, type="category")  # years are labels, not numbers
    return fig
