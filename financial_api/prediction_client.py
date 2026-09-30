"""HTTP client for the external prediction service.

Phase 1 does not call the network. Phase 2 replaces the body of
``call_prediction_service`` with an httpx POST to PREDICTION_SERVICE_URL
and maps connection failures to PredictionServiceUnavailable.
"""

from typing import Any

from config.settings import settings


async def call_prediction_service(payload: dict[str, Any]) -> dict[str, Any]:
    """Send a Gold payload to the prediction service and return its scores.

    Phase 2 will POST ``payload`` to ``{PREDICTION_SERVICE_URL}/predict`` and
    return ``impact_score`` and ``sentiment``. This Phase 1 stub reads the
    configured URL and does not perform an HTTP call.
    """
    _url = settings.prediction_service_url
    raise NotImplementedError(
        "Phase 2: POST the Gold payload to "
        f"{_url} and return impact_score and sentiment."
    )
