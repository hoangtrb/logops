"""Streamlit entry point: `uv run logops dashboard` (or `streamlit run` this file)."""

import streamlit as st

from logops.dashboard import data, pages, ui
from logops.dashboard.charts import fmt
from logops.dashboard.i18n import T
from logops.reports import NoBrowserError, file_name

PAGES = pages.ORDER


def date_range(t: dict, first, last) -> tuple:
    """Start and end dates from a form, so picking dates doesn't reload the page mid-choice.

    The applied range lives in session state until the user presses Apply again.
    """
    applied = st.session_state.get("range", (first, last))
    with st.sidebar.form("date_range", border=False):
        st.markdown(f"**{t['period']}**")
        a = st.date_input(
            t["from"], applied[0], min_value=first, max_value=last, format=t["date_format"]
        )
        b = st.date_input(
            t["to"], applied[1], min_value=first, max_value=last, format=t["date_format"]
        )
        if st.form_submit_button(t["apply"], width="stretch"):
            if a <= b:
                st.session_state["range"] = applied = (a, b)
            else:
                st.error(t["bad_range"])
    return applied


def export(t: dict, lang: str, start, end) -> None:
    """Sidebar "Export report": format, Create button, a status line, then Download.

    The report is made on a worker thread, so the dashboard stays usable. While it runs, a small
    fragment refreshes every second (not the page): the status line shows the progress and the
    Download button fills with green. When it is done the button turns solid green.
    """
    job = st.session_state.get("r_job")
    with st.sidebar.expander(t["r_export"], key="r_panel"):
        fmt = st.segmented_control(
            t["r_format"], ["html", "pdf"], default="html", format_func=str.upper, key="r_fmt"
        )
        st.button(
            t["r_make"],
            width="stretch",
            key="r_make",
            disabled=job is not None,
            on_click=start_job,  # runs before the rerun, so the button is disabled right away
            args=(fmt or "html", lang, start, end),
        )
        st.fragment(report_status, run_every=1 if job else None)(t, lang)


def start_job(fmt: str, lang: str, start, end) -> None:
    progress = [0.0]  # the worker writes, the status fragment reads
    st.session_state["r_job"] = {
        "future": data.start_report(start, end, lang, fmt, progress),
        "progress": progress,
        "name": file_name(lang, start, end, fmt),
        "fmt": fmt,
    }
    st.session_state.pop("r_file", None)


def filling(t: dict, share: float) -> None:
    """The Download button, disabled, filled with green up to `share` (brighter as it fills)."""
    st.button(t["r_download"], key="r_wait", disabled=True, width="stretch")
    p, alpha = round(100 * share), 0.18 + 0.4 * share
    st.html(
        "<style>.st-key-r_wait button {opacity: 1 !important; color: #1f1e1c !important;"
        f"background: linear-gradient(90deg, rgba(30,142,78,{alpha:.2f}) {p}%, #fff {p}%)"
        " !important; transition: background 0.6s;}</style>"
    )


def report_status(t: dict, lang: str) -> None:
    """Status line and Download button for the running or finished report."""
    job = st.session_state.get("r_job")
    if job and job["future"].done():
        del st.session_state["r_job"]
        try:
            st.session_state["r_file"] = (job["future"].result(), job["name"], job["fmt"])
        except NoBrowserError:
            st.session_state["r_error"] = t["r_no_browser"]
        st.rerun(scope="app")  # stop refreshing and enable the Create button again
    if job:
        share = job["progress"][0]
        st.caption(t["r_running"].format(pct=f"{round(100 * share)}%"))
        filling(t, share)
        return
    if err := st.session_state.pop("r_error", None):
        st.error(err)
    if made := st.session_state.get("r_file"):
        content, name, made_fmt = made
        st.caption(t["r_done"].format(name=name))
        st.download_button(
            t["r_download"],
            content,
            file_name=name,
            mime="application/pdf" if made_fmt == "pdf" else "text/html",
            width="stretch",
            type="primary",
            key="r_download",
            on_click="ignore",
        )
    else:
        filling(t, 0.0)


def main() -> None:
    st.set_page_config(page_title="Logistics Ops", layout="wide")
    st.html(ui.CSS)
    lang = (
        st.sidebar.segmented_control(
            "Ngôn ngữ · Language",
            ["vi", "en"],
            default="vi",
            key="lang",
            format_func=lambda x: x.capitalize(),  # "Vi" / "En"
        )
        or "vi"
    )
    t = T[lang]
    try:
        first, last = data.bounds()
    except data.WarehouseUnavailable as e:
        st.error(t["no_warehouse"] if str(e) == "missing" else t["locked"])
        st.stop()
    start, end = date_range(t, first, last)
    export(t, lang, start, end)
    st.sidebar.caption(t["source_note"])

    with st.spinner(t["loading"]):
        bundle = data.bundle(start, end)
    ctx = {"lang": lang, "t": t, "f": fmt(lang), "start": start, "end": end, "bundle": bundle}

    scope = t["applied"].format(a=pages.day(ctx, start), b=pages.day(ctx, end))

    def page(render, key):
        def run():
            st.html(ui.page_header(t[key], t["d" + key.removeprefix("p")], scope))
            render(ctx)

        run.__name__ = render.__name__
        return run

    nav = st.navigation(
        [
            st.Page(
                page(fn, key),
                title=t[key],
                url_path=key.removeprefix("p_"),
                default=(i == 0),
            )
            for i, (key, fn) in enumerate(PAGES)
        ]
    )
    nav.run()


main()
