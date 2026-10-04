import datetime as dt

from logops.data_platform.dq_report import LANGUAGES, render

DATA = {
    "rows": {"trips": 1000, "drivers": 10},
    "flagged": {"trips": 25, "drivers": 0},
    "flagged_error": {"trips": 25, "drivers": 0},
    "findings": [
        ("trips", "idle_exceeds_duration", None, "error", 25, ["T1", "T2", "T3"]),
        ("drivers", "pk_unique", None, "error", 0, []),
        ("trips", "range", None, "warn", 1, ["D1|2022-01-01"]),
    ],
    "nulls": [("trips", "driver_id", 20, 1000)],
    "baselines": {
        "period_start": (dt.date(2022, 1, 1), "date"),
        "period_end": (dt.date(2024, 12, 31), "date"),
        "revenue": (298_600_000.0, "usd_m"),
        "fuel_cost": (95_590_000.0, "usd_m"),
        "maintenance_cost": (5_730_000.0, "usd_m"),
        "safety_cost": (1_000_000.0, "usd_m"),
        "operating_cost": (102_320_000.0, "usd_m"),
        "miles": (122_200_000, "int"),
        "cost_per_mile": (0.8373, "usd"),
        "fleet_mpg": (6.5, "num2"),
        "delivery_in_window": (0.446, "pct"),
        "pickup_in_window": (0.667, "pct"),
        "delivery_not_late": (0.333, "pct"),
        "detention_hours": (12345.6, "int"),
        "utilization": (0.71, "pct"),
    },
    "checks": {
        "dup_rows": (0, "int"),
        "driver_monthly_drift": (0.0, "pct"),
        "truck_monthly_drift": (0.0, "pct"),
        "on_time_flag_is_2h_window": (1.0, "pct"),
        "early_over_2h_not_on_time": (0.055, "pct"),
        "event_city_is_route_endpoint": (1.0, "pct"),
        "facility_city_is_route_endpoint": (0.034, "pct"),
    },
}


def test_report_shows_violations_samples_and_clean_rules():
    text = render(DATA, "en")

    assert "| error | `idle_exceeds_duration` | `trips` | 25 | 2.5% | `T1`, `T2`, `T3` |" in text
    assert "- `drivers`: `pk_unique`" in text  # rule that ran and found nothing
    assert "| `trips.driver_id` | 20 | 2.0% |" in text
    assert "| 2022-01-01 to 2024-12-31 |" in text
    assert r"`D1\|2022-01-01`" in text  # pipe in a composite key is escaped
    assert r"(\|actual − scheduled\| ≤ 120 min)" in text


def test_same_numbers_in_both_languages_with_local_formatting():
    en, vi = render(DATA, "en"), render(DATA, "vi")

    assert "$298.60M" in en and "298,60 tr USD" in vi
    assert "| 122,200,000 |" in en and "| 122.200.000 |" in vi
    assert "44.6%" in en and "44,6%" in vi


def test_render_is_deterministic():
    for lang in LANGUAGES:
        assert render(DATA, lang) == render(DATA, lang)
