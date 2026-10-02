"""Project paths. Everything resolves from the repo root, so commands work from any cwd."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = REPO_ROOT / "dataset"  # raw Kaggle CSVs, read-only
DATA_DIR = REPO_ROOT / "data"  # generated, git-ignored
PARQUET_DIR = DATA_DIR / "parquet"
WAREHOUSE_PATH = DATA_DIR / "warehouse.duckdb"
DOCS_DIR = REPO_ROOT / "docs"
