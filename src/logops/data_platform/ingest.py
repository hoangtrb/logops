"""CSV -> typed Parquet. Types come from schema.py; a value that doesn't fit fails loudly."""

import csv
from pathlib import Path

import duckdb

from logops.data_platform.schema import TableSchema


class IngestError(Exception):
    """A CSV doesn't match its declared schema."""


def ingest_table(table: TableSchema, csv_dir: Path, parquet_dir: Path) -> Path:
    """Read `<table>.csv` with the declared types and write `<parquet_dir>/<table>.parquet`.

    The CSV is read as text first so a bad value can be reported by table, column and value,
    instead of DuckDB silently inferring a looser type.
    """
    csv_path = csv_dir / table.csv_name
    if not csv_path.is_file():
        raise IngestError(f"{table.name}: file not found: {csv_path}")
    _check_header(table, csv_path)

    parquet_dir.mkdir(parents=True, exist_ok=True)
    out = parquet_dir / f"{table.name}.parquet"
    with duckdb.connect() as con:
        con.execute(
            f"CREATE TEMP VIEW raw AS SELECT * "
            f"FROM read_csv({sql_path(csv_path)}, header = true, all_varchar = true)"
        )
        _check_types(con, table)
        casts = ", ".join(f'CAST("{c}" AS {t}) AS "{c}"' for c, t in table.columns.items())
        con.execute(f"COPY (SELECT {casts} FROM raw) TO {sql_path(out)} (FORMAT parquet)")
    return out


def _check_header(table: TableSchema, csv_path: Path) -> None:
    with csv_path.open(newline="", encoding="utf-8") as f:
        header = next(csv.reader(f), [])
    expected = list(table.columns)
    if header != expected:
        raise IngestError(f"{table.name}: header {header} does not match schema {expected}")


def _check_types(con: duckdb.DuckDBPyConnection, table: TableSchema) -> None:
    for column, dtype in table.columns.items():
        if dtype == "VARCHAR":
            continue
        bad = con.execute(
            f'SELECT count(*), any_value("{column}") FROM raw '
            f'WHERE "{column}" IS NOT NULL AND TRY_CAST("{column}" AS {dtype}) IS NULL'
        ).fetchone()
        if bad[0]:
            raise IngestError(
                f"{table.name}.{column}: {bad[0]} value(s) are not {dtype}, e.g. {bad[1]!r}"
            )


def sql_path(path: Path) -> str:
    """A path as a quoted SQL string literal."""
    return "'" + path.as_posix().replace("'", "''") + "'"
