"""Parquet -> DuckDB warehouse. Each build replaces the tables, so re-running is safe."""

from collections.abc import Iterable
from pathlib import Path

import duckdb

from logops.data_platform.ingest import sql_path
from logops.data_platform.schema import TableSchema


def load_warehouse(tables: Iterable[TableSchema], parquet_dir: Path, db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as con:
        for table in tables:
            parquet = sql_path(parquet_dir / f"{table.name}.parquet")
            con.execute(
                f'CREATE OR REPLACE TABLE "{table.name}" AS SELECT * FROM read_parquet({parquet})'
            )
