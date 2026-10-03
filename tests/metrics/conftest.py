"""A tiny warehouse whose KPIs can be computed by hand.

Jan 2024: trips tr1 (truck T1, driver D1) and tr2 (truck T2, no driver), fuel spend $250 for 50
gallons burned → $5 per burned gallon. Maintenance: T1 $55 (allocated to tr1), T9 $40 (T9 never
runs a trip → Unattributed). Incident on tr2: $70, preventable.
Feb 2024: trip tr3 (T1, D1), fuel spend $100 for 25 gallons burned → $4 per burned gallon.
Mar 2024: fuel spend $30 with no trips that month → Unattributed.
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
            origin_state="GA",
            destination_city="Chicago",
            destination_state="IL",
            typical_distance_miles=100,
        )
    ],
    "customers": [
        dict(customer_id="C1", customer_type="Contract"),
        dict(customer_id="C2", customer_type="Spot"),
    ],
    "trucks": [
        dict(truck_id="T1", status="Active", model_year=2020),
        dict(truck_id="T2", status="Active", model_year=2021),
        dict(truck_id="T9", status="Inactive", model_year=2015),
    ],
    "loads": [
        dict(
            load_id="L1",
            customer_id="C1",
            route_id="R1",
            revenue=300,
            fuel_surcharge=20,
            accessorial_charges=0,
        ),
        dict(
            load_id="L2",
            customer_id="C2",
            route_id="R1",
            revenue=200,
            fuel_surcharge=10,
            accessorial_charges=0,
        ),
        dict(
            load_id="L3",
            customer_id="C1",
            route_id="R1",
            revenue=250,
            fuel_surcharge=0,
            accessorial_charges=50,
        ),
    ],
    "trips": [
        dict(
            trip_id="tr1",
            load_id="L1",
            driver_id="D1",
            truck_id="T1",
            dispatch_date="2024-01-10",
            actual_distance_miles=110,
            fuel_gallons_used=20,
        ),
        dict(
            trip_id="tr2",
            load_id="L2",
            driver_id=None,
            truck_id="T2",
            dispatch_date="2024-01-20",
            actual_distance_miles=100,
            fuel_gallons_used=30,
        ),
        dict(
            trip_id="tr3",
            load_id="L3",
            driver_id="D1",
            truck_id="T1",
            dispatch_date="2024-02-05",
            actual_distance_miles=100,
            fuel_gallons_used=25,
        ),
    ],
    "fuel_purchases": [
        dict(
            fuel_purchase_id="F1",
            trip_id="tr1",
            truck_id="T1",
            purchase_date="2024-01-10",
            gallons=30,
            total_cost=120,
        ),
        dict(
            fuel_purchase_id="F2",
            trip_id="tr2",
            truck_id="T2",
            purchase_date="2024-01-20",
            gallons=30,
            total_cost=130,
        ),
        dict(
            fuel_purchase_id="F3",
            trip_id="tr3",
            truck_id="T1",
            purchase_date="2024-02-05",
            gallons=25,
            total_cost=100,
        ),
        dict(
            fuel_purchase_id="F4",
            trip_id="tr3",
            truck_id="T1",
            purchase_date="2024-03-01",
            gallons=6,
            total_cost=30,
        ),
    ],
    "maintenance_records": [
        dict(
            maintenance_id="M1",
            truck_id="T1",
            maintenance_date="2024-01-15",
            total_cost=55,
            downtime_hours=5,
        ),
        dict(
            maintenance_id="M9",
            truck_id="T9",
            maintenance_date="2024-01-25",
            total_cost=40,
            downtime_hours=8,
        ),
    ],
    "safety_incidents": [
        dict(incident_id="I1", trip_id="tr2", claim_amount=70, preventable_flag=True)
    ],
    "truck_utilization_metrics": [
        dict(truck_id="T1", month="2024-01-01", utilization_rate=0.8),
        dict(truck_id="T2", month="2024-01-01", utilization_rate=0.6),
        dict(truck_id="T1", month="2024-02-01", utilization_rate=0.7),
    ],
    # deviation: tr1 delivery +90 min, tr2 +150 min, tr3 -30 min
    "delivery_events": [
        dict(
            event_id="E1",
            trip_id="tr1",
            load_id="L1",
            event_type="Pickup",
            scheduled_datetime="2024-01-10 08:00",
            actual_datetime="2024-01-10 08:00",
            detention_minutes=30,
            location_city="Atlanta",
        ),
        dict(
            event_id="E2",
            trip_id="tr1",
            load_id="L1",
            event_type="Delivery",
            scheduled_datetime="2024-01-11 08:00",
            actual_datetime="2024-01-11 09:30",
            detention_minutes=0,
            location_city="Chicago",
        ),
        dict(
            event_id="E3",
            trip_id="tr2",
            load_id="L2",
            event_type="Delivery",
            scheduled_datetime="2024-01-21 08:00",
            actual_datetime="2024-01-21 10:30",
            detention_minutes=0,
            location_city="Chicago",
        ),
        dict(
            event_id="E4",
            trip_id="tr3",
            load_id="L3",
            event_type="Delivery",
            scheduled_datetime="2024-02-06 08:00",
            actual_datetime="2024-02-06 07:30",
            detention_minutes=60,
            location_city="Chicago",
        ),
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
    """Connection to the tiny warehouse, with the metrics views created."""
    con = duckdb.connect(str(tmp_path / "warehouse.duckdb"))
    _build(con)
    yield con
    con.close()


@pytest.fixture
def warehouse(tmp_path):
    """Path to the tiny warehouse file, closed so other code can open it."""
    path = tmp_path / "warehouse.duckdb"
    with duckdb.connect(str(path)) as con:
        _build(con)
    return path
