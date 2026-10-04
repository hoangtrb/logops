"""Cached access to the analysis layer. The only module that opens the warehouse."""

import datetime as dt
from concurrent.futures import Future, ThreadPoolExecutor

import duckdb
import streamlit as st

from logops import config
from logops.analysis import service
from logops.analysis.bundle import analysis_bundle
from logops.analysis.profit import bridge
from logops.data_platform.dq_report import collect as dq_collect
from logops.data_platform.schema import TABLES
from logops.metrics.kpis import CATALOG, FLEET, kpi
from logops.optimize.report import collect


class WarehouseUnavailable(Exception):
    """The warehouse file is missing or locked by another program."""


def _connect() -> duckdb.DuckDBPyConnection:
    if not config.WAREHOUSE_PATH.is_file():
        raise WarehouseUnavailable("missing")
    try:
        return duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True)
    except duckdb.IOException as e:
        raise WarehouseUnavailable("locked") from e


def _run(fn, *args):
    with _connect() as con:
        return fn(con, *args)


@st.cache_data(show_spinner=False)
def bounds() -> tuple[dt.date, dt.date]:
    return _run(service.data_bounds)


@st.cache_data(show_spinner=False)
def dataset_profile() -> dict:
    return _run(service.dataset_profile)


@st.cache_data(show_spinner=False)
def bundle(start: dt.date, end: dt.date) -> dict:
    return _run(analysis_bundle, start, end)


@st.cache_data(show_spinner=False)
def profit_bridge(year_a: int, year_b: int) -> dict:
    return _run(
        bridge,
        (dt.date(year_a, 1, 1), dt.date(year_a, 12, 31)),
        (dt.date(year_b, 1, 1), dt.date(year_b, 12, 31)),
    )


@st.cache_data(show_spinner=False)
def delivery_timing(start: dt.date, end: dt.date) -> dict:
    return _run(service.delivery_timing, start, end)


@st.cache_data(show_spinner=False)
def scorecard(start: dt.date, end: dt.date) -> dict:
    return _run(service.scorecard, start, end)


@st.cache_data(show_spinner=False)
def service_summary(start: dt.date, end: dt.date, window: int) -> dict:
    return _run(service.service_summary, start, end, window)


@st.cache_data(show_spinner=False)
def sensitivity(start: dt.date, end: dt.date):
    return _run(service.on_time_sensitivity, start, end)


@st.cache_data(show_spinner=False)
def service_by(start: dt.date, end: dt.date, by: str, window: int):
    return _run(service.service_by, start, end, by, window)


@st.cache_data(show_spinner=False)
def detention(start: dt.date, end: dt.date):
    return _run(service.detention_by_type, start, end)


@st.cache_data(show_spinner=False)
def fleet_tables() -> dict:
    return _run(
        lambda con: {
            "status": service.fleet_status(con),
            "idle": service.idle_trucks(con),
            "trucks": service.truck_productivity(con),
        }
    )


@st.cache_data(show_spinner=False)
def fleet_productivity(start: dt.date, end: dt.date) -> dict:
    return _run(service.fleet_productivity, start, end)


@st.cache_data(show_spinner=False)
def customer_names() -> dict:
    return _run(service.customer_names)


@st.cache_data(show_spinner=False)
def optimization(growth: float) -> dict:
    """Recommendations and scenarios over the whole data period (not the sidebar range)."""
    return _run(collect, growth)


PDF_SHARE = 0.85  # of the progress bar spent drawing pages when the PDF print follows


def report_file(start: dt.date, end: dt.date, lang: str, fmt: str, progress: list) -> bytes:
    """The report as bytes; `progress[0]` goes from 0 to 1 while it is made.

    Raises reports.NoBrowserError for PDF without Edge or Chrome.
    """
    from logops.reports import build_html, to_pdf  # the report draws with this module's loaders

    share = PDF_SHARE if fmt == "pdf" else 1.0

    def step(x: float) -> None:
        progress[0] = share * x

    html = build_html(start, end, lang, progress=step, for_print=fmt == "pdf")
    if fmt == "pdf":
        html = to_pdf(html)
    progress[0] = 1.0
    return html if isinstance(html, bytes) else html.encode("utf-8")


_REPORTS = ThreadPoolExecutor(max_workers=2, thread_name_prefix="report")


def start_report(start: dt.date, end: dt.date, lang: str, fmt: str, progress: list) -> Future:
    """Build the report on a worker thread, so the dashboard stays usable while it runs."""
    return _REPORTS.submit(report_file, start, end, lang, fmt, progress)


@st.cache_data(show_spinner=False)
def data_quality() -> dict:
    return _run(dq_collect, TABLES.values())


@st.cache_data(show_spinner=False)
def kpi_glossary(start: dt.date, end: dt.date) -> list[dict]:
    def build(con):
        table = kpi(con, start, end)
        fleet = table.filter(table["group"] == FLEET).row(0, named=True)
        return [
            {
                "name": k.name,
                "area": k.area,
                "unit": k.unit,
                "formula": k.formula,
                "value": fleet[k.name],
            }
            for k in CATALOG
        ]

    return _run(build)
