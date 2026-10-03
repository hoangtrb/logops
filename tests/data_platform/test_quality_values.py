"""Each value rule flags its defective fixture row and leaves the clean row alone."""

from collections import Counter

import duckdb
import pytest

from logops.data_platform.quality import VALUE_RULES, run_quality
from logops.data_platform.schema import TABLES

# Reference geography: Atlanta, GA and Chicago, IL (from routes + facilities).
REFERENCE = {
    "routes": [
        {
            "route_id": "R1",
            "origin_city": "Atlanta",
            "origin_state": "GA",
            "destination_city": "Chicago",
            "destination_state": "IL",
        }
    ],
    "facilities": [{"facility_id": "F1", "city": "Atlanta", "state": "GA"}],
}

# (table, row id, values, expected dq_issues). The id column is the table's primary key.
CASES = [
    (
        "trips",
        "clean",
        dict(
            average_mpg=6.5,
            actual_distance_miles=500,
            actual_duration_hours=10,
            fuel_gallons_used=77,
            idle_time_hours=2,
        ),
        [],
    ),
    (
        "trips",
        "mpg",
        dict(
            average_mpg=40,
            actual_distance_miles=500,
            actual_duration_hours=10,
            fuel_gallons_used=77,
            idle_time_hours=2,
        ),
        ["range"],
    ),
    (
        "trips",
        "idle",
        dict(
            average_mpg=6.5,
            actual_distance_miles=500,
            actual_duration_hours=3,
            fuel_gallons_used=77,
            idle_time_hours=5,
        ),
        ["idle_exceeds_duration"],
    ),
    (
        "loads",
        "clean",
        dict(revenue=1000, weight_lbs=20000, pieces=5, fuel_surcharge=50, accessorial_charges=0),
        [],
    ),
    (
        "loads",
        "neg",
        dict(revenue=-5, weight_lbs=20000, pieces=5, fuel_surcharge=50, accessorial_charges=0),
        ["range"],
    ),
    (
        "fuel_purchases",
        "clean",
        dict(
            gallons=100,
            price_per_gallon=4,
            total_cost=400,
            location_city="Atlanta",
            location_state="GA",
        ),
        [],
    ),
    (
        "fuel_purchases",
        "amount",
        dict(
            gallons=100,
            price_per_gallon=4,
            total_cost=480,
            location_city="Atlanta",
            location_state="GA",
        ),
        ["amount_mismatch"],
    ),
    (
        "fuel_purchases",
        "geo",
        dict(
            gallons=100,
            price_per_gallon=4,
            total_cost=400,
            location_city="Atlanta",
            location_state="AZ",
        ),
        ["geo_mismatch:location_state"],
    ),
    ("maintenance_records", "clean", dict(labor_cost=100, parts_cost=50, total_cost=150), []),
    (
        "maintenance_records",
        "amount",
        dict(labor_cost=100, parts_cost=50, total_cost=300),
        ["amount_mismatch"],
    ),
    (
        "safety_incidents",
        "clean",
        dict(
            vehicle_damage_cost=10,
            cargo_damage_cost=5,
            claim_amount=15,
            location_city="Chicago",
            location_state="IL",
        ),
        [],
    ),
    (
        "safety_incidents",
        "amount",
        dict(
            vehicle_damage_cost=10,
            cargo_damage_cost=5,
            claim_amount=99,
            location_city="Chicago",
            location_state="IL",
        ),
        ["amount_mismatch"],
    ),
    (
        "drivers",
        "clean",
        dict(hire_date="2015-01-01", termination_date="2020-01-01"),
        [],
    ),
    (
        "drivers",
        "fired_before_hired",
        dict(hire_date="2015-01-01", termination_date="2010-01-01"),
        ["time_order:termination_date"],
    ),
    ("truck_utilization_metrics", "clean", dict(utilization_rate=0.7), []),
    ("truck_utilization_metrics", "over", dict(utilization_rate=1.4), ["range:utilization_rate"]),
]

# Delivery events need a pickup/delivery pair on the same trip.
EVENTS = [
    # trip OK: pickup 08:00, delivery 12:00, at the facility's city
    ("E1", "OK", "Pickup", "F1", "2022-01-01 08:00", "2022-01-01 08:00", "Atlanta", "GA", []),
    ("E2", "OK", "Delivery", "F1", "2022-01-01 12:00", "2022-01-01 12:00", "Atlanta", "GA", []),
    # trip BAD: delivered (actual) before picked up; scheduled the same way round
    ("E3", "BAD", "Pickup", "F1", "2022-01-02 12:00", "2022-01-02 12:00", "Atlanta", "GA", []),
    (
        "E4",
        "BAD",
        "Delivery",
        "F1",
        "2022-01-02 08:00",
        "2022-01-02 08:00",
        "Atlanta",
        "GA",
        ["time_order:actual_datetime", "time_order:scheduled_datetime"],
    ),
    # event in Chicago, IL (a valid pair) but its facility F1 is in Atlanta
    (
        "E5",
        "GEO",
        "Pickup",
        "F1",
        "2022-01-03 08:00",
        "2022-01-03 08:00",
        "Chicago",
        "IL",
        ["geo_mismatch:facility_id"],
    ),
]


def _insert(con, table, row):
    cols = ", ".join(f'"{c}"' for c in row)
    con.execute(
        f'INSERT INTO "{table}" ({cols}) VALUES ({", ".join("?" * len(row))})', list(row.values())
    )


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "warehouse.duckdb"
    with duckdb.connect(str(path)) as con:
        for t in TABLES.values():
            cols = ", ".join(f'"{c}" {dtype}' for c, dtype in t.columns.items())
            con.execute(f'CREATE TABLE "{t.name}" ({cols})')
        for table, rows in REFERENCE.items():
            for row in rows:
                _insert(con, table, row)
        for table, row_id, values, _ in CASES:
            pk = TABLES[table].primary_key[0]
            _insert(con, table, {pk: row_id, **values})
        for eid, trip, etype, fac, sched, actual, city, state, _ in EVENTS:
            _insert(
                con,
                "delivery_events",
                dict(
                    event_id=eid,
                    trip_id=trip,
                    event_type=etype,
                    facility_id=fac,
                    scheduled_datetime=sched,
                    actual_datetime=actual,
                    location_city=city,
                    location_state=state,
                ),
            )
    return path


def _issues(path, table, row_id):
    pk = TABLES[table].primary_key[0]
    with duckdb.connect(str(path), read_only=True) as con:
        (issues,) = con.execute(
            f'SELECT dq_issues FROM "{table}" WHERE "{pk}" = ?', [row_id]
        ).fetchone()
    return sorted(issues)


@pytest.mark.parametrize(("table", "row_id", "expected"), [(t, r, e) for t, r, _, e in CASES])
def test_value_rule(db, table, row_id, expected):
    run_quality(db, TABLES.values(), VALUE_RULES)
    assert _issues(db, table, row_id) == sorted(expected)


@pytest.mark.parametrize(("event_id", "expected"), [(e[0], e[-1]) for e in EVENTS])
def test_delivery_event_rules(db, event_id, expected):
    run_quality(db, TABLES.values(), VALUE_RULES)
    assert _issues(db, "delivery_events", event_id) == sorted(expected)


def test_rule_labels_are_unique_per_table():
    counts = Counter((r.table, r.label) for r in VALUE_RULES)
    assert [k for k, n in counts.items() if n > 1] == []
    assert {r.table for r in VALUE_RULES} <= set(TABLES)
