import datetime as dt

from typer.testing import CliRunner

from logops import cli, config
from logops.metrics.kpi_doc import LANGUAGES, fleet_values, render
from logops.metrics.kpis import CATALOG, TITLES


def test_kpi_command_prints_groups_and_fleet(warehouse, monkeypatch):
    monkeypatch.setattr(config, "WAREHOUSE_PATH", warehouse)
    result = CliRunner().invoke(
        cli.app, ["kpi", "--by", "driver", "--from", "2024-01-01", "--to", "2024-12-31"]
    )
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0].split()[:3] == ["group", "revenue", "cost_per_mile"]
    assert [ln.split()[0] for ln in lines[1:]] == ["D1", "Unattributed", "Fleet"]
    assert "830.00" in lines[-1]


def test_kpi_command_rejects_unknown_names(warehouse, monkeypatch):
    monkeypatch.setattr(config, "WAREHOUSE_PATH", warehouse)
    result = CliRunner().invoke(cli.app, ["kpi", "--kpis", "profit"])
    assert result.exit_code == 1
    assert "Unknown KPI" in result.output


def test_kpi_doc_lists_every_kpi_in_both_languages(con):
    start, end = dt.date(2024, 1, 1), dt.date(2024, 12, 31)
    values = fleet_values(con, start, end)
    for lang in LANGUAGES:
        text = render(values, start, end, lang)
        for k in CATALOG:
            assert f"{TITLES[k.name][lang]} (`{k.name}`) |" in text, (lang, k.name)
        assert render(values, start, end, lang) == text  # deterministic
    assert "| 830.0 |" in render(values, start, end, "en")
    assert "| 830,0 |" in render(values, start, end, "vi")
