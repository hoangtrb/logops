import re
import string

import polars as pl

from logops.analysis.insights import RULES, THRESHOLDS, generate
from logops.analysis.operations import MATRIX_ACTIONS, _thirds

FACTS = {
    "year_first": "2022",
    "year_last": "2024",
    "margin_first": 60.0,
    "margin_last": 65.0,
    "trips_first": 1000,
    "trips_last": 1005,
    "trips_change_pct": 0.5,
    "rpm_first": 2.0,
    "rpm_last": 2.01,
    "rpm_change_pct": 0.5,
    "bridge_delta": 100.0,
    "bridge_fuel": 80.0,
    "bridge_fuel_share": 0.8,
    "margin_fuel_corr": -0.9,
    "segment_margin_min": 65.0,
    "segment_margin_max": 65.5,
    "segment_margin_spread": 0.5,
    "top_state": "TX",
    "top_state_contribution": 10.0,
    "top_state_share": 12.0,
    "state_margin_min": 55.0,
    "state_margin_max": 70.0,
    "largest_customer_pct": 0.6,
    "top10_pct": 5.0,
    "customers_for_80pct": 150,
    "customers": 200,
    "hhi": 50.0,
    "fuel_ratio_min": 1.28,
    "fuel_ratio_max": 1.3,
    "cap_p95": 73.0,
    "cap_p99": 75.0,
    "cap_max": 80,
    "trucks_in_use": 92,
    "trucks_owned": 120,
    "lag1": 0.18,
    "quarter_persistence": 0.04,
    "yearly_mean_min": 66.0,
    "yearly_mean_max": 66.2,
    "lanes_protect": 7,
    "lanes_reprice": 6,
    "lanes_exit": 6,
    "surplus_pct": 33.0,
    "surplus": 28178,
    "cities_imbalanced": 16,
    "cities": 20,
    "balance_persistence": 0.997,
    "receive_only_cities": ["Los Angeles"],
    "moved_pct": 95.4,
}


def test_templates_contain_no_digits():
    for rule in RULES:
        for lang, text in rule.templates.items():
            literal = "".join(part for part, *_ in string.Formatter().parse(text))
            assert not re.search(r"\d", literal), (rule.id, lang, literal)


def test_every_rule_fires_on_the_sample_facts_in_both_languages():
    for lang in ("en", "vi"):
        ids = [i["id"] for i in generate(FACTS, lang)]
        assert ids == [r.id for r in RULES], lang


def test_numbers_come_from_the_facts():
    text = {i["id"]: i["text"] for i in generate(FACTS, "en")}
    assert "28,178" in text["imbalance"] and "Los Angeles" in text["imbalance"]
    assert "92 trucks in use and 120 owned" in text["capacity"]


def test_concentration_level_follows_thresholds():
    level = {r.id: r for r in RULES}["concentration"].level
    assert level(FACTS) == "info"
    assert level(FACTS | {"hhi": 1200.0}) == "watch"
    assert level(FACTS | {"largest_customer_pct": 12.0}) == "act"


def test_rules_skip_when_their_condition_is_false():
    ids = [i["id"] for i in generate(FACTS | {"trips_change_pct": 8.0, "moved_pct": 10.0}, "en")]
    assert "volume_flat" not in ids and "repositioning" not in ids


def test_every_threshold_has_reason_and_source():
    for name, (value, reason, source) in THRESHOLDS.items():
        assert value is not None and reason and source, name


def test_thirds_and_matrix_cover_every_cell():
    tiers = _thirds(pl.Series([5, 1, 9, 3, 7, 2, 8, 4, 6]))
    assert sorted(tiers.to_list()) == [1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert set(MATRIX_ACTIONS) == {(v, m) for v in (1, 2, 3) for m in (1, 2, 3)}
