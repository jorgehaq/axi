from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid

# core/models.py - OPCIONAL: Custom upload path
# from django.db import models
# from django.conf import settings
# import uuid
from datetime import datetime

class Token(models.Model):
    key = models.CharField(max_length=40, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    @staticmethod
    def create_for(user):
        token = uuid.uuid4().hex  # 32 chars
        # añade 8 chars para 40 total
        token = (token + uuid.uuid4().hex)[:40]
        return Token.objects.create(user=user, key=token)

    def __str__(self):
        return f"{self.user.username}:{self.key[:6]}***"


def dataset_upload_path(instance, filename):
    """Generate upload path: datasets/2024/08/user123/uuid-filename.csv"""
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}-{filename}"
    return f"datasets/{datetime.now().year}/{datetime.now().month:02d}/user{instance.uploaded_by.id}/{new_filename}"

class DataFile(models.Model):
    file = models.FileField(
        upload_to=dataset_upload_path,
        # storage=get_media_storage,  # Si usas custom storage
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # Nuevo: track size
    original_filename = models.CharField(max_length=255, blank=True)  # Nuevo: nombre original

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.original_filename = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_filename} by {self.uploaded_by}"