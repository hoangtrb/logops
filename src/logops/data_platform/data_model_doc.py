"""Render docs/02-data-model(.vi).md from schema.py: a Mermaid ER diagram + a data dictionary.

The warehouse has no physical PK/FK constraints (DuckDB would block rebuilds and reject flagged
rows), so this document is where the relationships are made visible. It is generated, never
hand-edited, and a test fails if it drifts from schema.py.
"""

from collections.abc import Iterable
from pathlib import Path

from logops.data_platform.schema import TableSchema

LANGUAGES = ("en", "vi")

LABELS = {
    "en": {
        "title": "# 02 · Data Model",
        "banner": (
            "> Generated from `src/logops/data_platform/schema.py` by `uv run logops docs`. "
            "Do not edit by hand. · Vietnamese: [02-data-model.vi.md](02-data-model.vi.md)"
        ),
        "intro": (
            "The warehouse declares no physical PK/FK constraints: in DuckDB they would stop the "
            "build on a bad row instead of flagging it, and block rebuilding parent tables. The "
            "keys below are declared in `schema.py` and checked on every build by the "
            "data-quality rules `pk_unique`, `fk_missing` and `fk_orphan` (results in the "
            "`dq_findings` table)."
        ),
        "relationships": "## Relationships",
        "how_to_read": (
            'Each line `parent ||--o{ child : "column"` reads: one parent row has zero or more '
            "child rows, joined on that column. Only key columns are shown; every column is "
            "listed in the data dictionary below."
        ),
        "dictionary": "## Data dictionary",
        "primary_key": "Primary key",
        "column": "Column",
        "type": "Type",
        "key": "Key",
        "references": "references",
    },
    "vi": {
        "title": "# 02 · Mô hình dữ liệu",
        "banner": (
            "> Sinh tự động từ `src/logops/data_platform/schema.py` bằng `uv run logops docs`. "
            "Không sửa tay. · Bản tiếng Anh: [02-data-model.md](02-data-model.md)"
        ),
        "intro": (
            "Kho dữ liệu không khai báo ràng buộc PK/FK vật lý: trong DuckDB, ràng buộc sẽ làm "
            "build dừng hẳn khi gặp dòng lỗi thay vì đánh dấu, và chặn việc dựng lại bảng cha. "
            "Các khóa dưới đây được khai báo trong `schema.py` và được kiểm mỗi lần build bằng "
            "các quy tắc chất lượng `pk_unique`, `fk_missing` và `fk_orphan` (kết quả trong bảng "
            "`dq_findings`)."
        ),
        "relationships": "## Quan hệ giữa các bảng",
        "how_to_read": (
            'Mỗi dòng `cha ||--o{ con : "cột"` đọc là: một dòng ở bảng cha có không hoặc nhiều '
            "dòng ở bảng con, nối qua cột đó. Sơ đồ chỉ hiện các cột khóa; mọi cột được liệt kê "
            "trong từ điển dữ liệu bên dưới."
        ),
        "dictionary": "## Từ điển dữ liệu",
        "primary_key": "Khóa chính",
        "column": "Cột",
        "type": "Kiểu",
        "key": "Khóa",
        "references": "tham chiếu",
    },
}


def doc_path(docs_dir: Path, lang: str) -> Path:
    return docs_dir / ("02-data-model.md" if lang == "en" else f"02-data-model.{lang}.md")


def render(tables: Iterable[TableSchema], lang: str) -> str:
    tables = list(tables)
    t = LABELS[lang]
    lines = [t["title"], "", t["banner"], "", t["intro"], "", t["relationships"], ""]
    lines += [t["how_to_read"], "", *_mermaid(tables), "", t["dictionary"], ""]
    for table in tables:
        pk = ", ".join(f"`{c}`" for c in table.primary_key)
        lines += [f"### `{table.name}`", "", f"{t['primary_key']}: {pk}", ""]
        lines += [f"| {t['column']} | {t['type']} | {t['key']} |", "|---|---|---|"]
        for column, dtype in table.columns.items():
            key = _key_markers(table, column)
            if column in table.foreign_keys:
                key += f" ({t['references']} `{table.foreign_keys[column]}`)"
            lines.append(f"| `{column}` | {dtype} | {key} |")
        lines.append("")
    return "\n".join(lines)


def write_docs(tables: Iterable[TableSchema], docs_dir: Path) -> list[Path]:
    tables = list(tables)
    paths = []
    for lang in LANGUAGES:
        path = doc_path(docs_dir, lang)
        path.write_text(render(tables, lang), encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def _mermaid(tables: list[TableSchema]) -> list[str]:
    lines = ["```mermaid", "erDiagram"]
    for table in tables:
        for column, parent in table.foreign_keys.items():
            lines.append(f'    {parent} ||--o{{ {table.name} : "{column}"')
    for table in tables:
        lines.append(f"    {table.name} {{")
        for column, dtype in table.columns.items():
            if markers := _key_markers(table, column):
                lines.append(f"        {dtype} {column} {markers}")
        lines.append("    }")
    lines.append("```")
    return lines


def _key_markers(table: TableSchema, column: str) -> str:
    markers = [
        m
        for m, on in [("PK", column in table.primary_key), ("FK", column in table.foreign_keys)]
        if on
    ]
    return ", ".join(markers)
