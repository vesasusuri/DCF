from typing import Any

from app.domain.interfaces.event_publisher import IEventPublisher


class CeleryEventPublisher(IEventPublisher):
    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        from app.worker import celery_app

        celery_app.send_task("app.worker.handle_event", args=[event_type, payload])
