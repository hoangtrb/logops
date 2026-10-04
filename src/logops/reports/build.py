"""The report: every dashboard page in one self-contained HTML file, one tab per page.

The pages themselves draw the report: their `st.*` calls go to `static.HtmlOut` instead of
Streamlit (see dashboard/output.py), so the report holds exactly the dashboard's figures, charts,
notes and tables, each page in the view it opens with. Plotly is inlined once, so the file opens
without internet.

Printed (PDF) the same file follows a print layout of its own: a cover with the project, the data
source and the contents; numbered sections, each on a new sheet; numbered figures and tables with
no card frames; tables with many columns on a landscape sheet where they belong, never cut; a
header with the period and a footer with the report name, export date and page number.
"""

import base64
import datetime as dt
from collections.abc import Callable
from html import escape

from plotly.offline import get_plotlyjs

from logops import config
from logops.analysis import insights
from logops.dashboard import charts as ch
from logops.dashboard import data, pages, ui
from logops.dashboard.charts import fmt
from logops.dashboard.i18n import T
from logops.dashboard.output import drawing_to
from logops.optimize import report as optimize_report
from logops.reports.static import HtmlOut

SCREEN_CSS = """
body {margin: 0; background: #f6f5f1; color: #1f1e1c;
  font-family: 'Source Sans 3', 'Source Sans Pro', system-ui, 'Segoe UI', sans-serif;}
.r-page {max-width: 1180px; margin: 0 auto; padding: 20px 16px 40px;}
.r-cover {background: #fff; border: 1px solid #e3e1da; border-left: 6px solid #0f5257;
  border-radius: 14px; padding: 18px 22px; margin-bottom: 14px;}
.r-cover h1 {font-size: 1.6rem; margin: 0 0 4px; color: #0f2e2c;}
.r-cover .meta {display: inline-block; font-size: 0.85rem; font-weight: 600; color: #0f5257;
  background: #e6f0ef; border-radius: 999px; padding: 3px 12px; margin: 6px 0 12px;}
.r-cover .note {font-size: 0.82rem; color: #6b6a65; margin: 10px 0 0;}
.r-cover .lo-proj {border: 0; padding: 0; margin: 0;}
.r-toc {display: none;}
.r-card {background: #fff; border: 1px solid #e3e1da; border-radius: 12px;
  padding: 14px 18px 12px; margin: 12px 0; min-width: 0;}
.r-exp {font-size: 1rem; margin-bottom: 8px;}
.r-caption {font-size: 0.85rem; color: #6b6a65; margin: 6px 0;}
.r-shown {display: inline-block; font-size: 0.8rem; color: #55534e; background: #eceae3;
  border-radius: 999px; padding: 3px 10px; margin: 4px 6px 4px 0;}
.r-cols {display: grid; grid-template-columns: var(--cols); gap: 14px; align-items: start;}
.r-col {min-width: 0;}
.r-scroll {overflow: auto; max-height: 560px;}
.r-scroll thead th {position: sticky; top: 0; z-index: 1;}
.r-tabs .r-tabbar {display: flex; flex-wrap: wrap; gap: 2px; border-bottom: 1px solid #e3e1da;
  margin: 8px 0 12px;}
.r-tabs .r-tabbar button {font: inherit; background: none; border: 0; cursor: pointer;
  padding: 8px 12px; color: #6b6a65; font-weight: 600; border-bottom: 2px solid transparent;
  margin-bottom: -1px;}
.r-tabs .r-tabbar button:hover {color: #0f5257;}
.r-tabs .r-tabbar button.on {color: #0f5257; border-bottom-color: #0f5257;}
/* page tabs: two rows (5 + 4), no scrolling */
.r-pages > .r-tabbar {display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px;
  border: 0; margin: 4px 0 8px; padding: 8px 0; background: #f6f5f1;}
.r-pages > .r-tabbar button {background: #fff; border: 1px solid #e3e1da; border-radius: 10px;
  padding: 12px 10px; min-height: 52px; margin: 0; font-size: 0.95rem; line-height: 1.25;
  text-align: center; color: #3d3c38;}
.r-pages > .r-tabbar button:hover {border-color: #0f5257; color: #0f5257;}
.r-pages > .r-tabbar button.on {background: #0f5257; border-color: #0f5257; color: #fff;}
@media (min-width: 900px) {.r-pages > .r-tabbar {position: sticky; top: 0; z-index: 5;}}
.r-section-head {font-size: 1.25rem; font-weight: 700; color: #0f2e2c; margin: 14px 0 2px;}
.r-section-desc {color: #6b6a65; margin: 0 0 8px;}
@media (max-width: 760px) {
  .r-pages > .r-tabbar {grid-template-columns: repeat(3, minmax(0, 1fr));}
  .r-cols {grid-template-columns: 1fr;}
  .r-page {padding: 12px 10px 32px;}
  .r-card, .r-cover {padding: 12px;}
}
@media (max-width: 430px) {.r-pages > .r-tabbar {grid-template-columns: repeat(2, minmax(0, 1fr));}}
"""

PRINT_CSS = """
@media print {
  html {font-size: 9.5pt;}
  body {background: #fff; color: #1f1e1c;}
  .r-page {max-width: none; padding: 0;}
  .modebar-container, .r-pages > .r-tabbar, .r-ftabs > .r-tabbar {display: none !important;}
  .r-tabpanel[hidden] {display: block !important;}

  /* cover: project, data source, contents */
  .r-cover {border: 0; border-radius: 0; padding: 30mm 0 0; margin: 0; break-after: page;}
  .r-cover h1 {font-size: 26pt; color: #0f2e2c; margin-bottom: 4mm;}
  .r-cover .meta {background: none; padding: 0; font-size: 10.5pt; margin: 0 0 10mm;}
  .r-cover .lo-proj {font-size: 10pt; gap: 3mm 8mm; border: 0; border-radius: 0;
    border-top: 1.5pt solid #0f5257; padding-top: 5mm;}
  .r-cover .note {font-size: 9pt; margin-top: 8mm;}
  .r-toc {display: block; margin-top: 12mm; padding-top: 5mm; border-top: 0.5pt solid #c9c7bf;}
  .r-toc h2 {font-size: 12pt; margin: 0 0 3mm; color: #0f2e2c;}
  .r-toc ol {margin: 0; padding-left: 6mm; columns: 2; column-gap: 10mm; font-size: 10pt;
    line-height: 1.8;}

  /* sections: numbered, each on a new sheet */
  .r-pages {counter-reset: sec;}
  .r-pages > .r-tabpanel {break-before: page; counter-increment: sec; counter-reset: fig tab;}
  .r-section-head {font-size: 17pt; margin: 0 0 1mm; padding-bottom: 2mm;
    border-bottom: 1.5pt solid #0f5257;}
  .r-section-head::before {content: counter(sec) ". "; color: #0f5257;}
  .r-section-desc {font-size: 9.5pt; margin: 2mm 0 4mm;}

  /* no card frames: figures and tables on the page, numbered, with their note as a caption */
  .r-card {border: 0; border-radius: 0; padding: 0; margin: 0 0 6mm; background: none;}
  .r-card:has(.js-plotly-plot) {break-inside: avoid;}
  .r-card:has(.js-plotly-plot) .lo-chead .t::before {counter-increment: fig;
    content: var(--fig-word) " " counter(sec) "." counter(fig) ". "; color: #0f5257;}
  .r-card:has(table):not(:has(.js-plotly-plot)) > .lo-chead .t::before {counter-increment: tab;
    content: var(--tab-word) " " counter(sec) "." counter(tab) ". "; color: #0f5257;}
  .lo-chead {border: 0; padding: 0; margin: 0 0 2mm; break-after: avoid;}
  .lo-chead .t {font-size: 10.5pt;}
  .lo-unit {background: none; border: 0; padding: 0; font-size: 8.5pt; color: #6b6a65;}
  .lo-callout {background: none; border: 0; border-left: 1.5pt solid #c9c7bf; border-radius: 0;
    padding: 0 0 0 3mm; margin-top: 1mm; font-size: 8.5pt; color: #4a4945;}
  .r-cols {display: block;}
  .r-shown {background: none; padding: 0; font-style: italic; font-size: 8.5pt;}
  .r-exp {font-size: 11pt; break-after: avoid;}
  .lo-group {margin-top: 4mm; break-after: avoid;}

  /* KPI cards: compact boxes, four or five a row; "how it is computed" printed under the value */
  .lo-grid {gap: 2mm !important; grid-template-columns: repeat(4, minmax(0, 1fr)) !important;}
  .lo-grid.c5 {grid-template-columns: repeat(5, minmax(0, 1fr)) !important;}
  .lo-grid.c2 {grid-template-columns: repeat(2, minmax(0, 1fr)) !important;}
  .lo-kpi {border-radius: 0; border: 0; border-top: 1.5pt solid #0f5257; background: #f7f7f4;
    padding: 2.5mm 3mm; break-inside: avoid;}
  .lo-kpi .l {font-size: 8.5pt;}
  .lo-kpi .v {font-size: 14pt; margin-top: 1mm;}
  .lo-grid.c5 .lo-kpi .v {font-size: 12pt; white-space: nowrap;}
  .lo-kpi .n, .lo-kpi .d {font-size: 7.5pt;}
  .lo-kpi .n {margin-top: 1mm; padding-top: 0;}
  .lo-kpi.has-tip .l {text-decoration: none;}
  .lo-kpi .tip {display: block !important; position: static; width: auto; max-width: none;
    background: none; color: #4a4945; box-shadow: none; padding: 1.5mm 0 0; font-size: 7.5pt;
    border-top: 0.5pt solid #d9d7cf; margin-top: 1.5mm; border-radius: 0;}

  /* findings: one column, every level printed with its name */
  .lo-fgrid {grid-template-columns: 1fr !important; gap: 2.5mm !important;}
  .lo-item {break-inside: avoid; border-radius: 0; padding: 2.5mm 3.5mm; box-shadow: none;}
  .r-ftabs > .r-tabpanel::before {content: attr(data-label); display: block; font-size: 8pt;
    font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #6b6a65;
    margin: 3mm 0 1.5mm; break-after: avoid;}

  /* tables: full length, header repeated on every sheet; wide ones on a landscape sheet */
  .r-scroll {max-height: none; overflow: visible;}
  .lo-table {font-size: 7.5pt; line-height: 1.3;}
  .lo-table th, .lo-table td {padding: 1.2mm 1.8mm; overflow-wrap: normal; word-break: normal;}
  .lo-table thead {display: table-header-group;}
  .lo-table tr {break-inside: avoid;}
  .r-card.wide {page: wide; break-before: page;}
  .lo-proj a {color: inherit; text-decoration: none;}
}
"""

PAPER_CSS = """
/* the PDF: a printed report, not a screen. Times New Roman, black text, dark blue headings,
   tables with thin horizontal rules, findings and KPIs as text (see ui.findings_text, kpi_text) */
body.paper {background: #fff; color: #000; font-size: 11pt; line-height: 1.4;}
.paper, .paper * {font-family: 'Times New Roman', Times, serif !important;}
.paper .r-page {max-width: none; padding: 0;}
.paper .r-pages > .r-tabbar, .paper .modebar-container {display: none !important;}
.paper .r-cover {background: none; border: 0; border-radius: 0; padding: 35mm 0 0; margin: 0;
  break-after: page;}
.paper .r-cover h1 {font-size: 24pt; color: #1f3864; margin: 0 0 3mm;}
.paper .r-cover .meta {background: none; padding: 0; color: #000; font-size: 11pt;
  font-weight: normal; margin: 0 0 12mm;}
.paper .lo-proj {background: none; border: 0; border-top: 1pt solid #000;
  border-bottom: 1pt solid #000; border-radius: 0; padding: 3mm 0; margin: 0; font-size: 11pt;
  gap: 2mm 8mm;}
.paper .lo-proj .k {color: #000; font-weight: bold;}
.paper .lo-proj .x, .paper .lo-proj a {color: #000; text-decoration: none;}
.paper .r-cover .note {font-size: 10pt; font-style: italic; color: #333; margin-top: 6mm;}
.paper .r-toc {display: block; margin-top: 14mm;}
.paper .r-toc h2 {font-size: 13pt; color: #1f3864; margin: 0 0 3mm;}
.paper .r-toc ol {margin: 0; padding-left: 7mm; font-size: 11pt; line-height: 1.8;}

.paper .r-pages {counter-reset: sec;}
.paper .r-pages > .r-tabpanel {display: block !important; break-before: page;
  counter-increment: sec; counter-reset: fig tab;}
.paper .r-section-head {font-size: 16pt; color: #1f3864; margin: 0 0 2mm; padding-bottom: 1.5mm;
  border-bottom: 0.75pt solid #1f3864;}
.paper .r-section-head::before {content: counter(sec) ". ";}
.paper .r-section-desc {font-size: 11pt; font-style: italic; color: #333; margin: 0 0 4mm;}
.paper .lo-group {font-size: 12pt; font-weight: bold; color: #1f3864; text-transform: none;
  letter-spacing: 0; margin: 5mm 0 2mm; break-after: avoid;}
.paper .p-h3 {font-size: 12pt; color: #1f3864; margin: 5mm 0 2mm; break-after: avoid;}
.paper .p-h4 {font-size: 11pt; font-style: italic; margin: 3mm 0 1mm; break-after: avoid;}
.paper .r-shown, .paper .r-caption {background: none; padding: 0; border-radius: 0; color: #333;
  font-size: 10pt; font-style: italic; margin: 0 0 2mm;}
.paper .r-shown b {font-weight: normal;}
.paper .r-shown {display: inline-block; margin: 0 6mm 2mm 0;}
.paper p {margin: 0 0 1.5mm;}

/* figures and tables: no frames, numbered titles, the note as a caption underneath */
.paper .r-card {background: none; border: 0; border-radius: 0; padding: 0; margin: 0 0 6mm;}
.paper .r-card:has(.js-plotly-plot) {break-inside: avoid;}
.paper .r-cols {display: block;}
.paper .lo-chead {border: 0; padding: 0; margin: 0 0 1.5mm; display: block; break-after: avoid;}
.paper .lo-chead .t {font-size: 11pt; font-weight: bold; color: #000;}
.paper .lo-chead .t::before {color: #000;}
.paper .r-card:has(.js-plotly-plot) .lo-chead .t::before {counter-increment: fig;
  content: var(--fig-word) " " counter(sec) "." counter(fig) ". ";}
.paper .r-card:has(table):not(:has(.js-plotly-plot)) > .lo-chead .t::before {
  counter-increment: tab; content: var(--tab-word) " " counter(sec) "." counter(tab) ". ";}
.paper .lo-unit {display: inline; background: none; border: 0; padding: 0 0 0 2mm; color: #333;
  font-size: 10pt; font-style: italic; font-weight: normal;}
.paper .lo-callout {background: none; border: 0; border-radius: 0; padding: 0; margin: 1.5mm 0 0;
  font-size: 10pt; color: #333; text-align: justify;}
.paper .lo-callout b {color: #000;}

/* tables: thin horizontal rules only, header repeated on every sheet */
.paper .r-scroll {max-height: none; overflow: visible;}
.paper .lo-table, .paper .p-kpis {width: 100%; border-collapse: collapse; font-size: 9.5pt;
  line-height: 1.3; border-top: 1pt solid #000; border-bottom: 1pt solid #000;}
.paper .lo-table th {background: none; color: #000; font-weight: bold; text-align: left;
  border-bottom: 0.75pt solid #000; padding: 1.2mm 1.6mm; vertical-align: bottom;}
.paper .lo-table td {border-bottom: 0.25pt solid #bfbfbf; padding: 1.1mm 1.6mm; color: #000;
  overflow-wrap: normal; word-break: normal;}
.paper .lo-table td.n {color: #000;}
.paper .lo-table thead {display: table-header-group;}
.paper .lo-table tr, .paper .p-kpis tr {break-inside: avoid;}
.paper .r-card.wide {page: wide; break-before: page;}
.paper .lo-level {color: #000; font-weight: bold;}

/* KPIs as a table: indicator, value and change, how to read it */
.paper .p-kpis {margin: 0 0 4mm;}
.paper .p-kpis td {border-bottom: 0.25pt solid #bfbfbf; padding: 1.4mm 1.6mm; vertical-align: top;}
.paper .p-kpis td:first-child {width: 30%; font-weight: bold; font-size: 10.5pt;}
.paper .p-kpis td.num {width: 20%; text-align: right; font-size: 11pt; font-weight: bold;
  white-space: nowrap;}
.paper .p-kpis .p-delta {font-size: 9pt; font-weight: normal; font-style: italic;}
.paper .p-kpis td:last-child {color: #333; font-size: 9.5pt;}
.paper .p-kpis td:last-child p {margin: 0 0 0.8mm;}

/* findings as numbered paragraphs */
.paper .p-findings {margin: 0 0 3mm; padding-left: 6mm;}
.paper .p-findings li {margin: 0 0 3mm; break-inside: avoid; text-align: justify;}
.paper .p-ftitle {margin-bottom: 0.8mm;}
"""


FRONT_CSS = """
/* printed front matter: cover, contents, lists of figures and tables, executive summary */
.paper .r-section-head::before, .paper .lo-chead .t::before {content: none !important;}
.paper .lo-chead .t .no {color: #1f3864;}
.paper .r-cover {padding: 22mm 0 0;}
.paper .r-cover-img {display: block; width: 100%; height: 88mm; object-fit: cover;
  margin: 12mm 0 0;}
.paper .r-cover h1 {font-size: 26pt; margin: 0 0 2mm;}
.paper .r-subtitle {font-size: 15pt; color: #1f3864; font-style: italic; margin: 0 0 3mm;}
.paper .r-facts {display: grid; grid-template-columns: 34mm 1fr; margin: 0;
  border-top: 2pt solid #1f3864; border-bottom: 0.75pt solid #1f3864;}
.paper .r-facts .k, .paper .r-facts .x {padding: 2mm 0; border-bottom: 0.25pt solid #bfbfbf;}
.paper .r-facts .k {font-size: 9.5pt; font-weight: bold; color: #1f3864; text-transform: uppercase;
  letter-spacing: 0.04em; padding-top: 2.6mm;}
.paper .r-facts .x {font-size: 11pt;}
.paper .r-facts .key {font-size: 12.5pt; font-weight: bold;}
.paper .r-facts > :nth-last-child(-n + 2) {border-bottom: 0;}
.paper .r-front {break-before: page;}
.paper .r-front h2 {font-size: 16pt; color: #1f3864; margin: 0 0 4mm; padding-bottom: 1.5mm;
  border-bottom: 0.75pt solid #1f3864;}
.paper .p-list {list-style: none; margin: 0 0 8mm; padding: 0; font-size: 11pt;}
.paper .p-list li {margin: 0 0 1.6mm; break-inside: avoid;}
.paper .p-list a {display: flex; align-items: baseline; color: #000; text-decoration: none;}
.paper .p-list .lead {flex: 1; border-bottom: 0.75pt dotted #7f7f7f; margin: 0 2mm;
  min-width: 8mm; transform: translateY(-1mm);}
.paper .p-list .pg {min-width: 6mm; text-align: right;}
.paper .p-list.sections > li {font-weight: bold; margin-bottom: 2.4mm;}
.paper .r-summary {break-before: page;}
.paper .r-summary .p-h3 {font-size: 13pt; margin-top: 6mm;}
.paper .p-bullets {margin: 0 0 3mm; padding-left: 6mm;}
.paper .p-bullets li {margin: 0 0 1.6mm; text-align: justify; break-inside: avoid;}
.paper .p-bullets .p-action {margin-top: 0.8mm;}
.paper .p-h3.act {color: #c00000;}
.paper .p-h3.watch {color: #b45f06;}

/* findings: coloured level headings and tones, facts as bullets, the action set off by a rule */
.paper .p-level {font-size: 11pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 0.03em; margin: 4mm 0 1.5mm; break-after: avoid;}
.paper .p-level.act {color: #c00000;}
.paper .p-level.watch {color: #b45f06;}
.paper .p-level.info {color: #595959;}
.paper .p-tags {font-size: 9.5pt; color: #333; margin: 0 0 1mm;}
.paper .p-tone {font-weight: bold;}
.paper .p-tone.bad {color: #c00000;}
.paper .p-tone.risk {color: #b45f06;}
.paper .p-tone.good {color: #2e7d32;}
.paper .p-tone.neutral {color: #595959;}
.paper .p-parts {margin: 0 0 1.2mm; padding-left: 5mm;}
.paper .p-parts li {margin: 0 0 0.8mm;}
.paper .p-action {border-left: 2.5pt solid #1f3864; padding: 0.5mm 0 0.5mm 3mm;
  margin: 1mm 0 0;}
.paper .p-action b {color: #1f3864;}
"""


TABS_JS = """
document.querySelectorAll('[data-tabs]').forEach(function (group) {
  var buttons = Array.from(group.querySelector(':scope > .r-tabbar').children);
  var panels = Array.from(group.querySelectorAll(':scope > .r-tabpanel'));
  function show(i) {
    buttons.forEach(function (b, j) { b.classList.toggle('on', i === j); });
    panels.forEach(function (p, j) { p.hidden = i !== j; });
    panels[i].querySelectorAll('.js-plotly-plot').forEach(function (d) { Plotly.Plots.resize(d); });
  }
  buttons.forEach(function (b, i) {
    b.addEventListener('click', function () {
      show(i);
      if (group.classList.contains('r-pages')) {
        history.replaceState(null, '', '#' + panels[i].id);
        group.scrollIntoView({block: 'start'});
      }
    });
  });
  if (group.classList.contains('r-pages') && location.hash) {
    var k = panels.findIndex(function (p) { return '#' + p.id === location.hash; });
    if (k > 0) show(k);
  }
});
window.addEventListener('beforeprint', function () {
  document.querySelectorAll('.js-plotly-plot').forEach(function (d) { Plotly.Plots.resize(d); });
});
"""


def _css_text(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def page_css(name: str, exported: str, period: str, t: dict) -> str:
    """A4 sheets (landscape ones named `wide`): period in the header; report name, export date
    and page number in the footer; the cover has neither."""
    font = "font-family: 'Times New Roman', Times, serif; font-size: 9pt; color: #333;"
    boxes = (
        f"@top-right {{content: {_css_text(period)}; {font}}}"
        f"@bottom-left {{content: {_css_text(f'{name} · {exported}')}; {font}}}"
        f'@bottom-right {{content: {_css_text(t["r_page"] + " ")} counter(page) " / " '
        f"counter(pages); {font}}}"
    )
    blank = "@top-right {content: none} @bottom-left {content: none} @bottom-right {content: none}"
    words = f":root {{--fig-word: {_css_text(t['r_fig'])}; --tab-word: {_css_text(t['r_tab'])};}}"
    return (
        f"{words}"
        f"@page {{size: A4; margin: 20mm 20mm 20mm; {boxes}}}"
        f"@page wide {{size: A4 landscape; margin: 18mm 20mm 18mm; {boxes}}}"
        f"@page :first {{{blank}}}"
    )


COVER_IMAGE = config.REPO_ROOT / "reports" / "assets" / "cover.jpg"  # optional


def _cover_image() -> str:
    if not COVER_IMAGE.is_file():
        return ""
    data64 = base64.b64encode(COVER_IMAGE.read_bytes()).decode()
    return f'<img class="r-cover-img" alt="" src="data:image/jpeg;base64,{data64}">'


def _list(items: list[tuple[str, str]], cls: str = "") -> str:
    """Entries that link to their target and show its page, with dotted leaders."""
    rows = "".join(
        f'<li><a href="#{ref}"><span>{label}</span><span class="lead"></span>'
        f'<span class="pg">[[page:{ref}]]</span></a></li>'
        for ref, label in items
    )
    return f'<ul class="p-list {cls}">{rows}</ul>'


def _summary(ctx: dict) -> str:
    """One page for a reader in a hurry: results, what to act on, what to watch, savings."""
    t, f = ctx["t"], ctx["f"]
    s = data.scorecard(ctx["start"], ctx["end"])
    money = lambda x: ch.money(f, ctx["lang"], x)  # noqa: E731
    results = [
        (t["k_revenue"], money(s["revenue"])),
        (t["k_op_cost"], money(s["op_cost"])),
        (t["k_contribution"], money(s["contribution"])),
        (t["k_margin"], f.pct(s["margin_pct"] / 100)),
        (t["k_otd"], f.pct(s["otd_pct"] / 100)),
        (t["k_fleet_use"], f.pct(s["fleet_use_pct"] / 100)),
    ]
    found = ctx["bundle"]["insights"][ctx["lang"]]
    act = [i for i in found if i["level"] == "act"]
    watch = [i for i in found if i["level"] == "watch"]
    d = data.optimization(0.0)
    rec = optimize_report.recommendations(d, ctx["lang"])
    tips = pages.savings_tips(ctx, d, rec, optimize_report.totals(d))
    word = insights.PARTS[ctx["lang"]]["action"]

    def finding(i: dict) -> str:
        action = (
            f'<p class="p-action"><b>{escape(word)}:</b> {escape(i["action"])}</p>'
            if i.get("action")
            else ""
        )
        return f"<li><b>{escape(i['title'])}</b>{action}</li>"

    parts = [
        f'<div class="r-section-head">{escape(t["r_summary"])}</div>',
        f'<h3 class="p-h3">{escape(t["r_sum_results"])}</h3><ul class="p-bullets">'
        + "".join(f"<li>{escape(k)}: <b>{escape(v)}</b></li>" for k, v in results)
        + "</ul>",
    ]
    if act:
        parts.append(
            f'<h3 class="p-h3 act">{escape(t["r_sum_act"])} ({len(act)})</h3>'
            f'<ul class="p-bullets">{"".join(finding(i) for i in act)}</ul>'
        )
    if watch:
        parts.append(
            f'<h3 class="p-h3 watch">{escape(t["r_sum_watch"])} ({len(watch)})</h3>'
            f'<ul class="p-bullets">{"".join(finding(i) for i in watch)}</ul>'
        )
    savings = [f"{t['o_target']}: {tips['target'][-1]}", *tips["total"]]
    scope = pages.scope_note(ctx)
    parts.append(
        f'<h3 class="p-h3">{escape(t["r_sum_savings"])}</h3>'
        + (f'<p class="r-caption">{escape(scope)}</p>' if scope else "")
        + '<ul class="p-bullets">'
        + "".join(f"<li>{escape(line)}</li>" for line in savings)
        + "</ul>"
    )
    return f'<section class="r-summary" id="summary">{"".join(parts)}</section>'


def build_html(
    start: dt.date,
    end: dt.date,
    lang: str = "vi",
    today: dt.date | None = None,
    progress: Callable[[float], None] | None = None,
    for_print: bool = False,
) -> str:
    """The whole report as one HTML string. `progress` gets 0..1 as the pages are drawn.

    `for_print` makes the printed document: every tab open (charts laid out at the sheet's
    width), cover, contents, lists of figures and tables, executive summary, text findings.
    """
    t = T[lang]
    step = progress or (lambda _x: None)
    n = len(pages.ORDER) + 1
    step(0.02)
    ctx = {
        "lang": lang,
        "t": t,
        "f": fmt(lang),
        "start": start,
        "end": end,
        "bundle": data.bundle(start, end),
        "static": True,  # pages leave out what a file can't hold (the map needs the internet)
    }
    step(1 / n)
    day = (lambda d: d.strftime("%d/%m/%Y")) if lang == "vi" else (lambda d: d.isoformat())
    exported = t["r_generated"].format(d=day(today or dt.date.today()))
    period = t["r_period"].format(a=day(start), b=day(end))

    labels, panels, sections, catalog = [], [], [], []
    for i, (key, render) in enumerate(pages.ORDER):
        out = HtmlOut(lang, t, paper=for_print, section=i + 1)
        with drawing_to(out):
            render(ctx)
        body = str(out)  # numbers the figures and tables, in reading order
        catalog += out.catalog
        name = key.removeprefix("p_")
        hidden = " hidden" if i > 0 and not for_print else ""
        head = f"{i + 1}. {t[key]}" if for_print else t[key]
        labels.append(t[key])
        sections.append((name, escape(head)))
        panels.append(
            f'<section class="r-tabpanel" id="{name}"{hidden}>'
            f'<div class="r-section-head">{escape(head)}</div>'
            f'<p class="r-section-desc">{escape(t["d_" + name])}</p>{body}</section>'
        )
        step((i + 2) / n)

    bar = "".join(
        f'<button type="button" role="tab"{" class=on" if i == 0 else ""}>{escape(lb)}</button>'
        for i, lb in enumerate(labels)
    )
    rows = pages.project_rows(ctx)
    if for_print:
        facts = "".join(
            f'<div class="k">{escape(k)}</div>'
            f'<div class="x{" key" if j < 2 else ""}">{escape(text)}</div>'
            for j, (k, text, _url) in enumerate(rows)
        )
        cover = (
            f'<header class="r-cover"><h1>{escape(t["r_title"])}</h1>'
            f'<div class="meta">{escape(exported)} · {escape(period)}</div>'
            f'<div class="r-facts">{facts}</div>'
            f'<p class="note">{escape(t["r_note"])}</p>{_cover_image()}</header>'
        )
        figures = [
            (ref, f"{escape(lb)}. {title}") for kind, ref, lb, title in catalog if kind == "fig"
        ]
        tables = [
            (ref, f"{escape(lb)}. {title}") for kind, ref, lb, title in catalog if kind == "tab"
        ]
        front = (
            f'<section class="r-front"><h2>{escape(t["r_toc"])}</h2>'
            + _list([("summary", escape(t["r_summary"])), *sections], "sections")
            + "</section>"
            + f'<section class="r-front"><h2>{escape(t["r_figs"])}</h2>{_list(figures)}</section>'
            + f'<section class="r-front"><h2>{escape(t["r_tabs"])}</h2>{_list(tables)}</section>'
            + _summary(ctx)
        )
    else:
        cover = (
            f'<header class="r-cover"><h1>{escape(t["r_title"])}</h1>'
            f'<div class="meta">{escape(exported)} · {escape(period)}</div>'
            f"{ui.project_card(rows)}"
            f'<p class="note">{escape(t["r_note"])}</p></header>'
        )
        front = ""
    css = ui.CSS.replace("<style>", "").replace("</style>", "")
    paper = page_css(t["r_title"], exported, period, t)
    extra = PAPER_CSS + FRONT_CSS if for_print else ""
    return (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(t['r_title'])} · {escape(period)}</title>"
        f"<style>{css}{SCREEN_CSS}{PRINT_CSS}{extra}{paper}</style>"
        f'<script type="text/javascript">{get_plotlyjs()}</script></head>'
        f"<body{' class=paper' if for_print else ''}>"
        f'<div class="r-page">{cover}{front}'
        f'<div class="r-tabs r-pages" data-tabs><div class="r-tabbar" role="tablist">{bar}</div>'
        f"{''.join(panels)}</div></div>"
        f"<script>{TABS_JS}</script></body></html>"
    )
