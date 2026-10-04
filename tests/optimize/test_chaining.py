"""Nearest-truck replay on a hand-computable timeline; distances over the lanes."""

import datetime as dt

import polars as pl

from logops.optimize.chaining import shortest_paths, simulate

T0 = dt.datetime(2024, 1, 1)
DISTANCE = shortest_paths([("A", "B", 100), ("A", "C", 300), ("B", "C", 250)])
SPEED = 50  # mph: B → A takes 2 h, C → A takes 6 h


def timeline(rows):
    return pl.DataFrame(
        [(a, b, T0 + dt.timedelta(hours=p), T0 + dt.timedelta(hours=d)) for a, b, p, d in rows],
        schema=["pickup_city", "delivery_city", "pickup_at", "free_at"],
        orient="row",
    )


def test_distances_follow_the_lanes_both_ways_and_take_the_shortest_path():
    d = shortest_paths([("A", "B", 100), ("B", "C", 50), ("A", "C", 400)])
    assert d["C", "A"] == 150 and d["A", "C"] == 150 and d["B", "B"] == 0


def test_nearest_rule_sends_the_closest_free_truck():
    loads = timeline(
        [
            ("A", "C", 0, 2),  # truck 0 ends in C, free at 2 h (idle longest)
            ("A", "B", 1, 5),  # truck 0 busy: truck 1, ends in B, free at 5 h
            ("A", "A", 20, 30),  # both can reach A in time
        ]
    )
    today = simulate(loads, DISTANCE, SPEED, nearest=False)
    near = simulate(loads, DISTANCE, SPEED, nearest=True)
    assert (today["empty_miles"], near["empty_miles"]) == (300, 100)
    assert today["moved"] == near["moved"] == 1
    assert today["trucks"] == near["trucks"] == 2


def test_a_truck_that_cannot_arrive_in_time_is_not_used():
    loads = timeline([("A", "C", 0, 2), ("A", "B", 1, 5), ("A", "A", 6, 9)])
    # B is 2 h away but free only at 5 h; C is 6 h away, free at 2 h: neither is in A by 6 h
    assert simulate(loads, DISTANCE, SPEED, nearest=True)["trucks"] == 3
