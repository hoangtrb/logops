"""`logops` command-line entry point."""

import time

import duckdb
import typer

from logops import config
from logops.data_platform.data_model_doc import write_docs
from logops.data_platform.ingest import IngestError, ingest_table
from logops.data_platform.quality import key_rules, run_quality
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
    run_quality(config.WAREHOUSE_PATH, TABLES.values(), key_rules(TABLES.values()))

    with duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) as con:
        for name in TABLES:
            rows = con.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
            typer.echo(f"  {name:<28} {rows:>10,} rows")
        findings = con.execute(
            "SELECT table_name, rule_id, column_name, severity, violations FROM dq_findings "
            "WHERE violations > 0 ORDER BY severity, violations DESC"
        ).fetchall()
    typer.echo(f"Data quality: {len(findings)} rule(s) with violations (rows flagged, not removed)")
    for table, rule, column, severity, n in findings:
        target = f"{table}.{column}" if column else table
        typer.echo(f"  [{severity:<5}] {rule:<12} {target:<36} {n:>8,} rows")
    typer.echo(f"Built {config.WAREHOUSE_PATH} in {time.perf_counter() - start:.1f} s")


@app.command()
def docs() -> None:
    """Regenerate docs/02-data-model (EN + VI): ER diagram and data dictionary from schema.py."""
    for path in write_docs(TABLES.values(), config.DOCS_DIR):
        typer.echo(f"Wrote {path.relative_to(config.REPO_ROOT)}")
