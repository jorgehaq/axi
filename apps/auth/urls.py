from django.urls import path
from .views import ping, oauth_token_view

urlpatterns = [
    path("auth/ping", ping, name="auth_ping"),
    path("oauth/token", oauth_token_view, name="oauth_token"),
]
