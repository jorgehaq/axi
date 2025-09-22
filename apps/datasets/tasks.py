"""Celery tasks for dataset processing."""
from __future__ import annotations

from celery import shared_task

from .webhooks import notify_nexus, publish_echo_event


@shared_task
def process_dataset_upload(dataset_id: int) -> None:
    """Post-upload processing: notify external services."""
    notify_nexus(dataset_id, "uploaded")
    publish_echo_event("axi.dataset.uploaded", {"id": dataset_id})

