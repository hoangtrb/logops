# Implementation Plan: data-platform

> Module 1 of 6 · Spec: [SPEC-data-platform.md](../SPEC-data-platform.md) · Vietnamese: [plan.vi.md](plan.vi.md)
> Task checklist: [todo.md](todo.md) (the English file is the source of truth for checkboxes)

## Overview

Build `uv run logops build`, one idempotent command that turns the 14 Kaggle CSVs into typed
Parquet files, a DuckDB warehouse and a bilingual data-quality report with business baselines.
The tasks are vertical slices: the first slice takes **one table** through the whole pipeline
(CSV → Parquet → DuckDB → CLI → test). After that, each task widens either the set of tables
or the set of rules.

## Architecture Decisions

- **DuckDB does the heavy lifting.** It reads CSVs with an explicit schema, writes Parquet and
  serves the warehouse, so there is no pandas in the hot path. This is fast and shows a
  scalable pattern.
- **Schema as data.** `schema.py` holds one dict per table (column → DuckDB type, PK, FKs).
  Ingest, FK rules and tests all read from it, so there is a single source of truth.
- **Rules as data.** Each DQ rule is `Rule(table, id, severity, sql_predicate)`. The engine
  writes violations to a `dq_issues` list column and to a `dq_findings` table. Rows are never
  deleted (only exact duplicates are removed, and those are logged).
- **Report = template + findings table.** One renderer, two label dictionaries (EN/VI), two
  files. The numbers are never hand-typed.
- **Fixtures over mocks.** Tiny CSVs with known defects in `tests/fixtures/`. Tests run the
  real pipeline against them.

## Dependency Graph

```
T1 scaffold
  └─ T2 one-table slice (schema → ingest → warehouse → CLI)
       └─ T3 all 14 tables
            ├─ T4 DQ engine + key rules ─ T5 value rules ─ T6 agg_drift
            │                                         └─ T7 report EN/VI + baselines
            └─ T8 dedup, --skip-dq, idempotency, perf
                                                     └─ T9 data-understanding docs EN/VI
```

## Task List

### Phase 1: Foundation
- [x] T1: Project scaffold (uv, package, CLI stub, pytest, ruff) · S
- [x] T2: One-table vertical slice: `routes` end to end · M
- [x] T3: Extend schema & ingest to all 14 tables · M

### Checkpoint A: Warehouse builds
- [ ] `logops build` creates `data/warehouse.duckdb` with 14 tables; row counts match CSVs
- [ ] Tests and ruff green · human review

### Phase 2: Data quality
- [ ] T4: DQ engine + key rules (`pk_unique`, `fk_missing`, `fk_orphan`) · M
- [ ] T5: Value rules (`range`, `amount_mismatch`, `time_order`, `geo_mismatch`) · M
- [ ] T6: `agg_drift` rule (monthly metrics vs recomputed from trips) · S

### Checkpoint B: Findings correct
- [ ] Every rule has a passing fixture test; findings on the real data look plausible
- [ ] Human review of the false-positive rate (especially `geo_mismatch`)

### Phase 3: Report & hardening
- [ ] T7: DQ report generator, EN + VI, with business baselines · M
- [ ] T8: Dedup logging, `--skip-dq`, idempotency, < 30 s performance · S
- [ ] T9: Hand-written `02-data-understanding` (EN + VI) · S

### Checkpoint C: Module complete
- [ ] All spec success criteria met · ready for `metrics` spec

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Typed CSV read fails (microsecond timestamps, empty strings, "True"/"False") | High | T2 proves the pattern on one table first; T3 adds a test per table |
| `geo_mismatch` has no reliable city→state reference, so it produces a flood of false positives | Med | Severity `warn`; reference = city/state pairs seen in facilities + routes; review at Checkpoint B; drop the rule if it's noise |
| `agg_drift` month definition is ambiguous (dispatch vs delivery date) | Med | Try dispatch month; report the drift distribution instead of a hard fail |
| `uv` not on PATH on Windows | Low | Use `python -m uv`, or add the user Scripts dir to PATH |
| Scope creep into KPI views | Med | KPI views belong to the `metrics` module; this module stops at clean tables + DQ |

## Open Questions

None. All decisions are recorded in the spec.
