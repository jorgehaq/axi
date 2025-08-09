from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid

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

class DataFile(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} by {self.uploaded_by}"