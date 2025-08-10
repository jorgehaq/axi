from django.urls import path
from .views import login_view, upload_view, health, upload_view, health, data_preview, data_summary, data_rows, data_correlation, data_trend

urlpatterns = [
    # LOGIN, UPLOAD, HEALTHCHECK 
    path("health/", health, name="health"),
    path("auth/login", login_view, name="login"),
    path("upload", upload_view, name="upload"),
    

    # CORE ANALYTICS
    path("data/<int:id>/preview", data_preview, name="data_preview"),
    path("data/<int:id>/summary", data_summary, name="data_summary"),

    # **analytics** (correlación, trends por fecha, filtros)
    path("data/<int:id>/rows", data_rows, name="data_rows"),
    path("data/<int:id>/correlation", data_correlation, name="data_correlation"),
    path("data/<int:id>/trend", data_trend, name="data_trend"),
]
