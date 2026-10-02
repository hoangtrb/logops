import duckdb
import pytest

from logops.data_platform.quality import key_rules, run_quality
from logops.data_platform.schema import TableSchema

# A tiny parent/child pair is enough to exercise every key rule.
PARENT = TableSchema("drivers", {"driver_id": "VARCHAR"}, primary_key=("driver_id",))
CHILD = TableSchema(
    "trips",
    {"trip_id": "VARCHAR", "driver_id": "VARCHAR"},
    primary_key=("trip_id",),
    foreign_keys={"driver_id": "drivers"},
)
MONTHLY = TableSchema(
    "driver_monthly_metrics",
    {"driver_id": "VARCHAR", "month": "DATE"},
    primary_key=("driver_id", "month"),
)
TABLES = [PARENT, CHILD, MONTHLY]


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "warehouse.duckdb"
    with duckdb.connect(str(path)) as con:
        con.execute("CREATE TABLE drivers AS SELECT * FROM (VALUES ('D1'), ('D2')) t(driver_id)")
        con.execute(
            """CREATE TABLE trips AS SELECT * FROM (VALUES
                ('T1', 'D1'),   -- clean
                ('T2', 'D1'),   -- duplicate PK
                ('T2', 'D2'),   -- duplicate PK
                ('T3', NULL),   -- missing FK
                ('T4', 'D9')    -- orphan FK
            ) t(trip_id, driver_id)"""
        )
        con.execute(
            """CREATE TABLE driver_monthly_metrics AS SELECT * FROM (VALUES
                ('D1', DATE '2022-01-01'),
                ('D1', DATE '2022-02-01'),
                ('D1', DATE '2022-02-01')   -- duplicate composite PK
            ) t(driver_id, month)"""
        )
    return path


def issues(path, table, key="trip_id"):
    with duckdb.connect(str(path), read_only=True) as con:
        return con.execute(f"SELECT {key}, dq_issues FROM {table} ORDER BY ALL").fetchall()


def finding(path, table, rule, column=None):
    with duckdb.connect(str(path), read_only=True) as con:
        return con.execute(
            "SELECT severity, violations, sample_keys FROM dq_findings "
            "WHERE table_name = ? AND rule_id = ? AND column_name IS NOT DISTINCT FROM ?",
            [table, rule, column],
        ).fetchone()


def test_key_rules_are_generated_from_schema():
    labels = {(r.table, r.label) for r in key_rules(TABLES)}
    assert labels == {
        ("drivers", "pk_unique"),
        ("trips", "pk_unique"),
        ("trips", "fk_missing:driver_id"),
        ("trips", "fk_orphan:driver_id"),
        ("driver_monthly_metrics", "pk_unique"),
    }


def test_each_defect_flagged_once_and_clean_rows_empty(db):
    run_quality(db, TABLES, key_rules(TABLES))

    assert issues(db, "trips") == [
        ("T1", []),
        ("T2", ["pk_unique"]),
        ("T2", ["pk_unique"]),
        ("T3", ["fk_missing:driver_id"]),
        ("T4", ["fk_orphan:driver_id"]),
    ]
    assert all(dq == [] for _, dq in issues(db, "drivers", key="driver_id"))


def test_composite_primary_key(db):
    run_quality(db, TABLES, key_rules(TABLES))

    rows = issues(db, "driver_monthly_metrics", key="month")
    assert [dq for _, dq in rows] == [[], ["pk_unique"], ["pk_unique"]]


def test_findings_table_counts_and_samples(db):
    run_quality(db, TABLES, key_rules(TABLES))

    assert finding(db, "trips", "pk_unique") == ("error", 2, ["T2", "T2"])
    assert finding(db, "trips", "fk_missing", "driver_id") == ("warn", 1, ["T3"])
    assert finding(db, "trips", "fk_orphan", "driver_id") == ("error", 1, ["T4"])
    assert finding(db, "drivers", "pk_unique") == ("error", 0, [])  # checked, nothing found
    assert finding(db, "driver_monthly_metrics", "pk_unique")[2] == [
        "D1|2022-02-01",
        "D1|2022-02-01",
    ]


def test_no_rows_deleted_and_rerun_is_stable(db):
    run_quality(db, TABLES, key_rules(TABLES))
    first = issues(db, "trips")
    run_quality(db, TABLES, key_rules(TABLES))

    assert issues(db, "trips") == first
    assert len(first) == 5
