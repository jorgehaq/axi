from django.urls import path
from .views import login_view, upload_view, health

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/login", login_view, name="login"),
    path("upload", upload_view, name="upload"),
]