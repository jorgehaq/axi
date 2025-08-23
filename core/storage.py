# core/storage.py - CORRECCION MINIMA
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from django.core.files.storage import get_storage_class

class MediaStorage(GoogleCloudStorage):
    """Custom storage for media files"""
    
    def __init__(self, *args, **kwargs):
        # Mover bucket_name aquí para evitar error en local
        bucket_name = getattr(settings, 'GS_BUCKET_NAME', None)
        if bucket_name:
            kwargs['bucket_name'] = bucket_name
        super().__init__(*args, **kwargs)

def get_media_storage():
    """Factory function to get appropriate storage"""
    if getattr(settings, 'USE_GCS', False):
        return MediaStorage()
    else:
        return get_storage_class()()