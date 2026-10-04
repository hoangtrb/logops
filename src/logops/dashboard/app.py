"""Streamlit entry point: `uv run logops dashboard` (or `streamlit run` this file)."""

import streamlit as st

from logops.dashboard import data, pages, ui
from logops.dashboard.charts import fmt
from logops.dashboard.i18n import T

PAGES = [
    ("p_overview", pages.overview, "📊"),
    ("p_profit", pages.profit, "💰"),
    ("p_regions", pages.regions, "🗺️"),
    ("p_network", pages.network, "🛣️"),
    ("p_service", pages.service, "⏱️"),
    ("p_fleet", pages.fleet, "🚚"),
    ("p_fuel", pages.fuel, "⛽"),
    ("p_data", pages.data_page, "🧾"),
]


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


def main() -> None:
    st.set_page_config(page_title="Logistics Ops", page_icon="🚚", layout="wide")
    st.html(ui.CSS)
    lang = (
        st.sidebar.segmented_control(
            "🌐",
            ["vi", "en"],
            default="vi",
            key="lang",
            format_func=lambda x: "Tiếng Việt" if x == "vi" else "English",
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
                icon=icon,
                url_path=key.removeprefix("p_"),
                default=(i == 0),
            )
            for i, (key, fn, icon) in enumerate(PAGES)
        ]
    )
    nav.run()


main()
