"""Insert sample Gold runs, records, and predictions. Skips when any run already exists."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import func, select

from config.database import Base, SessionLocal, engine
from models.financial_gold import GoldFinancialRecord, GoldPipelineRun, Prediction


COMPANIES = [
    ("acme", "Acme Corp", "ACME", "Industrials"),
    ("northwind", "Northwind Trading", "NWND", "Retail"),
    ("helix", "Helix Bio", "HLXB", "Healthcare"),
    ("lumen", "Lumen Grid", "LMNG", "Utilities"),
    ("orbit", "Orbit Logistics", "ORBT", "Transportation"),
    ("quartz", "Quartz Bank", "QRTZ", "Financials"),
    ("sable", "Sable Energy", "SABL", "Energy"),
    ("terra", "Terra Foods", "TRRA", "Consumer"),
    ("vertex", "Vertex Software", "VRTX", "Technology"),
    ("willow", "Willow Media", "WLLO", "Communications"),
]

METRICS = [
    ("revenue", "revenue", 1_250_000),
    ("ebitda", "ebitda", 210_000),
    ("net_income", "net_income", 96_000),
    ("operating_cash_flow", "operating_cash_flow", 140_000),
    ("gross_margin", "gross_margin", 0.42),
    ("debt_to_equity", "debt_to_equity", 0.8),
    ("eps", "eps", 1.35),
    ("free_cash_flow", "free_cash_flow", 88_000),
    ("current_ratio", "current_ratio", 1.6),
    ("roe", "roe", 0.14),
]


def _runs_exist(db) -> int:
    return db.scalar(select(func.count()).select_from(GoldPipelineRun)) or 0


def seed() -> None:
    """Create two runs, twenty records, and five predictions when the Gold tables are empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = _runs_exist(db)
        if existing:
            print(f"Gold data already exists ({existing} runs). Skipping seed.")
            return

        now = datetime.now(timezone.utc)
        company_run = GoldPipelineRun(
            batch_id="seed-batch-001",
            source_file_id="seed-companies.csv",
            row_count=len(COMPANIES),
            status="completed",
            started_at=now,
            finished_at=now,
            meta={"loader": "seed_gold_financial", "entity_type": "company"},
        )
        metric_run = GoldPipelineRun(
            batch_id="seed-batch-002",
            source_file_id="seed-metrics.csv",
            row_count=len(METRICS),
            status="completed",
            started_at=now,
            finished_at=now,
            meta={"loader": "seed_gold_financial", "entity_type": "metric"},
        )
        db.add_all([company_run, metric_run])
        db.flush()

        company_rows: list[GoldFinancialRecord] = []
        for key, name, ticker, sector in COMPANIES:
            row = GoldFinancialRecord(
                pipeline_run_id=company_run.id,
                entity_type="company",
                entity_key=key,
                payload={"name": name, "ticker": ticker, "sector": sector},
            )
            company_rows.append(row)
        metric_rows = [
            GoldFinancialRecord(
                pipeline_run_id=metric_run.id,
                entity_type="metric",
                entity_key=key,
                payload={"name": name, "value": value, "period": "2024-Q4", "currency": "USD"},
            )
            for key, name, value in METRICS
        ]
        db.add_all(company_rows + metric_rows)
        db.flush()

        sentiments = ["positive", "neutral", "negative", "positive", "neutral"]
        scores = [0.62, 0.15, -0.28, 0.81, 0.05]
        for record, sentiment, score in zip(company_rows[:5], sentiments, scores):
            db.add(
                Prediction(
                    gold_record_id=record.id,
                    model_name="seed-model",
                    impact_score=score,
                    sentiment=sentiment,
                    status="completed",
                )
            )
        db.commit()
        print("Seeded 2 runs, 20 records, 5 predictions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
