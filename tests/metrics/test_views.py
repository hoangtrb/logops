import pytest


def trip(con, trip_id, column):
    return con.execute(
        f"SELECT {column} FROM trip_economics WHERE trip_id = ?", [trip_id]
    ).fetchone()[0]


def test_fuel_allocated_by_burned_gallons_within_the_month(con):
    # Jan: $250 spend / 50 gallons burned = $5 per gallon
    assert trip(con, "tr1", "fuel_cost") == pytest.approx(100)
    assert trip(con, "tr2", "fuel_cost") == pytest.approx(150)
    # Feb: $100 / 25 gallons = $4 per gallon
    assert trip(con, "tr3", "fuel_cost") == pytest.approx(100)


def test_maintenance_allocated_by_truck_month_miles(con):
    assert trip(con, "tr1", "maintenance_cost") == pytest.approx(55)
    assert trip(con, "tr2", "maintenance_cost") == 0  # T2 had no maintenance
    assert trip(con, "tr3", "maintenance_cost") == 0  # T1 had none in February


def test_revenue_incidents_and_contribution(con):
    assert trip(con, "tr1", "revenue") == 320
    assert trip(con, "tr2", "safety_cost") == 70
    assert trip(con, "tr2", "contribution") == pytest.approx(210 - 150 - 70)
    assert trip(con, "tr3", "gallons_purchased") == 31  # F3 + F4 both name tr3


def test_delivery_deviation_minutes(con):
    rows = dict(con.execute("SELECT event_id, deviation_min FROM delivery_performance").fetchall())
    assert rows == {"E1": 0, "E2": 90, "E3": 150, "E4": -30}


def test_truck_economics_includes_idle_trucks(con):
    rows = {
        r[0]: r[1:]
        for r in con.execute(
            "SELECT truck_id, trips, miles, maintenance_cost, status FROM truck_economics"
        ).fetchall()
    }
    assert rows["T1"] == (2, 210, 55, "Active")
    assert rows["T9"] == (0, 0, 40, "Inactive")  # costs money, never ran a trip
