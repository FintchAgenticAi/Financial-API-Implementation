"""SQLAlchemy reads and writes for Gold tables. No business rules."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.financial_gold import GoldFinancialRecord, GoldPipelineRun, Prediction


def find_runs(db: Session, skip: int, limit: int) -> list[GoldPipelineRun]:
    """Return a page of pipeline runs, newest id first."""
    stmt = (
        select(GoldPipelineRun)
        .order_by(GoldPipelineRun.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def find_records(
    db: Session,
    skip: int,
    limit: int,
    entity_type: str | None = None,
) -> list[GoldFinancialRecord]:
    """Return a page of Gold records, optionally filtered by entity_type."""
    stmt = select(GoldFinancialRecord)
    if entity_type:
        stmt = stmt.where(GoldFinancialRecord.entity_type == entity_type)
    stmt = stmt.order_by(GoldFinancialRecord.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_by_id(db: Session, record_id: int) -> GoldFinancialRecord | None:
    """Return one Gold record or None."""
    return db.get(GoldFinancialRecord, record_id)


def find_run_by_batch_id(db: Session, batch_id: str) -> GoldPipelineRun | None:
    """Return the pipeline run for a batch id, if it exists."""
    stmt = select(GoldPipelineRun).where(GoldPipelineRun.batch_id == batch_id)
    return db.scalars(stmt).first()


def dashboard_summary(db: Session) -> dict[str, int]:
    """Count runs, records, and predictions."""
    return {
        "run_count": db.scalar(select(func.count()).select_from(GoldPipelineRun)) or 0,
        "record_count": db.scalar(select(func.count()).select_from(GoldFinancialRecord)) or 0,
        "prediction_count": db.scalar(select(func.count()).select_from(Prediction)) or 0,
    }


def list_predictions(
    db: Session,
    skip: int,
    limit: int,
    gold_record_id: int | None = None,
) -> list[Prediction]:
    """Return a page of predictions, optionally for one Gold record."""
    stmt = select(Prediction)
    if gold_record_id is not None:
        stmt = stmt.where(Prediction.gold_record_id == gold_record_id)
    stmt = stmt.order_by(Prediction.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def insert_prediction(db: Session, payload: dict[str, Any]) -> Prediction:
    """Insert one prediction row and commit."""
    row = Prediction(**payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def insert_run_with_records(
    db: Session,
    *,
    batch_id: str,
    records: list[dict[str, Any]],
    source_file_id: str | None = None,
    meta: dict[str, Any] | None = None,
) -> tuple[GoldPipelineRun, int]:
    """Insert one completed pipeline run and its Gold records."""
    now = datetime.now(timezone.utc)
    run = GoldPipelineRun(
        batch_id=batch_id,
        source_file_id=source_file_id,
        row_count=len(records),
        status="completed",
        started_at=now,
        finished_at=now,
        meta=meta,
    )
    db.add(run)
    db.flush()
    for item in records:
        db.add(
            GoldFinancialRecord(
                pipeline_run_id=run.id,
                entity_type=item["entity_type"],
                entity_key=item["entity_key"],
                payload=item.get("payload") or {},
            )
        )
    db.commit()
    db.refresh(run)
    return run, len(records)
