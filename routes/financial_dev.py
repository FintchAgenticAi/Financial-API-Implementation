"""Dev-only ingest that mimics the Data Pumper. Mounted when ENABLE_DEV_INGEST is true."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config.database import get_db
from config.settings import settings
from financial_api import service
from financial_api.schemas import IngestRunIn, IngestRunOut

router = APIRouter(prefix="/internal/dev", tags=["dev"])


@router.post("/ingest-run", response_model=IngestRunOut, status_code=201)
def ingest_run(body: IngestRunIn, db: Session = Depends(get_db)) -> IngestRunOut:
    """Create a Gold pipeline run and its records."""
    if not settings.enable_dev_ingest:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        run_id, inserted_count = service.ingest_run(
            db,
            batch_id=body.batch_id,
            records=[row.model_dump() for row in body.records],
            source_file_id=body.source_file_id,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail=f"Batch {body.batch_id} already exists"
        ) from None
    return IngestRunOut(run_id=run_id, inserted_count=inserted_count)
