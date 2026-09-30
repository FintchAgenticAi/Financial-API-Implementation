"""HTTP handlers for /api/v1/gold. Validation and status codes only."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from config.database import get_db
from financial_api import service
from financial_api.exceptions import RecordNotFound
from financial_api.schemas import (
    PredictionCreate,
    PredictionOut,
    RecordDetailOut,
    RecordOut,
    RunOut,
    SummaryOut,
)
from models.financial_gold import GoldFinancialRecord, GoldPipelineRun, Prediction

router = APIRouter(prefix="/api/v1/gold", tags=["gold"])


@router.get("/runs", response_model=list[RunOut])
def list_runs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[GoldPipelineRun]:
    """List Gold pipeline runs."""
    return service.list_runs(db, skip, limit)


@router.get("/records", response_model=list[RecordOut])
def list_records(
    entity_type: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[GoldFinancialRecord]:
    """List Gold records, optionally filtered by entity_type."""
    if entity_type == "":
        entity_type = None
    return service.list_records(db, skip, limit, entity_type)


@router.get("/records/{record_id}", response_model=RecordDetailOut)
def get_record(record_id: int, db: Session = Depends(get_db)) -> GoldFinancialRecord:
    """Return one Gold record."""
    try:
        return service.get_record(db, record_id)
    except RecordNotFound:
        raise HTTPException(
            status_code=404, detail=f"Gold record {record_id} not found"
        ) from None


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)) -> dict[str, int]:
    """Return dashboard counts."""
    return service.dashboard_summary(db)


@router.get("/predictions", response_model=list[PredictionOut])
def list_predictions(
    gold_record_id: int | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[Prediction]:
    """List predictions, optionally for one Gold record."""
    return service.list_predictions(db, skip, limit, gold_record_id)


@router.post("/predictions", response_model=PredictionOut, status_code=201)
def create_prediction(body: PredictionCreate, db: Session = Depends(get_db)) -> Prediction:
    """Request a prediction for an existing Gold record."""
    try:
        return service.request_prediction(db, body.gold_record_id)
    except RecordNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Gold record {body.gold_record_id} not found",
        ) from None
