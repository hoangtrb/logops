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


# City/state pairs known to be real: every facility and every route endpoint.
_GEO_REFERENCE = (
    "SELECT city, state FROM facilities "
    "UNION SELECT origin_city, origin_state FROM routes "
    "UNION SELECT destination_city, destination_state FROM routes"
)
_UNKNOWN_PLACE = (
    f"NOT EXISTS (SELECT 1 FROM ({_GEO_REFERENCE}) g(city, state) "
    "WHERE g.city = location_city AND g.state = location_state)"
)


def _delivered_before_pickup(column: str) -> str:
    return (
        f"event_type = 'Delivery' AND {column} < (SELECT max(p.{column}) FROM delivery_events p "
        f"WHERE p.trip_id = delivery_events.trip_id AND p.event_type = 'Pickup')"
    )


# Why each threshold, with sources and evidence: docs/02-dq-rule-thresholds.md.
VALUE_RULES: list[Rule] = [
    Rule(
        "trips",
        "range",
        "error",
        "average_mpg NOT BETWEEN 3 AND 12 OR actual_distance_miles <= 0 "
        "OR actual_duration_hours <= 0 OR fuel_gallons_used <= 0 OR idle_time_hours < 0",
    ),
    Rule("trips", "idle_exceeds_duration", "error", "idle_time_hours > actual_duration_hours"),
    Rule(
        "loads",
        "range",
        "error",
        "revenue <= 0 OR weight_lbs <= 0 OR pieces <= 0 "
        "OR fuel_surcharge < 0 OR accessorial_charges < 0",
    ),
    Rule("fuel_purchases", "range", "error", "gallons <= 0 OR price_per_gallon <= 0"),
    Rule(
        "fuel_purchases",
        "amount_mismatch",
        "warn",
        "abs(total_cost - gallons * price_per_gallon) > 0.01 * total_cost",
    ),
    Rule("fuel_purchases", "geo_mismatch", "warn", _UNKNOWN_PLACE, "location_state"),
    Rule(
        "maintenance_records",
        "range",
        "error",
        "labor_hours < 0 OR labor_cost < 0 OR parts_cost < 0 OR downtime_hours < 0",
    ),
    Rule(
        "maintenance_records",
        "amount_mismatch",
        "warn",
        "abs(total_cost - (labor_cost + parts_cost)) > 0.01 * total_cost",
    ),
    Rule(
        "safety_incidents",
        "range",
        "error",
        "vehicle_damage_cost < 0 OR cargo_damage_cost < 0 OR claim_amount < 0",
    ),
    Rule(
        "safety_incidents",
        "amount_mismatch",
        "warn",
        "abs(claim_amount - (vehicle_damage_cost + cargo_damage_cost)) > 0.01 * claim_amount",
    ),
    Rule("safety_incidents", "geo_mismatch", "warn", _UNKNOWN_PLACE, "location_state"),
    Rule("delivery_events", "range", "error", "detention_minutes < 0"),
    Rule(
        "delivery_events",
        "time_order",
        "error",
        _delivered_before_pickup("actual_datetime"),
        "actual_datetime",
    ),
    Rule(
        "delivery_events",
        "time_order",
        "error",
        _delivered_before_pickup("scheduled_datetime"),
        "scheduled_datetime",
    ),
    Rule("delivery_events", "geo_mismatch", "warn", _UNKNOWN_PLACE, "location_state"),
    # The event's own location vs the city of the facility it claims to be at.
    Rule(
        "delivery_events",
        "geo_mismatch",
        "warn",
        "location_city <> (SELECT f.city FROM facilities f "
        "WHERE f.facility_id = delivery_events.facility_id)",
        "facility_id",
    ),
    Rule("drivers", "time_order", "error", "termination_date < hire_date", "termination_date"),
    Rule(
        "driver_monthly_metrics",
        "range",
        "error",
        "on_time_delivery_rate NOT BETWEEN 0 AND 1 OR average_mpg NOT BETWEEN 3 AND 12 "
        "OR trips_completed < 0",
    ),
    # Over 100% utilization is a definitional question, not necessarily wrong data.
    Rule(
        "truck_utilization_metrics",
        "range",
        "warn",
        "utilization_rate NOT BETWEEN 0 AND 1",
        "utilization_rate",
    ),
]


def all_rules(tables: Iterable[TableSchema]) -> list[Rule]:
    """Key rules generated from the schema plus the value rules for the given tables."""
    tables = list(tables)
    names = {t.name for t in tables}
    return key_rules(tables) + [r for r in VALUE_RULES if r.table in names]


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
