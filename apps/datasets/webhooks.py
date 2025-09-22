"""Webhook publishers for external integrations (Nexus, Echo)."""
from __future__ import annotations

from django.conf import settings
import requests


def notify_nexus(dataset_id: int, event_type: str) -> None:
    """Send dataset event to Nexus webhook."""
    url = getattr(settings, "NEXUS_WEBHOOK_URL", None)
    if not url:
        return
    payload = {"dataset_id": dataset_id, "event": event_type}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        # Intentionally swallow exceptions (non-critical path)
        pass


def publish_echo_event(event_name: str, data: dict) -> None:
    """Publish an event to Echo event bus."""
    base = getattr(settings, "ECHO_URL", None)
    if not base:
        return
    try:
        requests.post(f"{base}/events/publish/{event_name}", json=data, timeout=3)
    except Exception:
        # Intentionally swallow exceptions (non-critical path)
        pass

