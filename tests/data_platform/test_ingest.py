import shutil

import duckdb
import pytest
from typer.testing import CliRunner

from logops import cli, config
from logops.data_platform.ingest import IngestError, ingest_table
from logops.data_platform.schema import TABLES
from logops.data_platform.warehouse import load_warehouse

ROUTES = TABLES["routes"]


@pytest.fixture
def csv_dir(tmp_path, fixtures_dir):
    d = tmp_path / "dataset"
    d.mkdir()
    shutil.copy(fixtures_dir / "routes.csv", d / "routes.csv")
    return d


def test_routes_csv_to_typed_parquet_and_warehouse(csv_dir, tmp_path):
    parquet = ingest_table(ROUTES, csv_dir, tmp_path / "parquet")
    db_path = tmp_path / "warehouse.duckdb"
    load_warehouse([ROUTES], tmp_path / "parquet", db_path)

    assert parquet == tmp_path / "parquet" / "routes.parquet"
    with duckdb.connect(str(db_path), read_only=True) as con:
        types = dict(
            con.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'routes' ORDER BY ordinal_position"
            ).fetchall()
        )
        rows = con.execute("SELECT count(*) FROM routes").fetchone()[0]
        missing_miles = con.execute(
            "SELECT typical_distance_miles FROM routes WHERE route_id = 'RTE00004'"
        ).fetchone()[0]

    assert list(types.items()) == list(ROUTES.columns.items())
    assert rows == 4
    assert missing_miles is None  # empty field -> NULL, not 0 and not a VARCHAR fallback


def test_type_mismatch_names_table_and_column(csv_dir, tmp_path):
    text = (csv_dir / "routes.csv").read_text().replace(",697,", ",about 700,")
    (csv_dir / "routes.csv").write_text(text)

    with pytest.raises(IngestError, match=r"routes\.typical_distance_miles.*about 700"):
        ingest_table(ROUTES, csv_dir, tmp_path / "parquet")


def test_header_mismatch_is_rejected(csv_dir, tmp_path):
    text = (csv_dir / "routes.csv").read_text().replace("base_rate_per_mile", "rate")
    (csv_dir / "routes.csv").write_text(text)

    with pytest.raises(IngestError, match=r"routes.*header"):
        ingest_table(ROUTES, csv_dir, tmp_path / "parquet")


def test_rebuild_replaces_tables(csv_dir, tmp_path):
    db_path = tmp_path / "warehouse.duckdb"
    for _ in range(2):
        ingest_table(ROUTES, csv_dir, tmp_path / "parquet")
        load_warehouse([ROUTES], tmp_path / "parquet", db_path)

    with duckdb.connect(str(db_path), read_only=True) as con:
        assert con.execute("SELECT count(*) FROM routes").fetchone()[0] == 4


def test_cli_build_writes_warehouse(csv_dir, tmp_path, monkeypatch):
    # The DQ report, KPI views and KPI docs need all 14 tables; this fixture has only routes.
    monkeypatch.setattr(cli, "write_report", lambda *_: [])
    monkeypatch.setattr(cli, "create_views", lambda *_: None)
    monkeypatch.setattr(cli, "write_kpi_docs", lambda *_: [])
    monkeypatch.setattr(cli, "write_analysis_docs", lambda *_: [])
    monkeypatch.setattr(cli, "TABLES", {"routes": ROUTES})  # fixture dir holds only routes.csv
    monkeypatch.setattr(config, "DATASET_DIR", csv_dir)
    monkeypatch.setattr(config, "PARQUET_DIR", tmp_path / "parquet")
    monkeypatch.setattr(config, "WAREHOUSE_PATH", tmp_path / "warehouse.duckdb")

    result = CliRunner().invoke(cli.app, ["build"])

    assert result.exit_code == 0, result.output
    assert "routes" in result.output
    assert (tmp_path / "warehouse.duckdb").is_file()


def test_cli_build_fails_loudly_on_missing_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATASET_DIR", tmp_path / "nowhere")
    monkeypatch.setattr(config, "PARQUET_DIR", tmp_path / "parquet")
    monkeypatch.setattr(config, "WAREHOUSE_PATH", tmp_path / "warehouse.duckdb")

    result = CliRunner().invoke(cli.app, ["build"])

    assert result.exit_code == 1
    assert "file not found" in result.output


def test_cli_build_explains_a_locked_warehouse(csv_dir, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "TABLES", {"routes": ROUTES})
    monkeypatch.setattr(config, "DATASET_DIR", csv_dir)
    monkeypatch.setattr(config, "PARQUET_DIR", tmp_path / "parquet")
    monkeypatch.setattr(config, "WAREHOUSE_PATH", tmp_path / "warehouse.duckdb")

    def locked(*_):
        raise duckdb.IOException("Cannot open file: used by another process")

    monkeypatch.setattr(cli, "load_warehouse", locked)
    result = CliRunner().invoke(cli.app, ["build"])

    assert result.exit_code == 1
    assert "another program has it open" in result.output
