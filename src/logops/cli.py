"""`logops` command-line entry point."""

import datetime as dt
import subprocess
import sys
import time
from pathlib import Path

import duckdb
import typer

from logops import config
from logops.analysis.bundle import analysis_bundle
from logops.analysis.doc import write_analysis_docs
from logops.data_platform.data_model_doc import write_docs
from logops.data_platform.dq_report import write_report
from logops.data_platform.ingest import IngestError, ingest_table
from logops.data_platform.quality import all_rules, run_quality
from logops.data_platform.schema import TABLES
from logops.data_platform.warehouse import load_warehouse
from logops.metrics.kpi_doc import write_kpi_docs
from logops.metrics.kpis import CATALOG, DIMENSIONS, kpi
from logops.metrics.views import create_views
from logops.optimize.report import collect, recommendations, totals, write_optimize_outputs

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
    try:
        load_warehouse(TABLES.values(), config.PARQUET_DIR, config.WAREHOUSE_PATH)
    except duckdb.IOException as e:
        typer.secho(
            f"Cannot write {config.WAREHOUSE_PATH.name}: another program has it open "
            "(e.g. DBeaver or the DuckDB UI). Disconnect it and run the build again.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1) from e
    run_quality(config.WAREHOUSE_PATH, TABLES.values(), all_rules(TABLES.values()))
    with duckdb.connect(str(config.WAREHOUSE_PATH)) as con:
        create_views(con)
    reports = write_report(config.WAREHOUSE_PATH, TABLES.values(), config.DOCS_DIR)
    reports += write_kpi_docs(config.WAREHOUSE_PATH, config.DOCS_DIR)
    reports += write_analysis_docs(config.WAREHOUSE_PATH, config.DOCS_DIR)
    reports += write_optimize_outputs(config.WAREHOUSE_PATH, config.DOCS_DIR)

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
    for path in reports:
        typer.echo(f"Wrote {path.name}")
    typer.echo(f"Built {config.WAREHOUSE_PATH} in {time.perf_counter() - start:.1f} s")


@app.command()
def docs() -> None:
    """Regenerate docs/02-data-model (EN + VI): ER diagram and data dictionary from schema.py."""
    for path in write_docs(TABLES.values(), config.DOCS_DIR):
        typer.echo(f"Wrote {path.relative_to(config.REPO_ROOT)}")


DEFAULT_KPIS = "revenue,cost_per_mile,contribution_margin_pct,mpg,on_time_pct,avg_detention_min"


@app.command(name="kpi")
def kpi_command(
    by: str = typer.Option(None, help=f"Group by: {', '.join(DIMENSIONS)}"),
    date_from: str = typer.Option("2022-01-01", "--from", help="First dispatch date (YYYY-MM-DD)"),
    date_to: str = typer.Option("2025-12-31", "--to", help="Last dispatch date (YYYY-MM-DD)"),
    window: float = typer.Option(120, help="On-time window in minutes (120 = on_time_flag)"),
    kpis: str = typer.Option(DEFAULT_KPIS, help="Comma-separated KPI names, or 'all'"),
) -> None:
    """Print KPIs for the fleet, or per group, from the warehouse built by `logops build`."""
    names = [k.name for k in CATALOG] if kpis == "all" else kpis.split(",")
    unknown = set(names) - {k.name for k in CATALOG}
    if unknown or (by is not None and by not in DIMENSIONS):
        typer.secho(
            f"Unknown KPI(s) {sorted(unknown)} or --by {by!r}. "
            f"KPIs: {', '.join(k.name for k in CATALOG)}. --by: {', '.join(DIMENSIONS)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    with duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) as con:
        table = kpi(
            con,
            dt.date.fromisoformat(date_from),
            dt.date.fromisoformat(date_to),
            by=by,
            on_time_window_min=window,
        )
    shown = table.select(["group", *names])
    header = f"{'group':<28}" + "".join(f"{n[:22]:>24}" for n in names)
    typer.echo(header)
    for row in shown.iter_rows():
        cells = "".join(f"{'—' if v is None else f'{v:,.2f}':>24}" for v in row[1:])
        typer.echo(f"{str(row[0])[:28]:<28}{cells}")


@app.command()
def insights(
    date_from: str = typer.Option("2022-01-01", "--from", help="First date (YYYY-MM-DD)"),
    date_to: str = typer.Option("2024-12-31", "--to", help="Last date (YYYY-MM-DD)"),
    lang: str = typer.Option("vi", help="Language: vi or en"),
) -> None:
    """Print the rule-based commentary for the period."""
    with duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) as con:
        bundle = analysis_bundle(
            con, dt.date.fromisoformat(date_from), dt.date.fromisoformat(date_to)
        )
    for item in bundle["insights"][lang]:
        typer.echo(f"[{item['level_label']} · {item['tone_label']}] {item['text']}")
        typer.echo("")


@app.command()
def optimize(
    growth: float = typer.Option(0, help="Volume growth scenario in percent, e.g. 10"),
) -> None:
    """Print the recommendations and how they compare with the savings target."""
    with duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) as con:
        data = collect(con, growth=growth / 100)
    t = totals(data)
    typer.echo(f"Savings target:      ${t['target']:>12,.0f} per year (3% of measured cost)")
    typer.echo(f"Measured savings:    ${t['measured']:>12,.0f} ({t['measured'] / t['target']:.0%})")
    typer.echo(f"Upper bound (price): ${t['upper']:>12,.0f} (needs customers to accept)")
    typer.echo("")
    for r in recommendations(data).iter_rows(named=True):
        impact = f"${r['annual_impact_usd']:>11,.0f}" if r["annual_impact_usd"] else " " * 12
        what = r["item"] if r["impact_type"] == "no signal" else r["action"]
        typer.echo(f"  [{r['impact_type']:<12}] {impact}  {r['area']:<8} {what}")


@app.command()
def report(
    date_from: str = typer.Option("2022-01-01", "--from", help="First date (YYYY-MM-DD)"),
    date_to: str = typer.Option("2024-12-31", "--to", help="Last date (YYYY-MM-DD)"),
    lang: str = typer.Option("vi", help="Language: vi or en"),
    fmt: str = typer.Option("html", "--format", help="html or pdf"),
) -> None:
    """Write the report (every dashboard page) to reports/output/: HTML, or PDF via Edge/Chrome."""
    import logging

    from logops.reports import NoBrowserError, build_html, file_name, to_pdf  # loads Streamlit

    for name in list(logging.root.manager.loggerDict):  # cached loaders run outside the app
        if name.startswith("streamlit"):
            logging.getLogger(name).setLevel(logging.ERROR)
    start, end = dt.date.fromisoformat(date_from), dt.date.fromisoformat(date_to)
    html = build_html(start, end, lang, for_print=fmt == "pdf")
    out_dir = config.REPO_ROOT / "reports" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / file_name(lang, start, end, fmt)
    if fmt == "pdf":
        try:
            path.write_bytes(to_pdf(html))
        except NoBrowserError as e:
            raise typer.Exit(f"{e}; use --format html") from e
    else:
        path.write_text(html, encoding="utf-8")
    typer.echo(f"Wrote {path}")


@app.command()
def dashboard(port: int = typer.Option(8501, help="Port for the local web server")) -> None:
    """Open the dashboard in the browser (http://localhost:PORT). Ctrl+C to stop."""
    app_path = Path(__file__).parent / "dashboard" / "app.py"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(port),
            "--server.headless",
            "false",
        ],
        cwd=config.REPO_ROOT,
        check=False,
    )
