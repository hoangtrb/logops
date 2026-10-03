"""A tiny fleet whose sizing can be computed by hand.

Trucks: A and B active; C Inactive and D in Maintenance (both never run a trip).
Trips over 10 days (2024-01-01 .. 2024-01-10):
  t1 A day 1, 30 h → occupies days 1-2       t2 B day 1, 10 h → day 1
  t3 A day 5, 20 h → day 5                    t4 (no truck) day 5, 5 h → day 5
  t5 B day 10, 2 h → day 10
Trucks busy per day: d1=2, d2=1, d5=2 (A + the truckless trip), d10=1, other days 0.
Maintenance: A 24 h downtime ($100), C $300, D $200 over the period.
"""

import duckdb
import pytest

from logops.data_platform.schema import TABLES
from logops.metrics.views import create_views

ROWS = {
    "routes": [
        dict(
            route_id="R1",
            origin_city="Atlanta",
            destination_city="Chicago",
            typical_distance_miles=100,
            fuel_surcharge_rate=0.2,
        )
    ],
    "customers": [dict(customer_id="C1", customer_type="Contract")],
    "trucks": [
        dict(truck_id="A", status="Active"),
        dict(truck_id="B", status="Active"),
        dict(truck_id="C", status="Inactive"),
        dict(truck_id="D", status="Maintenance"),
    ],
    "loads": [
        dict(
            load_id=f"L{i}",
            customer_id="C1",
            route_id="R1",
            revenue=100,
            fuel_surcharge=20,
            accessorial_charges=0,
        )
        for i in range(1, 6)
    ],
    "trips": [
        dict(
            trip_id="t1",
            load_id="L1",
            truck_id="A",
            dispatch_date="2024-01-01",
            actual_duration_hours=30,
            actual_distance_miles=100,
            fuel_gallons_used=10,
        ),
        dict(
            trip_id="t2",
            load_id="L2",
            truck_id="B",
            dispatch_date="2024-01-01",
            actual_duration_hours=10,
            actual_distance_miles=100,
            fuel_gallons_used=10,
        ),
        dict(
            trip_id="t3",
            load_id="L3",
            truck_id="A",
            dispatch_date="2024-01-05",
            actual_duration_hours=20,
            actual_distance_miles=100,
            fuel_gallons_used=10,
        ),
        dict(
            trip_id="t4",
            load_id="L4",
            truck_id=None,
            dispatch_date="2024-01-05",
            actual_duration_hours=5,
            actual_distance_miles=100,
            fuel_gallons_used=10,
        ),
        dict(
            trip_id="t5",
            load_id="L5",
            truck_id="B",
            dispatch_date="2024-01-10",
            actual_duration_hours=2,
            actual_distance_miles=100,
            fuel_gallons_used=10,
        ),
    ],
    "maintenance_records": [
        dict(
            maintenance_id="M1",
            truck_id="A",
            maintenance_date="2024-01-03",
            total_cost=100,
            downtime_hours=24,
        ),
        dict(
            maintenance_id="M2",
            truck_id="C",
            maintenance_date="2024-01-04",
            total_cost=300,
            downtime_hours=10,
        ),
        dict(
            maintenance_id="M3",
            truck_id="D",
            maintenance_date="2024-01-06",
            total_cost=200,
            downtime_hours=10,
        ),
    ],
    "truck_utilization_metrics": [
        dict(truck_id="A", month="2024-01-01", utilization_rate=0.5),
        dict(truck_id="B", month="2024-01-01", utilization_rate=0.4),
    ],
}


def _build(con):
    for t in TABLES.values():
        cols = ", ".join(f'"{c}" {dtype}' for c, dtype in t.columns.items())
        con.execute(f'CREATE TABLE "{t.name}" ({cols})')
    for table, rows in ROWS.items():
        for row in rows:
            cols = ", ".join(f'"{c}"' for c in row)
            marks = ", ".join("?" * len(row))
            con.execute(f'INSERT INTO "{table}" ({cols}) VALUES ({marks})', list(row.values()))
    create_views(con)


@pytest.fixture
def con(tmp_path):
    con = duckdb.connect(str(tmp_path / "warehouse.duckdb"))
    _build(con)
    yield con
    con.close()
