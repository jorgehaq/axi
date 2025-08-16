from django.urls import path
from .views import login_view, upload_view, health, data_preview, data_summary, data_rows, data_correlation, data_trend, get_download_url, bulk_upload_view

urlpatterns = [
    # LOGIN, UPLOAD, HEALTHCHECK 
    path("health/", health, name="health"),
    path("auth/login", login_view, name="login"),
    path("datasets/upload", upload_view, name="upload"),
    path("datasets/bulk-upload", bulk_upload_view, name="bulk_upload"),
    

    # CORE ANALYTICS
    path("datasets/<int:id>/preview", data_preview, name="data_preview"),
    path("datasets/<int:id>/summary", data_summary, name="data_summary"),

    # **analytics** (correlación, trends por fecha, filtros)
    path("datasets/<int:id>/rows", data_rows, name="data_rows"),
    path("datasets/<int:id>/correlation", data_correlation, name="data_correlation"),
    path("datasets/<int:id>/trend", data_trend, name="data_trend"),

    path("datasets/<int:id>/download-url/", get_download_url, name="download_url"),
]
