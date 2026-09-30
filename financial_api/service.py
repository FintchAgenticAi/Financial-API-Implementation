"""Gold use cases. This module does not execute SQL."""

from typing import Any

from sqlalchemy.orm import Session

from financial_api import repository
from financial_api.exceptions import RecordNotFound
from models.financial_gold import GoldFinancialRecord, GoldPipelineRun, Prediction


def list_runs(db: Session, skip: int, limit: int) -> list[GoldPipelineRun]:
    """Return a page of pipeline runs."""
    return repository.find_runs(db, skip, limit)


def list_records(
    db: Session,
    skip: int,
    limit: int,
    entity_type: str | None = None,
) -> list[GoldFinancialRecord]:
    """Return a page of Gold records."""
    return repository.find_records(db, skip, limit, entity_type)


def get_record(db: Session, record_id: int) -> GoldFinancialRecord:
    """Return one Gold record or raise RecordNotFound."""
    record = repository.get_by_id(db, record_id)
    if record is None:
        raise RecordNotFound(record_id)
    return record


def dashboard_summary(db: Session) -> dict[str, int]:
    """Return counts for the dashboard."""
    return repository.dashboard_summary(db)


def list_predictions(
    db: Session,
    skip: int,
    limit: int,
    gold_record_id: int | None = None,
) -> list[Prediction]:
    """Return a page of predictions."""
    return repository.list_predictions(db, skip, limit, gold_record_id)


def request_prediction(db: Session, gold_record_id: int) -> Prediction:
    """Store a Phase 1 stub prediction after confirming the Gold record exists."""
    get_record(db, gold_record_id)
    # TODO Phase 2: call prediction_client.call_prediction_service with the Gold
    # record payload and store the returned impact_score and sentiment.
    return repository.insert_prediction(
        db,
        {
            "gold_record_id": gold_record_id,
            "model_name": "phase1-stub",
            "impact_score": 0.0,
            "sentiment": None,
            "status": "stub",
        },
    )


def ingest_run(
    db: Session,
    batch_id: str,
    records: list[dict[str, Any]],
    source_file_id: str | None = None,
) -> tuple[int, int]:
    """Store a dev batch that mimics the Data Pumper. Returns run id and row count."""
    run, inserted_count = repository.insert_run_with_records(
        db,
        batch_id=batch_id,
        records=records,
        source_file_id=source_file_id,
        meta={"loader": "dev-ingest"},
    )
    return run.id, inserted_count
