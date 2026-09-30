# Financial API (Gold)

Phase 1 read API for curated Gold financial records, plus a stub prediction write. This process is separate from the Transformation service (`main.py`, port 8000). It uses the same PostgreSQL server and its own tables: `gold_pipeline_runs`, `gold_financial_records`, and `predictions`.

The Data Pumper is not required yet. `scripts/seed_gold_financial.py` fills the Gold tables for local use.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a database, then point the app at it. `GOLD_DATABASE_URL` wins when both are set. A URL that starts with `postgresql://` is loaded with the psycopg driver.

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/financial
ENABLE_DEV_INGEST=false
PREDICTION_SERVICE_URL=http://localhost:8002
```

`ENABLE_DEV_INGEST=true` mounts `POST /internal/dev/ingest-run`, which inserts one pipeline run and its records.

## How to run

Terminal 1 — Transformation service (Silver), when `main.py` is in this repo:

```bash
uvicorn main:app --reload
```

Terminal 2 — Financial API (Gold):

```bash
uvicorn financial_main:app --reload --port 8001
```

Seed Gold rows (safe to re-run; it skips when any pipeline run already exists):

```bash
python scripts/seed_gold_financial.py
```

Smoke test against port 8001:

```bash
python scripts/test_financial_api.py
```

OpenAPI: http://127.0.0.1:8001/docs

## Phase 1 endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/api/v1/gold/runs` | List pipeline runs |
| GET | `/api/v1/gold/records` | List records (`entity_type`, `skip`, `limit`) |
| GET | `/api/v1/gold/records/{id}` | One record (404 when missing) |
| GET | `/api/v1/gold/summary` | Counts of runs, records, and predictions |
| GET | `/api/v1/gold/predictions` | List predictions (`gold_record_id` optional) |
| POST | `/api/v1/gold/predictions` | Stub prediction (`status=stub`, `impact_score=0.0`) |

`POST /api/v1/gold/predictions` checks that the Gold record exists, then stores a stub. The external model call is Phase 2 (`financial_api/prediction_client.py`).
