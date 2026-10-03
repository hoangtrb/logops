"""Full build on the real Kaggle dataset. Skipped when dataset/ is not downloaded."""

import csv

import duckdb
import pytest

from logops import config
from logops.data_platform.ingest import ingest_table
from logops.data_platform.schema import TABLES
from logops.data_platform.warehouse import load_warehouse

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        not (config.DATASET_DIR / "trips.csv").is_file(), reason="dataset/ not downloaded"
    ),
]


def csv_record_count(table) -> int:
    with (config.DATASET_DIR / table.csv_name).open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.reader(f)) - 1  # minus header


def test_all_tables_load_with_csv_row_counts(tmp_path):
    for table in TABLES.values():
        ingest_table(table, config.DATASET_DIR, tmp_path / "parquet")
    db_path = tmp_path / "warehouse.duckdb"
    load_warehouse(TABLES.values(), tmp_path / "parquet", db_path)

    with duckdb.connect(str(db_path), read_only=True) as con:
        loaded = {n for (n,) in con.execute("SELECT table_name FROM duckdb_tables()").fetchall()}
        assert loaded == set(TABLES)
        for table in TABLES.values():
            rows = con.execute(f'SELECT count(*) FROM "{table.name}"').fetchone()[0]
            assert rows == csv_record_count(table), table.name


def test_key_rules_run_on_real_data_without_dropping_rows(tmp_path):
    from logops.data_platform.quality import key_rules, run_quality

    for table in TABLES.values():
        ingest_table(table, config.DATASET_DIR, tmp_path / "parquet")
    db_path = tmp_path / "warehouse.duckdb"
    load_warehouse(TABLES.values(), tmp_path / "parquet", db_path)
    run_quality(db_path, TABLES.values(), key_rules(TABLES.values()))

    with duckdb.connect(str(db_path), read_only=True) as con:
        rules = con.execute("SELECT count(*) FROM dq_findings").fetchone()[0]
        assert rules == len(key_rules(TABLES.values()))
        for table in TABLES.values():
            rows = con.execute(f'SELECT count(*) FROM "{table.name}"').fetchone()[0]
            assert rows == csv_record_count(table), table.name


def test_dq_report_covers_every_table_and_rule_and_is_reproducible(tmp_path):
    from logops.data_platform.dq_report import LANGUAGES, report_path, write_report
    from logops.data_platform.quality import all_rules, run_quality

    for table in TABLES.values():
        ingest_table(table, config.DATASET_DIR, tmp_path / "parquet")
    db_path = tmp_path / "warehouse.duckdb"
    load_warehouse(TABLES.values(), tmp_path / "parquet", db_path)
    rules = all_rules(TABLES.values())
    run_quality(db_path, TABLES.values(), rules)

    first = {p: p.read_bytes() for p in write_report(db_path, TABLES.values(), tmp_path)}
    second = {p: p.read_bytes() for p in write_report(db_path, TABLES.values(), tmp_path)}
    assert first == second  # byte-identical re-run

    for lang in LANGUAGES:
        text = report_path(tmp_path, lang).read_text(encoding="utf-8")
        for table in TABLES:
            assert f"`{table}" in text, (lang, table)
        for rule in rules:
            assert f"`{rule.id}" in text, (lang, rule.label)
