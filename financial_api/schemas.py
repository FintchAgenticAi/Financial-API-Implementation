"""Request and response contracts for the Gold Financial API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    """Base schema that can be built from SQLAlchemy rows."""

    model_config = ConfigDict(from_attributes=True)


class RunOut(ORMModel):
    """One Gold pipeline run."""

    id: int
    batch_id: str
    source_file_id: str | None
    row_count: int
    status: str
    started_at: datetime
    finished_at: datetime | None
    meta: dict[str, Any] | None


class RecordOut(ORMModel):
    """Curated Gold record returned by list endpoints."""

    id: int
    pipeline_run_id: int
    entity_type: str
    entity_key: str
    payload: dict[str, Any]
    created_at: datetime


class RecordDetailOut(RecordOut):
    """Single-record view. Same fields as RecordOut in Phase 1."""


class SummaryOut(ORMModel):
    """Dashboard counts."""

    run_count: int
    record_count: int
    prediction_count: int


class PredictionCreate(BaseModel):
    """Body for requesting a prediction."""

    model_config = ConfigDict(from_attributes=True)

    gold_record_id: int = Field(..., ge=1)


class PredictionOut(ORMModel):
    """Stored prediction."""

    id: int
    gold_record_id: int
    model_name: str
    impact_score: float
    sentiment: str | None
    status: str
    created_at: datetime


class IngestRecordIn(BaseModel):
    """One record inside a dev ingest batch."""

    entity_type: str = Field(..., min_length=1, max_length=64)
    entity_key: str = Field(..., min_length=1, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)


class IngestRunIn(BaseModel):
    """Dev stand-in for a Data Pumper batch."""

    batch_id: str = Field(..., min_length=1, max_length=128)
    source_file_id: str | None = None
    records: list[IngestRecordIn]


class IngestRunOut(BaseModel):
    """Result of a dev ingest."""

    run_id: int
    inserted_count: int
