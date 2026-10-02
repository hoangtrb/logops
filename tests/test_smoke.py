from typer.testing import CliRunner

from logops import config
from logops.cli import app


def test_cli_lists_build_command():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "build" in result.output


def test_paths_resolve_from_repo_root():
    assert (config.REPO_ROOT / "pyproject.toml").is_file()
    assert config.DATASET_DIR == config.REPO_ROOT / "dataset"
    assert config.DATA_DIR == config.REPO_ROOT / "data"
    assert config.PARQUET_DIR == config.DATA_DIR / "parquet"
    assert config.WAREHOUSE_PATH == config.DATA_DIR / "warehouse.duckdb"
