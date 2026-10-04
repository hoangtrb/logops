"""The subset of Streamlit the dashboard pages use, writing HTML instead of a live app.

Widgets show the value the page starts with (its default) as a small "shown: …" chip, so the reader
knows which view the report holds; filters are left open. Columns become a responsive grid, tabs
become script-driven tabs (all panels shown when printed), cards and expanders become cards.
"""

import re
from html import escape

import polars as pl

from logops.dashboard import charts as ch


class _Block:
    """A piece of output with its own buffer; rendered when the report is joined."""

    def __init__(self, out: "HtmlOut", wrap=("", "")):
        self.out, self.wrap, self.parts = out, wrap, []

    def __enter__(self):
        self.out.stack.append(self)
        return self

    def __exit__(self, *exc):
        self.out.stack.pop()

    def __getattr__(self, name):  # c1.selectbox(...) and the like
        return getattr(self.out, name)

    def __str__(self) -> str:
        return self.wrap[0] + "".join(str(p) for p in self.parts) + self.wrap[1]


class _Card(_Block):
    """A card; marked wide when it holds a table with many columns (printed on a landscape page)."""

    wide = False

    def __str__(self) -> str:
        cls = "r-card wide" if self.wide else "r-card"
        body = "".join(str(p) for p in self.parts)
        if self.out.paper:
            body = self.out.number(body)
        return f'<div class="{cls}">{body}</div>'


PAPER_FONT = "'Times New Roman', Times, serif"
WIDE_COLUMNS = 8  # a table with this many columns or more gets a landscape page when printed


class _Row:
    def __init__(self, cols: list[_Block], weights: list[float]):
        self.cols, self.weights = cols, weights

    def __str__(self) -> str:
        cells = [str(c) for c in self.cols]
        if not any(cells):
            return ""
        grid = " ".join(f"minmax(0, {w}fr)" for w in self.weights)
        inner = "".join(f'<div class="r-col">{c}</div>' for c in cells)
        return f'<div class="r-cols" style="--cols: {grid}">{inner}</div>'


class _Tabs:
    def __init__(self, labels: list[str], panels: list[_Block], cls: str):
        self.labels, self.panels, self.cls = labels, panels, cls

    def __str__(self) -> str:
        bar = "".join(
            f'<button type="button" role="tab"{" class=on" if i == 0 else ""}>{escape(lb)}</button>'
            for i, lb in enumerate(self.labels)
        )
        panels = "".join(
            f'<div class="r-tabpanel" data-label="{escape(lb)}"{"" if i == 0 else " hidden"}>'
            f"{p}</div>"
            for i, (lb, p) in enumerate(zip(self.labels, self.panels, strict=True))
        )
        return (
            f'<div class="r-tabs {self.cls}" data-tabs><div class="r-tabbar" role="tablist">{bar}'
            f"</div>{panels}</div>"
        )


class _ColumnConfig:
    @staticmethod
    def NumberColumn(**kw):  # noqa: N802  (mirrors st.column_config)
        return {"type": "number", **kw}

    @staticmethod
    def TextColumn(**kw):  # noqa: N802
        return {"type": "text", **kw}


class HtmlOut:
    column_config = _ColumnConfig()

    def __init__(self, lang: str, labels: dict, paper: bool = False, section: int = 0):
        self.f, self.t = ch.fmt(lang), labels
        self.paper = paper  # drawn for print: pages switch findings and KPIs to text
        self.section, self.counts = section, {"fig": 0, "tab": 0}
        self.catalog: list[tuple[str, str, str, str]] = []  # kind, id, "Figure 2.1", title html
        self.root = _Block(self)
        self.stack = [self.root]

    def number(self, body: str) -> str:
        """Number a card's title as a figure (it holds a chart) or a table, give it an id the
        lists of figures and tables link to, and record it. Cards are numbered as rendered,
        so in reading order."""
        title = re.search(r'<span class="t">(.*?)</span>', body)
        kind = "fig" if "plotly-graph-div" in body else "tab" if "<table" in body else None
        if not title or not kind:
            return body
        self.counts[kind] += 1
        ref = f"{kind}-{self.section}-{self.counts[kind]}"
        word = self.t["r_fig" if kind == "fig" else "r_tab"]
        label = f"{word} {self.section}.{self.counts[kind]}"
        self.catalog.append((kind, ref, label, title.group(1)))
        numbered = (
            f'<span class="t" id="{ref}"><span class="no">{escape(label)}.</span> '
            f"{title.group(1)}</span>"
        )
        return body[: title.start()] + numbered + body[title.end() :]

    # -- writing
    def _add(self, part) -> None:
        self.stack[-1].parts.append(part)

    def html(self, body: str) -> None:
        if "<table" in body:
            self._mark_wide(body.split("</thead>")[0].count("<th"))
        self._add(body)

    def _mark_wide(self, columns: int) -> None:
        if columns >= WIDE_COLUMNS:
            for block in reversed(self.stack):
                if isinstance(block, _Card):
                    block.wide = True
                    break

    def caption(self, text: str) -> None:
        self._add(f'<p class="r-caption">{escape(text)}</p>')

    def markdown(self, text: str) -> None:
        self._add(f"<p>{_bold(text)}</p>")

    def plotly_chart(self, fig, config=None, **_) -> None:
        cfg = {**(config or ch.CONFIG), "responsive": True}
        if self.paper:  # same typeface and ink as the printed text
            fig.update_layout(font_family=PAPER_FONT, font_color="#000000")
        self._add(fig.to_html(full_html=False, include_plotlyjs=False, config=cfg))

    def dataframe(self, df: pl.DataFrame, column_config=None, **_) -> None:
        cols = df.columns
        self._mark_wide(len(cols))
        numeric = {i for i, c in enumerate(cols) if df.schema[c].is_numeric() and i > 0}
        rows = [[self._cell(v) for v in row] for row in df.iter_rows()]
        head = "".join(f"<th>{escape(c)}</th>" for c in cols)
        body = "".join(
            "<tr>"
            + "".join(
                f'<td class="{"n" if i == 0 else "num" if i in numeric else ""}">{escape(v)}</td>'
                for i, v in enumerate(row)
            )
            + "</tr>"
            for row in rows
        )
        self._add(
            f'<div class="r-scroll"><table class="lo-table"><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>"
        )

    def _cell(self, v) -> str:
        if v is None:
            return "—"
        if isinstance(v, bool):
            return str(v)
        if isinstance(v, int):
            return self.f.int(v)
        if isinstance(v, float):
            if v == int(v):
                return self.f.int(v)
            digits = min(3, len(repr(v).split(".")[1]))
            return self.f.num(v, digits)
        return str(v)

    # -- layout
    def container(self, **_) -> _Block:
        block = _Card(self)
        self._add(block)
        return block

    def expander(self, label: str, **_) -> _Block:
        head = f'<div class="r-card"><div class="r-exp">{_bold(label)}</div>'
        block = _Block(self, (head, "</div>"))
        self._add(block)
        return block

    def columns(self, spec, **_) -> list[_Block]:
        weights = [1] * spec if isinstance(spec, int) else list(spec)
        cols = [_Block(self) for _ in weights]
        self._add(_Row(cols, weights))
        return cols

    def tabs(self, labels: list[str], **_) -> list[_Block]:
        panels = [_Block(self) for _ in labels]
        self._add(_Tabs(labels, panels, "r-ftabs"))
        return panels

    # -- widgets: the page's starting value, shown as a chip
    def _shown(self, label: str, value: str) -> None:
        self._add(
            f'<div class="r-shown">{escape(label)}: <b>{escape(value)}</b></div>' if label else ""
        )

    def segmented_control(self, label, options, default=None, format_func=str, **_):
        if default is not None:
            self._shown(label, format_func(default))
        return default

    def selectbox(self, label, options, index=0, format_func=str, **_):
        value = list(options)[index]
        self._shown(label, format_func(value))
        return value

    def slider(self, label, min_value=None, max_value=None, value=None, *args, **_):
        self._shown(label, str(value))
        return value

    def number_input(self, label, min_value=None, max_value=None, value=None, *a, **_):
        self._shown(label, self.f.num(value, 0) if isinstance(value, float) else str(value))
        return value

    def multiselect(self, *args, **kw) -> list:
        return []

    def __str__(self) -> str:
        return str(self.root)


def _bold(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))
