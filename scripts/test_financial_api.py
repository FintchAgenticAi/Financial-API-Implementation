"""Smoke-test the Financial API. Expects uvicorn on port 8001 and a seeded database."""

from __future__ import annotations

import os
import sys

import httpx

BASE_URL = os.environ.get("FINANCIAL_API_BASE_URL", "http://127.0.0.1:8001")
failures: list[str] = []


def check(name: str, ok: bool, detail: str) -> None:
    """Record one assertion and print the result."""
    status = "PASS" if ok else "FAIL"
    print(f"{status}  {name}  {detail}")
    if not ok:
        failures.append(f"{name}: {detail}")


def main() -> int:
    """Call the Phase 1 endpoints and return 0 when every check passes."""
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        health = client.get("/health")
        check("GET /health", health.status_code == 200, f"status={health.status_code}")

        runs = client.get("/api/v1/gold/runs")
        runs_ok = runs.status_code == 200 and isinstance(runs.json(), list)
        check("GET /api/v1/gold/runs", runs_ok, f"status={runs.status_code}")

        records = client.get("/api/v1/gold/records")
        body = records.json() if records.status_code == 200 else None
        records_ok = records.status_code == 200 and isinstance(body, list)
        check("GET /api/v1/gold/records", records_ok, f"status={records.status_code}")

        one = client.get("/api/v1/gold/records/1")
        check(
            "GET /api/v1/gold/records/1",
            one.status_code in (200, 404),
            f"status={one.status_code}",
        )

        summary = client.get("/api/v1/gold/summary")
        summary_body = summary.json() if summary.status_code == 200 else {}
        summary_ok = summary.status_code == 200 and {
            "run_count",
            "record_count",
            "prediction_count",
        }.issubset(summary_body)
        check("GET /api/v1/gold/summary", summary_ok, f"status={summary.status_code}")

        record_id = body[0]["id"] if isinstance(body, list) and body else None
        if record_id is None:
            check(
                "POST /api/v1/gold/predictions",
                False,
                "no Gold records; run python scripts/seed_gold_financial.py first",
            )
        else:
            created = client.post(
                "/api/v1/gold/predictions",
                json={"gold_record_id": record_id},
            )
            created_body = created.json() if created.status_code == 201 else {}
            created_ok = (
                created.status_code == 201
                and created_body.get("status") == "stub"
                and created_body.get("gold_record_id") == record_id
                and created_body.get("impact_score") == 0.0
            )
            check(
                "POST /api/v1/gold/predictions",
                created_ok,
                f"status={created.status_code} body={created_body}",
            )

    if failures:
        print(f"\n{len(failures)} check(s) failed.")
        return 1
    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
