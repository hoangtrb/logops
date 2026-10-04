"""O3 trip chaining: send the nearest free truck to each load, and price the empty miles saved.

Every load of the period is replayed in pickup order with its actual pickup and delivery times.
A truck can take a load if it is free in time to drive empty from where it stands to the pickup
city. Two dispatch rules are compared on the same loads:
- **as today**: the truck idle longest, wherever it is; it comes close to the observed share of
  trips that start in another city, so it stands for today's dispatching;
- **nearest truck**: the free truck closest to the pickup city (a truck already there first).
When no truck qualifies, one more truck is added in the pickup city.

No fixed limit on the empty drive: a third of loads end in cities that send little back, so trucks
there must drive far, and any limit up to 24 h needs thousands of extra trucks in the replay. The
nearest-truck rule already keeps every move as short as the free trucks allow; the share of moves
within one driving day is reported.

Everything comes from the data, nothing from outside:
- distance between two cities = the lanes' typical distance; for cities with no lane between them,
  the shortest path over the lanes (longer than the real road);
- driving speed and fuel economy = miles ÷ hours and miles ÷ gallons over all trips;
- cost of an empty mile = fuel-card price per gallon ÷ miles per gallon.

Money: the replay's empty miles are far above what the fuel data allows (gallons bought but not
burned on trips cover about a third of them), so only the replay's **relative** cut in empty miles
is used, applied to the miles that fuel covers: saving = cut × (gallons bought − burned) × price.
That is a maximum: it assumes the extra fuel is all spent driving empty.

The data's own truck assignment can't be the baseline: in 54% of a truck's consecutive trips the
next pickup comes before the last delivery (a synthetic-data artefact).
"""

import datetime as dt
import heapq
from itertools import count

import duckdb
import polars as pl

from logops.analysis.operations import repositioning

DRIVING_DAY_HOURS = 11  # a move within one driving day, for the report on move lengths


def load_timeline(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> pl.DataFrame:
    """One row per load: pickup city and time, delivery city and time (never before pickup)."""
    return con.execute(
        """
        SELECT t.load_id, t.truck_id, r.origin_city AS pickup_city,
               r.destination_city AS delivery_city, p.actual_datetime AS pickup_at,
               greatest(d.actual_datetime,
                        p.actual_datetime + to_microseconds(
                            CAST(t.actual_duration_hours * 3600e6 AS BIGINT))) AS free_at
        FROM trips t
        JOIN loads l ON l.load_id = t.load_id
        JOIN routes r ON r.route_id = l.route_id
        JOIN delivery_events p ON p.trip_id = t.trip_id AND p.event_type = 'Pickup'
        JOIN delivery_events d ON d.trip_id = t.trip_id AND d.event_type = 'Delivery'
        WHERE t.dispatch_date BETWEEN ? AND ?
        ORDER BY pickup_at, t.load_id
        """,
        [start, end],
    ).pl()


def city_distances(con: duckdb.DuckDBPyConnection) -> dict[tuple[str, str], float]:
    """Miles between every two cities: lane distance, else the shortest path over the lanes."""
    lanes = con.execute(
        "SELECT origin_city, destination_city, typical_distance_miles FROM routes"
    ).fetchall()
    return shortest_paths(lanes)


def shortest_paths(lanes: list[tuple[str, str, float]]) -> dict[tuple[str, str], float]:
    cities = sorted({a for a, _, _ in lanes} | {b for _, b, _ in lanes})
    far = float("inf")
    d = {(a, b): 0.0 if a == b else far for a in cities for b in cities}
    for a, b, miles in lanes:  # a road is as long both ways
        d[a, b] = d[b, a] = min(d[a, b], float(miles))
    for k in cities:  # Floyd–Warshall: 20 cities
        for i in cities:
            for j in cities:
                if d[i, k] + d[k, j] < d[i, j]:
                    d[i, j] = d[i, k] + d[k, j]
    return d


def move_costs(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    """Driving speed, fuel economy and prices, all from the data."""
    speed, mpg = con.execute(
        "SELECT sum(actual_distance_miles) / sum(actual_duration_hours), "
        "sum(actual_distance_miles) / sum(fuel_gallons_used) FROM trips "
        "WHERE dispatch_date BETWEEN ? AND ?",
        [start, end],
    ).fetchone()
    price = con.execute(
        "SELECT sum(total_cost) / sum(gallons) FROM fuel_purchases "
        "WHERE purchase_date BETWEEN ? AND ?",
        [start, end],
    ).fetchone()[0]
    years = (end - start).days / 365.25
    bought = con.execute(
        "SELECT sum(gallons) FROM fuel_purchases WHERE purchase_date BETWEEN ? AND ?", [start, end]
    ).fetchone()[0]
    burned = con.execute(
        "SELECT sum(fuel_gallons_used) FROM trips WHERE dispatch_date BETWEEN ? AND ?", [start, end]
    ).fetchone()[0]
    off_trip = max(0.0, bought - burned) / years  # gallons a year not burned on any trip
    return {
        "speed_mph": speed,
        "mpg": mpg,
        "fuel_price": price,
        "cost_per_mile": price / mpg,
        "off_trip_miles_per_year": off_trip * mpg,
        "off_trip_fuel_per_year": off_trip * price,
    }


def simulate(
    timeline: pl.DataFrame,
    distance: dict[tuple[str, str], float],
    speed_mph: float,
    nearest: bool,
) -> dict:
    """Replay the loads with one dispatch rule: loads chained, moves, empty miles, trucks."""
    cities = sorted({a for a, _ in distance})
    by_distance = {a: sorted(cities, key=lambda b: (distance[b, a], b)) for a in cities}
    free: dict[str, list] = {c: [] for c in cities}  # city -> heap of (free_at, seq, truck)
    seq = count()
    chained = moved = trucks = 0
    empty_miles = 0.0
    move_miles: list[float] = []
    for pickup_city, delivery_city, pickup_at, free_at in timeline.select(
        "pickup_city", "delivery_city", "pickup_at", "free_at"
    ).iter_rows():
        best = None  # (rank, city)
        for city in by_distance[pickup_city]:
            heap = free[city]
            if not heap:
                continue
            miles = distance[city, pickup_city]
            hours = miles / speed_mph
            if heap[0][0] + dt.timedelta(hours=hours) > pickup_at:
                continue  # the earliest-free truck there can't make it, so none can
            rank = miles if nearest else heap[0][0].timestamp()
            if best is None or rank < best[0]:
                best = (rank, city)
                if nearest:
                    break  # the first truck in distance order is the nearest
        if best is None:
            truck, trucks = trucks, trucks + 1  # one more truck, starting in the pickup city
        else:
            city = best[1]
            truck = heapq.heappop(free[city])[2]
            if city == pickup_city:
                chained += 1
            else:
                moved += 1
                empty_miles += distance[city, pickup_city]
                move_miles.append(distance[city, pickup_city])
        heapq.heappush(free[delivery_city], (free_at, next(seq), truck))
    return {
        "chained": chained,
        "moved": moved,
        "trucks": trucks,
        "empty_miles": empty_miles,
        "move_miles": move_miles,
        "moved_pct": 100 * moved / (chained + moved) if chained + moved else 0.0,
    }


def chaining(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    """Today's dispatching against the nearest truck: moves, empty miles, trucks, money."""
    timeline = load_timeline(con, start, end)
    distance = city_distances(con)
    costs = move_costs(con, start, end)
    years = (end - start).days / 365.25
    day_miles = DRIVING_DAY_HOURS * costs["speed_mph"]

    def run(nearest: bool) -> dict:
        r = simulate(timeline, distance, costs["speed_mph"], nearest)
        moves = r["move_miles"]
        return {
            "moved_pct": r["moved_pct"],
            "moves_per_year": r["moved"] / years,
            "empty_miles_per_year": r["empty_miles"] / years,
            "miles_per_move": r["empty_miles"] / r["moved"] if r["moved"] else 0.0,
            "within_a_day_pct": 100 * sum(m <= day_miles for m in moves) / len(moves)
            if moves
            else 0.0,
            "trucks": r["trucks"],
        }

    today, nearest = run(nearest=False), run(nearest=True)
    cut = 1 - nearest["empty_miles_per_year"] / today["empty_miles_per_year"]
    seen = repositioning(con, start, end)
    return {
        "loads": timeline.height,
        "observed_moved_pct": seen["moved_pct"],
        "costs": costs,
        "today": today,
        "nearest": nearest,
        "empty_miles_cut": cut,  # share of empty miles the nearest-truck rule avoids
        "model_fuel_saving": (today["empty_miles_per_year"] - nearest["empty_miles_per_year"])
        * costs["cost_per_mile"],
        "saving_per_year": cut * costs["off_trip_fuel_per_year"],
    }
