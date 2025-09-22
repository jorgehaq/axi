from django.db import models


# Modelos mínimos (portafolio)
class RefreshToken(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)


class OAuthApplication(models.Model):
    name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=64, unique=True)
    client_secret = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

