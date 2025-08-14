# core/storage.py - NUEVO ARCHIVO
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from django.core.files.storage import get_storage_class
import os

class MediaStorage(GoogleCloudStorage):
    """Custom storage for media files"""
    bucket_name = settings.GS_BUCKET_NAME
    default_acl = None
    
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = self.bucket_name
        super().__init__(*args, **kwargs)

def get_media_storage():
    """Factory function to get appropriate storage"""
    if getattr(settings, 'USE_GCS', False):
        return MediaStorage()
    else:
        return get_storage_class()()