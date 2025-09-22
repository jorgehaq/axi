from django.db import models
from django.utils import timezone


class Token(models.Model):
    key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='datasets_tokens')
    created_at = models.DateTimeField(default=timezone.now)

    @staticmethod
    def create_for(user):
        import secrets
        key = secrets.token_hex(20)
        return Token.objects.create(user=user, key=key)

    def __str__(self):
        return f"Token({self.user_id})"


def dataset_upload_path(instance, filename):
    return f"datasets/{instance.uploaded_by_id}/{filename}"


class DataFile(models.Model):
    file = models.FileField(upload_to=dataset_upload_path)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='datasets_files')
    created_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    original_filename = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except Exception:
                pass
        if self.file and not self.original_filename:
            self.original_filename = getattr(self.file, 'name', None)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"DataFile({self.id})"
