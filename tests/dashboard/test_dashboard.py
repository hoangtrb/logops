"""Every page runs without errors in both languages; the dashboard computes nothing itself."""

import re
import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from logops import config

DASHBOARD = Path(__file__).parents[2] / "src" / "logops" / "dashboard"
WARM_LOAD_SECONDS = 3  # docs/01 §5: each page under 3 s once cached
PAGES = (
    "overview",
    "optimize",
    "profit",
    "regions",
    "network",
    "service",
    "fleet",
    "fuel",
    "data_page",
)
SCRIPT = """
from logops.dashboard import data, pages
from logops.dashboard.charts import fmt
from logops.dashboard.i18n import T
first, last = data.bounds()
ctx = {{"lang": "{lang}", "t": T["{lang}"], "f": fmt("{lang}"), "start": first, "end": last,
        "bundle": data.bundle(first, last)}}
pages.{page}(ctx)
"""


def test_dashboard_code_has_no_sql():
    for path in DASHBOARD.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"\b(SELECT|execute)\b", text), path.name


def test_every_label_exists_in_both_languages():
    from logops.dashboard.i18n import T

    assert set(T["vi"]) == set(T["en"])


@pytest.mark.slow
@pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first")
@pytest.mark.parametrize("lang", ["vi", "en"])
@pytest.mark.parametrize("page", PAGES)
def test_page_runs_and_reloads_fast(page, lang):
    at = AppTest.from_string(SCRIPT.format(page=page, lang=lang), default_timeout=180)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    began = time.perf_counter()
    at.run()
    assert time.perf_counter() - began < WARM_LOAD_SECONDS


def _html(at) -> str:
    return " ".join(el.proto.body for el in at.get("html"))


@pytest.mark.slow
@pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first")
def test_overview_cards_equal_the_analysis_layer():
    """The cards show the analysis layer's scorecard, read independently of the dashboard."""
    import duckdb

    from logops.analysis.service import data_bounds, scorecard
    from logops.dashboard.charts import fmt, money

    with duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) as con:
        card = scorecard(con, *data_bounds(con))
    f = fmt("vi")
    at = AppTest.from_file(str(DASHBOARD / "app.py"), default_timeout=180)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    shown = _html(at)
    assert "Doanh thu" in shown
    for value in (
        money(f, "vi", card["revenue"]),
        money(f, "vi", card["contribution"]),
        f.pct(card["margin_pct"] / 100),
        f.pct(card["otd_pct"] / 100),
        f.int(card["trips"]),
        f.pct(card["fleet_use_pct"] / 100),
    ):
        assert value in shown, value


def test_finding_cards_show_tone_parts_and_action_only_when_there_is_one():
    from logops.analysis.insights import PARTS
    from logops.dashboard import ui

    base = {"topic_label": "Fleet", "what": "w", "impact": "i"}
    items = [
        base
        | {
            "level": "act",
            "tone": "bad",
            "tone_label": "Negative",
            "title": "a <b>",
            "action": "do it",
        },
        base
        | {"level": "info", "tone": "good", "tone_label": "Positive", "title": "c", "action": None},
    ]
    out = ui.findings_html(items, PARTS["en"])
    assert out.count('class="lo-item ') == 2 and "a &lt;b&gt;" in out
    assert out.count('class="lo-part action"') == 1 and "do it" in out
    assert "What it means" in out and "Impact" in out and "Negative" in out


def test_kpi_cards_keep_an_aligned_delta_row():
    from logops.dashboard import ui

    out = ui.kpi_grid([ui.Kpi("A", "1", "▲ 1%", "good"), ui.Kpi("B", "2")])
    assert out.count('class="d ') == 2
    assert 'class="d ' not in ui.kpi_grid([ui.Kpi("A", "1"), ui.Kpi("B", "2")])


@pytest.mark.slow
@pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first")
def test_date_range_applies_only_when_the_form_is_submitted():
    import datetime as dt

    at = AppTest.from_file(str(DASHBOARD / "app.py"), default_timeout=180)
    at.run()
    picked = (dt.date(2023, 3, 1), dt.date(2024, 6, 30))
    for widget, value in zip(at.sidebar.date_input, picked, strict=True):
        widget.set_value(value)
    at.run()
    assert "01/01/2022 – 31/12/2024" in _html(at)  # picking dates alone changes nothing
    for widget, value in zip(at.sidebar.date_input, picked, strict=True):
        widget.set_value(value)
    at.sidebar.button[0].click()  # Apply
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert "01/03/2023 – 30/06/2024" in _html(at)


def test_html_table_keeps_headers_and_cells_aligned():
    from logops.dashboard import ui

    out = ui.html_table(["A", "B"], [["x <y>", 1.5]], numeric={1}, nowrap={0})
    assert out.index(">A<") < out.index(">B<")
    assert '<td class="nw">x &lt;y&gt;</td><td class="num">1.5</td>' in out


@pytest.mark.slow
@pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first")
def test_sidebar_exports_an_html_report_in_the_background():
    at = AppTest.from_file(str(DASHBOARD / "app.py"), default_timeout=300)
    at.run()
    next(b for b in at.sidebar.button if b.key == "r_make").click()
    at.run()  # returns while the report is still being built
    assert not at.exception, [e.value for e in at.exception]
    job = at.session_state["r_job"]
    assert next(b for b in at.sidebar.button if b.key == "r_make").disabled
    job["future"].result(timeout=300)
    at.run()  # the status fragment picks up the finished file
    assert not at.exception, [e.value for e in at.exception]
    assert "r_job" not in at.session_state
    content, name, fmt = at.session_state["r_file"]
    assert fmt == "html" and name.startswith("bao-cao-van-tai-")
    assert content.startswith(b"<!doctype")
    assert job["progress"][0] == 1.0


def test_report_drawing_never_reaches_streamlit_in_other_threads():
    import threading

    import streamlit

    from logops.dashboard.output import drawing_to, st
    from logops.reports.static import HtmlOut

    seen = []
    with drawing_to(HtmlOut("vi", {})):
        other = threading.Thread(target=lambda: seen.append(st.html))
        other.start()
        other.join()
        st.caption("x")  # goes to the HTML builder, not the app
    assert seen == [streamlit.html]


@pytest.mark.slow
@pytest.mark.skipif(not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first")
def test_savings_tips_add_up_to_the_cards_and_say_what_reaches_the_target():
    from logops.dashboard import data, pages
    from logops.dashboard.charts import fmt
    from logops.dashboard.i18n import T
    from logops.optimize import report

    ctx = {"lang": "en", "t": T["en"], "f": fmt("en")}
    d = data.optimization(0.0)
    rec = report.recommendations(d, "en")
    tot = report.totals(d)
    tips = pages.savings_tips(ctx, d, rec, tot)
    musd = pages._musd(ctx)
    assert musd(tot["target"]) in tips["target"][-1]
    measured_items = [x for x in tips["measured"] if x.startswith("• ")]
    assert len(measured_items) == rec.filter(rec["impact_type"] == "measured").height
    assert musd(tot["measured"] + tot["upper"]) in tips["total"][0]
    assert musd(tot["target"] - tot["measured"]) in tips["total"][1]  # the gap still to find
