"""The exportable report: every dashboard page for a date range and a language → HTML or PDF."""

from logops.reports.build import build_html
from logops.reports.pdf import NoBrowserError, to_pdf

__all__ = ["NoBrowserError", "build_html", "file_name", "to_pdf"]


def file_name(lang: str, start, end, fmt: str) -> str:
    stem = "bao-cao-van-tai" if lang == "vi" else "transport-report"
    return f"{stem}-{start}-{end}.{fmt}"
