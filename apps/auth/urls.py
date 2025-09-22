from django.urls import path
from .views import ping

urlpatterns = [
    path("auth/ping", ping, name="auth_ping"),
]

