"""Hand-built HTML pieces where Streamlit's own widgets are too rigid.

- KPI cards in a CSS grid, so every card in a row has the same size and the grid steps down to
  2 columns on tablets and 1 on phones.
- Finding cards: each says whether it is good or bad news, what happened, its impact and
  what to do. Pages group them in tabs by level.

The functions return HTML strings (no Streamlit calls), so they can be tested on their own.
All text is escaped.
"""

from dataclasses import dataclass
from html import escape

LEVEL_ORDER = ("act", "watch", "info")

CSS = """
<style>
.block-container {padding-top: 3.4rem; padding-bottom: 3rem; max-width: 1320px;}
header[data-testid="stHeader"] {background: transparent;}
.lo-sub {font-size: 0.9rem; color: #6b6a65; margin: -0.4rem 0 0.6rem;}
.lo-group {font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
  color: #8a8882; margin: 1.1rem 0 0.5rem;}
.lo-wrap {container-type: inline-size; container-name: lo;}
.lo-grid {display: grid; gap: 12px; margin-bottom: 0.4rem;}
.lo-grid.c2 {grid-template-columns: repeat(2, minmax(0, 1fr));}
.lo-grid.c3 {grid-template-columns: repeat(3, minmax(0, 1fr));}
.lo-grid.c4 {grid-template-columns: repeat(4, minmax(0, 1fr));}
.lo-grid.c5 {grid-template-columns: repeat(5, minmax(0, 1fr));}
/* columns follow the width of the content area (the sidebar may be open), not the screen */
@container lo (max-width: 900px) {.lo-grid.c5 {grid-template-columns: repeat(3, minmax(0, 1fr));}}
@container lo (max-width: 760px) {
  .lo-grid.c4, .lo-grid.c5 {grid-template-columns: repeat(2, minmax(0, 1fr));}
}
@container lo (max-width: 600px) {.lo-grid.c3 {grid-template-columns: repeat(2, minmax(0, 1fr));}}
@container lo (max-width: 430px) {.lo-grid {grid-template-columns: 1fr !important;}}
.lo-kpi {background: #fff; border: 1px solid #e3e1da; border-radius: 12px;
  padding: 14px 16px 12px; display: flex; flex-direction: column; min-height: 100%;
  box-sizing: border-box;}
.lo-kpi .l {font-size: 0.84rem; font-weight: 600; color: #4a4945; line-height: 1.3;}
.lo-kpi .v {font-size: 1.6rem; font-weight: 700; color: #141413; line-height: 1.25;
  margin-top: 6px; font-variant-numeric: tabular-nums; overflow-wrap: anywhere;}
.lo-grid.c5 .lo-kpi .v {font-size: 1.35rem;}
.lo-kpi .d {font-size: 0.8rem; font-weight: 600; margin-top: 4px; min-height: 1.1em;}
.lo-kpi .d.good {color: #0e7a50;}
.lo-kpi .d.bad {color: #c0392b;}
.lo-kpi .d.flat {color: #8a8882;}
.lo-kpi .n {font-size: 0.76rem; color: #8a8882; line-height: 1.35; margin-top: auto;
  padding-top: 8px;}
[class*="st-key-card-"] {background: #fff;}
/* KPI with a "how it is computed" note: dotted label, note opens on hover, focus or tap */
.lo-kpi.has-tip {position: relative; cursor: help; outline: none;}
.lo-kpi.has-tip .l {text-decoration: underline dotted #8a8882; text-underline-offset: 3px;}
.lo-kpi .tip {display: none; position: absolute; left: 0; top: calc(100% + 6px); z-index: 50;
  width: max(100%, 340px); max-width: 92vw; box-sizing: border-box; background: #1f2e2d;
  color: #f4f3ee; border-radius: 10px; padding: 10px 12px; font-size: 0.8rem; line-height: 1.45;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.18);}
.lo-kpi .tip p {margin: 0 0 4px; font-size: inherit; line-height: inherit; color: inherit;}
.lo-kpi .tip p:last-child {margin-bottom: 0;}
.lo-kpi.has-tip:hover .tip, .lo-kpi.has-tip:focus .tip, .lo-kpi.has-tip:focus-within .tip {
  display: block;}
.lo-grid > .lo-kpi.has-tip:last-child .tip {left: auto; right: 0;}
.lo-proj {display: grid; grid-template-columns: max-content 1fr; gap: 6px 18px;
  background: #fff; border: 1px solid #e3e1da; border-radius: 12px; padding: 14px 18px;
  margin: 4px 0 14px; font-size: 0.88rem; line-height: 1.45;}
.lo-proj .k {color: #6b6a65; font-weight: 600;}
.lo-proj .x {color: #1f1e1c; min-width: 0; overflow-wrap: anywhere;}
.lo-proj a {color: #0f5257;}
@media (max-width: 560px) {.lo-proj {grid-template-columns: 1fr; gap: 2px;}
  .lo-proj .x {margin-bottom: 6px;}}
.lo-level {font-weight: 700;}
.lo-level.ok {color: #0e7a50;}
.lo-level.warn {color: #a86400;}
.lo-level.no {color: #c0392b;}
/* finished report: green Download button with a short pulse to draw the eye */
.st-key-r_download button {background: #1e8e4e; border-color: #1e8e4e; color: #fff;
  animation: lo-pulse 1.2s ease-out 3;}
.st-key-r_download button:hover {background: #18753f; border-color: #18753f; color: #fff;}
@keyframes lo-pulse {0% {box-shadow: 0 0 0 0 rgba(30, 142, 78, 0.55);}
  100% {box-shadow: 0 0 0 10px rgba(30, 142, 78, 0);}}
.lo-fgrid {display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;
  margin: 6px 0 4px;}
.lo-fgrid.one {grid-template-columns: 1fr;}
@container lo (max-width: 680px) {.lo-fgrid {grid-template-columns: 1fr;}}
.lo-legend {font-size: 0.76rem; color: #6b6a65; margin: 2px 0 4px;}
.lo-legend i {display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  margin: 0 4px -1px 10px;}
.lo-table {width: 100%; border-collapse: collapse; font-size: 0.86rem; line-height: 1.45;}
.lo-table th {text-align: left; font-weight: 600; color: #55534e; background: #f6f5f1;
  border-bottom: 1px solid #e3e1da; padding: 7px 10px; font-size: 0.78rem;}
.lo-table td {border-bottom: 1px solid #f0efea; padding: 7px 10px; vertical-align: top;
  color: #2b2a27; overflow-wrap: anywhere;}
.lo-table td.n {color: #8a8882; width: 1%; white-space: nowrap;}
.lo-table td.nw {white-space: nowrap;}
.lo-table td.num {text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums;}
.lo-item {border: 1px solid #e3e1da; border-left: 4px solid #c3c2b7; border-radius: 10px;
  padding: 14px 16px 12px; background: #fff;}
.lo-item.good {border-left-color: #1baf7a;} .lo-item.bad {border-left-color: #d03b3b;}
.lo-item.risk {border-left-color: #e09a00;}
.lo-ihead {display: flex; gap: 8px; align-items: center; margin-bottom: 6px;}
.lo-tone {font-size: 0.72rem; font-weight: 700; padding: 2px 9px; border-radius: 999px;}
.lo-tone.good {background: #e3f4ec; color: #0e6b46;}
.lo-tone.bad {background: #fbe8e6; color: #a32a1f;}
.lo-tone.risk {background: #fcf1d6; color: #7d5300;}
.lo-tone.neutral {background: #efeee9; color: #55534e;}
.lo-topic {font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  color: #8a8882;}
.lo-ititle {font-size: 1rem; font-weight: 700; color: #141413; line-height: 1.4;
  margin-bottom: 8px;}
.lo-part {margin-top: 6px; font-size: 0.88rem; line-height: 1.55; color: #2b2a27;}
.lo-part .k {display: block; font-size: 0.72rem; font-weight: 700; color: #6b6a65;
  text-transform: uppercase; letter-spacing: 0.05em;}
.lo-part.action {background: #f2f7f6; border-radius: 8px; padding: 8px 10px; margin-top: 10px;}
.lo-part.action .k {color: #0f5257;}
.lo-banner {background: #fff; color: #141413; border: 1px solid #e3e1da;
  border-left: 6px solid #0f5257; border-radius: 12px; padding: 16px 22px 14px;
  margin: 0 0 14px;}
.lo-banner .t {font-size: 1.5rem; font-weight: 700; line-height: 1.25; color: #0f2e2c;}
.lo-banner .d {margin-top: 4px; font-size: 0.9rem; color: #55534e; line-height: 1.45;}
.lo-banner .s {display: inline-block; margin-top: 10px; font-size: 0.76rem; font-weight: 600;
  color: #0f5257; background: #eaf3f2; border: 1px solid #cfe3e1; padding: 2px 10px;
  border-radius: 999px;}
.lo-chead {display: flex; justify-content: space-between; align-items: baseline; gap: 6px 12px;
  flex-wrap: wrap; padding-bottom: 8px; border-bottom: 1px solid #eeede8; margin-bottom: 2px;}
.lo-chead .t {font-weight: 700; font-size: 0.98rem; color: #141413; line-height: 1.35;}
.lo-unit {font-size: 0.72rem; font-weight: 600; color: #55534e; background: #f3f2ee;
  border: 1px solid #e3e1da; border-radius: 6px; padding: 2px 8px;}
.lo-callout {background: #f2f7f6; border-left: 4px solid #0f5257; border-radius: 6px;
  padding: 10px 14px; font-size: 0.86rem; line-height: 1.55; color: #2b2a27; margin: 4px 0 2px;}
.lo-callout b {color: #0f5257;}
.lo-note {font-size: 0.82rem; color: #6b6a65; line-height: 1.5; margin: 0.2rem 0 0.4rem;}
</style>
"""


@dataclass(frozen=True)
class Kpi:
    label: str
    value: str
    delta: str | None = None
    tone: str = "flat"  # good | bad | flat
    note: str | None = None
    tip: list[str] | None = None  # how the value is computed, shown on hover or tap


def kpi_grid(items: list[Kpi], cols: int = 4) -> str:
    """Equal-size KPI cards; the delta line is kept (blank) when any card in the grid has one."""
    show_delta = any(k.delta for k in items)
    cards = []
    for k in items:
        delta = (
            f'<div class="d {escape(k.tone)}">{escape(k.delta) if k.delta else "&nbsp;"}</div>'
            if show_delta
            else ""
        )
        note = f'<div class="n">{escape(k.note)}</div>' if k.note else ""
        tip, attrs = "", ""
        if k.tip:
            lines = "".join(f"<p>{escape(line)}</p>" for line in k.tip)
            tip, attrs = f'<div class="tip" role="tooltip">{lines}</div>', ' tabindex="0"'
        cards.append(
            f'<div class="lo-kpi{" has-tip" if k.tip else ""}"{attrs}>'
            f'<div class="l">{escape(k.label)}</div>'
            f'<div class="v">{escape(k.value)}</div>{delta}{note}{tip}</div>'
        )
    return f'<div class="lo-wrap"><div class="lo-grid c{cols}">{"".join(cards)}</div></div>'


def project_card(rows: list[tuple[str, str, str | None]]) -> str:
    """What the project is about and where the data comes from: (label, text, link or None)."""
    cells = "".join(
        f'<div class="k">{escape(k)}</div><div class="x">'
        + (
            f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(text)}</a>'
            if url
            else escape(text)
        )
        + "</div>"
        for k, text, url in rows
    )
    return f'<div class="lo-proj">{cells}</div>'


def group_label(text: str) -> str:
    return f'<div class="lo-group">{escape(text)}</div>'


def findings_html(items: list[dict], parts: dict[str, str]) -> str:
    """Findings as cards: tone chip and topic, a plain title, then what happened, its impact
    (or, for information, what it means) and the recommended action when there is one."""

    def card(i: dict) -> str:
        impact_label = parts["meaning"] if i["level"] == "info" else parts["impact"]
        rows = [
            f'<div class="lo-part"><span class="k">{escape(parts["what"])}</span>'
            f"{escape(i['what'])}</div>",
            f'<div class="lo-part"><span class="k">{escape(impact_label)}</span>'
            f"{escape(i['impact'])}</div>",
        ]
        if i.get("action"):
            rows.append(
                f'<div class="lo-part action"><span class="k">{escape(parts["action"])}</span>'
                f"{escape(i['action'])}</div>"
            )
        return (
            f'<div class="lo-item {escape(i["tone"])}"><div class="lo-ihead">'
            f'<span class="lo-tone {escape(i["tone"])}">{escape(i["tone_label"])}</span>'
            f'<span class="lo-topic">{escape(i["topic_label"])}</span></div>'
            f'<div class="lo-ititle">{escape(i["title"])}</div>{"".join(rows)}</div>'
        )

    layout = "lo-fgrid one" if len(items) == 1 else "lo-fgrid"
    return (
        f'<div class="lo-wrap"><div class="{layout}">{"".join(card(i) for i in items)}</div></div>'
    )


def findings_text(
    heading: str, groups: list[tuple[str, str, list[dict]]], parts: dict[str, str]
) -> str:
    """Findings as text for print: a coloured heading per level (priority red, watch amber,
    reference grey) with its count; each finding a numbered title with its tone, the facts as
    bullets and the recommended action set off by a rule."""
    out = [f'<h3 class="p-h3">{escape(heading)}</h3>']
    for level, level_name, items in groups:
        out.append(
            f'<h4 class="p-level {escape(level)}">{escape(level_name)} ({len(items)})</h4>'
            '<ol class="p-findings">'
        )
        for i in items:
            impact = parts["meaning"] if i["level"] == "info" else parts["impact"]
            bullets = "".join(
                f"<li><b>{escape(k)}:</b> {escape(v)}</li>"
                for k, v in ((parts["what"], i["what"]), (impact, i["impact"]))
            )
            action = (
                f'<p class="p-action"><b>{escape(parts["action"])}:</b> {escape(i["action"])}</p>'
                if i.get("action")
                else ""
            )
            out.append(
                f'<li><p class="p-ftitle"><b>{escape(i["title"])}</b></p>'
                f'<p class="p-tags"><span class="p-tone {escape(i["tone"])}">'
                f"{escape(i['tone_label'])}</span> · {escape(i['topic_label'])}</p>"
                f'<ul class="p-parts">{bullets}</ul>{action}</li>'
            )
        out.append("</ol>")
    return "".join(out)


def kpi_text(items: list[Kpi]) -> str:
    """KPI cards as a table for print: indicator, value (with its change), and how to read it."""
    rows = []
    for k in items:
        change = f'<div class="p-delta">{escape(k.delta)}</div>' if k.delta else ""
        notes = [k.note] if k.note else []
        notes += k.tip or []
        note = "".join(f"<p>{escape(n)}</p>" for n in notes)
        rows.append(
            f'<tr><td>{escape(k.label)}</td><td class="num">{escape(k.value)}{change}</td>'
            f"<td>{note}</td></tr>"
        )
    return f'<table class="p-kpis"><tbody>{"".join(rows)}</tbody></table>'


def page_header(title: str, description: str, scope: str) -> str:
    return (
        f'<div class="lo-banner"><div class="t">{escape(title)}</div>'
        f'<div class="d">{escape(description)}</div><span class="s">{escape(scope)}</span></div>'
    )


def chart_header(title: str, unit: str | None = None) -> str:
    """A card title with its unit on the right, e.g. 'Unit: USD millions'."""
    chip = f'<span class="lo-unit">{escape(unit)}</span>' if unit else ""
    return f'<div class="lo-chead"><span class="t">{escape(title)}</span>{chip}</div>'


def callout(lead: str, text: str) -> str:
    """The reading note under a chart: a bold lead-in, then the explanation."""
    return f'<div class="lo-callout"><b>{escape(lead)}</b> {escape(text)}</div>'


def tone_legend(labels: dict[str, str], prefix: str) -> str:
    """What the coloured left edge of a finding means (its tone, not its level)."""
    colors = {"bad": "#d03b3b", "risk": "#e09a00", "good": "#1baf7a", "neutral": "#c3c2b7"}
    keys = ("bad", "risk", "good", "neutral")
    items = "".join(f'<i style="background:{colors[k]}"></i>{escape(labels[k])}' for k in keys)
    return f'<div class="lo-legend">{escape(prefix)}{items}</div>'


class Html(str):
    """A table cell that is already HTML (not escaped)."""


def level_text(text: str, level: str) -> Html:
    """A rating written as coloured text: ok (green), warn (amber), no (red)."""
    return Html(f'<span class="lo-level {escape(level)}">{escape(text)}</span>')


def html_table(
    columns: list[str],
    rows: list[list],
    numeric: set[int] = frozenset(),
    nowrap: set[int] = frozenset(),
    numbered: bool = True,
) -> str:
    """A numbered table whose long text wraps inside the cell (st.dataframe truncates it)."""
    head = ("<th></th>" if numbered else "") + "".join(f"<th>{escape(c)}</th>" for c in columns)
    body = "".join(
        "<tr>"
        + (f'<td class="n">{n}</td>' if numbered else "")
        + "".join(
            f'<td class="{"num" if i in numeric else "nw" if i in nowrap else ""}">'
            f"{v if isinstance(v, Html) else escape(str(v))}</td>"
            for i, v in enumerate(row)
        )
        + "</tr>"
        for n, row in enumerate(rows, start=1)
    )
    return f'<table class="lo-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def note(text: str) -> str:
    return f'<div class="lo-note">{escape(text)}</div>'
