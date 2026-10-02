from logops import config
from logops.data_platform.data_model_doc import LANGUAGES, doc_path, render
from logops.data_platform.schema import TABLES, TableSchema

PARENT = TableSchema("drivers", {"driver_id": "VARCHAR", "name": "VARCHAR"}, ("driver_id",))
CHILD = TableSchema(
    "driver_monthly_metrics",
    {"driver_id": "VARCHAR", "month": "DATE", "miles": "INTEGER"},
    ("driver_id", "month"),
    {"driver_id": "drivers"},
)


def test_diagram_shows_relationships_and_key_columns():
    text = render([PARENT, CHILD], "en")

    assert "```mermaid\nerDiagram" in text
    assert '    drivers ||--o{ driver_monthly_metrics : "driver_id"' in text
    assert "        VARCHAR driver_id PK, FK" in text  # composite PK that is also a FK
    assert "        DATE month PK" in text
    assert "INTEGER miles" not in text.split("```")[1]  # diagram keeps only key columns
    assert "| `miles` | INTEGER |" in text  # ...the dictionary lists every column


def test_both_languages_render_and_differ_only_in_labels():
    en, vi = render([PARENT, CHILD], "en"), render([PARENT, CHILD], "vi")

    assert en != vi
    assert en.split("```")[1] == vi.split("```")[1]  # identical diagram


def test_committed_docs_match_schema():
    """Fails if schema.py changed without running `logops docs`."""
    for lang in LANGUAGES:
        path = doc_path(config.DOCS_DIR, lang)
        assert path.read_text(encoding="utf-8") == render(TABLES.values(), lang), (
            f"{path.name} is stale: run `uv run logops docs`"
        )
