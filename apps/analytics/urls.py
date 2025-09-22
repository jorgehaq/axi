from django.urls import path
from .views import ping

urlpatterns = [
    path("analytics/ping", ping, name="analytics_ping"),
]

