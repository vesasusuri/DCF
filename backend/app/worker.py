from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "dcf",
    broker=settings.broker_url,
    backend=settings.result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="app.worker.handle_event")
def handle_event(event_type: str, payload: dict) -> dict:
    return {"event_type": event_type, "payload": payload, "status": "received"}


@celery_app.task(name="app.worker.health_check")
def health_check() -> str:
    return "ok"
