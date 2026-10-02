"""Data-quality rules: each violation is flagged on its row (`dq_issues`), never deleted.

A rule is data: a SQL predicate over one table that is TRUE when a row violates it. Key rules
(`pk_unique`, `fk_missing`, `fk_orphan`) are generated from the PK/FK declarations in schema.py.
`run_quality` rebuilds each table with a `dq_issues` list column and writes a `dq_findings`
summary (one row per rule, including rules with zero violations).
"""

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import duckdb

from logops.data_platform.schema import TableSchema

SEVERITIES = ("error", "warn")
SAMPLE_SIZE = 3


@dataclass(frozen=True)
class Rule:
    table: str
    id: str
    severity: str
    predicate: str  # SQL over the table's columns; TRUE = violation
    column: str | None = None  # set when one table has several rules with the same id

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"{self.table}/{self.id}: severity must be one of {SEVERITIES}")

    @property
    def label(self) -> str:
        """The tag written into `dq_issues`, e.g. `fk_orphan:driver_id`."""
        return f"{self.id}:{self.column}" if self.column else self.id


def key_rules(tables: Iterable[TableSchema]) -> list[Rule]:
    """pk_unique for every table; fk_missing + fk_orphan for every declared foreign key."""
    by_name = {t.name: t for t in tables}
    rules = []
    for t in by_name.values():
        pk = ", ".join(_q(c) for c in t.primary_key)
        pk_null = " OR ".join(f"{_q(c)} IS NULL" for c in t.primary_key)
        rules.append(
            Rule(
                t.name, "pk_unique", "error", f"{pk_null} OR count(*) OVER (PARTITION BY {pk}) > 1"
            )
        )
        for column, parent in t.foreign_keys.items():
            (parent_pk,) = by_name[parent].primary_key
            rules.append(Rule(t.name, "fk_missing", "warn", f"{_q(column)} IS NULL", column))
            rules.append(
                Rule(
                    t.name,
                    "fk_orphan",
                    "error",
                    f"{_q(column)} NOT IN "
                    f"(SELECT {_q(parent_pk)} FROM {_q(parent)} WHERE {_q(parent_pk)} IS NOT NULL)",
                    column,
                )
            )
    return rules


def run_quality(db_path: Path, tables: Iterable[TableSchema], rules: list[Rule]) -> None:
    """Flag every table in place and rewrite `dq_findings`. Safe to run repeatedly."""
    tables = list(tables)
    with duckdb.connect(str(db_path)) as con:
        for t in tables:
            _flag_table(con, t, [r for r in rules if r.table == t.name])
        _write_findings(con, {t.name: t for t in tables}, rules)


def _flag_table(con: duckdb.DuckDBPyConnection, table: TableSchema, rules: list[Rule]) -> None:
    # Select the schema's columns explicitly so a re-run replaces an existing dq_issues column.
    columns = ", ".join(_q(c) for c in table.columns)
    flags = ", ".join(f"CASE WHEN {r.predicate} THEN '{r.label}' END" for r in rules)
    issues = f"list_filter([{flags}], x -> x IS NOT NULL)" if rules else "[]::VARCHAR[]"
    order = ", ".join(_q(c) for c in table.primary_key)
    con.execute(
        f"CREATE OR REPLACE TABLE {_q(table.name)} AS "
        f"SELECT {columns}, {issues} AS dq_issues FROM {_q(table.name)} ORDER BY {order}"
    )


def _write_findings(
    con: duckdb.DuckDBPyConnection, tables: dict[str, TableSchema], rules: list[Rule]
) -> None:
    con.execute(
        "CREATE OR REPLACE TABLE dq_findings (table_name VARCHAR, rule_id VARCHAR, "
        "column_name VARCHAR, severity VARCHAR, violations BIGINT, sample_keys VARCHAR[])"
    )
    for r in rules:
        key = (
            "concat_ws('|', "
            + ", ".join(f"CAST({_q(c)} AS VARCHAR)" for c in tables[r.table].primary_key)
            + ")"
        )
        con.execute(
            f"INSERT INTO dq_findings SELECT ?, ?, ?, ?, count(*), "
            f"coalesce(list(k ORDER BY k)[1:{SAMPLE_SIZE}], []::VARCHAR[]) "
            f"FROM (SELECT {key} AS k FROM {_q(r.table)} WHERE list_contains(dq_issues, ?))",
            [r.table, r.id, r.column, r.severity, r.label],
        )


def _q(identifier: str) -> str:
    return f'"{identifier}"'
