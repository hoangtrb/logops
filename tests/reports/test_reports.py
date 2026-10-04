"""The report holds every dashboard page as a tab, matches the dashboard and prints to PDF."""

import datetime as dt

import pytest

from logops import config
from logops.dashboard.pages import ORDER
from logops.reports import build_html, file_name
from logops.reports.pdf import PAGE_TOKEN, destinations, find_browser, to_pdf

FULL = (dt.date(2022, 1, 1), dt.date(2024, 12, 31))
needs_warehouse = pytest.mark.skipif(
    not config.WAREHOUSE_PATH.is_file(), reason="run `logops build` first"
)


def test_file_name_follows_the_language():
    assert file_name("vi", *FULL, "pdf") == "bao-cao-van-tai-2022-01-01-2024-12-31.pdf"
    assert file_name("en", *FULL, "html").startswith("transport-report-")


def test_destinations_follow_the_page_tree():
    pdf = (
        b"1 0 obj <</Type /Catalog /Pages 2 0 R /Dests 9 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R 4 0 R] /Count 3>> endobj\n"
        b"3 0 obj <</Type /Page>> endobj\n"
        b"4 0 obj <</Type /Pages /Kids [5 0 R 6 0 R] /Count 2>> endobj\n"
        b"5 0 obj <</Type /Page>> endobj\n"
        b"6 0 obj <</Type /Page>> endobj\n"
        b"9 0 obj <</fig-1-1 [5 0 R /XYZ 0 0 0] /summary [3 0 R /XYZ 0 0 0]>> endobj\n"
    )
    assert destinations(pdf) == {"fig-1-1": 2, "summary": 1}
    assert destinations(b"%PDF-1.4 no catalog") == {}


@pytest.mark.slow
@needs_warehouse
def test_report_has_every_page_as_a_tab_and_opens_offline():
    seen = []
    html = build_html(*FULL, "vi", today=dt.date(2026, 10, 4), progress=seen.append)
    assert html.startswith("<!doctype html>")
    assert "Plotly" in html and "<script src=" not in html  # library inlined: opens offline
    assert "Báo cáo quản lý vận tải" in html
    assert "Ngày xuất: 04/10/2026" in html and "Khoảng thời gian: 01/01/2022 – 31/12/2024" in html
    for key, _render in ORDER:
        assert f'id="{key.removeprefix("p_")}"' in html
    assert html.count('class="r-tabpanel" id=') == len(ORDER)
    assert seen == sorted(seen) and seen[-1] == pytest.approx(1.0)


@pytest.mark.slow
@needs_warehouse
def test_overview_tab_shows_the_dashboard_figures_in_english_for_one_year():
    from logops.analysis.service import scorecard
    from logops.dashboard.charts import fmt, money
    from logops.dashboard.data import _run

    year = (dt.date(2024, 1, 1), dt.date(2024, 12, 31))
    html = build_html(*year, "en")
    card = _run(scorecard, *year)
    f = fmt("en")
    for x in ("revenue", "op_cost", "contribution"):
        assert money(f, "en", card[x]) in html
    assert f.pct(card["otd_pct"] / 100) in html
    assert "Transport management report" in html


@pytest.mark.slow
@needs_warehouse
def test_printed_report_opens_every_tab_and_puts_wide_tables_on_landscape_sheets():
    html = build_html(*FULL, "vi", for_print=True)
    assert 'class="r-tabpanel" id="profit" hidden' not in html
    assert 'class="r-card wide"' in html and "size: A4 landscape" in html
    assert "counter(page)" in html  # page numbers in the footer
    assert "kaggle.com/datasets/yogape/logistics-operations-database" in html  # data source
    assert "<body class=paper>" in html and "Times New Roman" in html  # a printed report
    assert 'class="p-findings"' in html and 'class="p-kpis"' in html  # findings and KPIs as text
    assert 'class="lo-item' not in html  # no finding cards on paper
    for heading in ("Mục lục", "Danh mục hình", "Danh mục bảng", "Tóm tắt điều hành"):
        assert heading in html
    refs = set(PAGE_TOKEN.findall(html))
    assert {"summary", "overview", "fig-1-1", "tab-2-1"} <= refs
    assert all(f'id="{r}"' in html for r in refs)  # every list entry has its target


@pytest.mark.slow
@needs_warehouse
@pytest.mark.skipif(find_browser() is None, reason="no Edge or Chrome for PDF output")
def test_pdf_output():
    pdf = to_pdf(build_html(*FULL, "vi", for_print=True))
    assert pdf.startswith(b"%PDF-") and len(pdf) > 10_000
    pages = destinations(pdf)  # the targets the contents and the lists point to
    assert pages["summary"] < pages["overview"] < pages["data"]
