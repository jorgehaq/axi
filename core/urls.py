from django.urls import path
from .views import login_view, upload_view, health, upload_view, health, data_preview, data_summary

urlpatterns = [
    # LOGIN, UPLOAD, HEALTHCHECK 
    path("health/", health, name="health"),
    path("auth/login", login_view, name="login"),
    path("upload", upload_view, name="upload"),
    

    # CORE ANALYTICS
    path("data/<int:id>/preview", data_preview, name="data_preview"),
    path("data/<int:id>/summary", data_summary, name="data_summary"),
]

