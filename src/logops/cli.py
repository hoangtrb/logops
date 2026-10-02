"""`logops` command-line entry point."""

import time

import duckdb
import typer

from logops import config
from logops.data_platform.ingest import IngestError, ingest_table
from logops.data_platform.schema import TABLES
from logops.data_platform.warehouse import load_warehouse

app = typer.Typer(help="Logistics Ops Optimizer: fleet data to cost-saving decisions.")


@app.callback()
def main() -> None:
    """Keep `logops` a command group so subcommands are listed in --help."""


@app.command()
def build() -> None:
    """Rebuild Parquet files, the DuckDB warehouse and the data-quality report from dataset/."""
    start = time.perf_counter()
    try:
        for table in TABLES.values():
            ingest_table(table, config.DATASET_DIR, config.PARQUET_DIR)
    except IngestError as e:
        typer.secho(f"Ingest failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from e
    load_warehouse(TABLES.values(), config.PARQUET_DIR, config.WAREHOUSE_PATH)

    with duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) as con:
        for name in TABLES:
            rows = con.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
            typer.echo(f"  {name:<28} {rows:>10,} rows")
    typer.echo(f"Built {config.WAREHOUSE_PATH} in {time.perf_counter() - start:.1f} s")
