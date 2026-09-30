"""Domain errors raised by the Financial API service layer."""


class RecordNotFound(Exception):
    """Raised when a Gold financial record id does not exist."""

    def __init__(self, record_id: int) -> None:
        self.record_id = record_id
        super().__init__(f"Gold record {record_id} not found")


class PredictionServiceUnavailable(Exception):
    """Raised when the external prediction service cannot be reached (Phase 2)."""
