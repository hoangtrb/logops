import datetime as dt
import shutil

import duckdb

from logops.data_platform.ingest import ingest_table
from logops.data_platform.schema import TABLES


def test_keys_reference_declared_columns_and_tables():
    assert len(TABLES) == 14
    for table in TABLES.values():
        assert set(table.primary_key) <= set(table.columns), table.name
        for column, parent in table.foreign_keys.items():
            assert column in table.columns, f"{table.name}.{column}"
            assert parent in TABLES, f"{table.name}.{column} -> {parent}"
            assert len(TABLES[parent].primary_key) == 1, f"{parent} has a composite key"


def test_microsecond_timestamps_booleans_and_empty_fk(tmp_path, fixtures_dir):
    shutil.copy(fixtures_dir / "delivery_events.csv", tmp_path / "delivery_events.csv")

    parquet = ingest_table(TABLES["delivery_events"], tmp_path, tmp_path / "parquet")

    rows = duckdb.sql(
        f"SELECT actual_datetime, on_time_flag, facility_id "
        f"FROM read_parquet('{parquet.as_posix()}') ORDER BY event_id"
    ).fetchall()
    assert rows == [
        (dt.datetime(2022, 1, 1, 20, 58, 55, 918185), False, "FAC00034"),
        (dt.datetime(2022, 1, 2, 17, 41, 2, 500000), True, None),
    ]
