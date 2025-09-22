from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import OAuthApplication, OAuthToken


@api_view(["GET"])  # ping mínimo
@permission_classes([AllowAny])
def ping(request):
    return Response({"status": "ok"})


@api_view(["POST"])  # OAuth2 client_credentials (minimal)
@permission_classes([AllowAny])
def oauth_token_view(request):
    data = request.data or {}
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
    grant_type = data.get("grant_type")

    if grant_type != "client_credentials":
        return Response({"error": "unsupported_grant_type"}, status=status.HTTP_400_BAD_REQUEST)
    if not client_id or not client_secret:
        return Response({"error": "invalid_client"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        app = OAuthApplication.objects.get(client_id=client_id, client_secret=client_secret)
    except OAuthApplication.DoesNotExist:
        return Response({"error": "invalid_client"}, status=status.HTTP_401_UNAUTHORIZED)

    # Generate and persist token
    access_token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(seconds=3600)

    # Create OAuth token
    oauth_token = OAuthToken.objects.create(
        token=access_token,
        application=app,
        scope="read,write",
        expires_at=expires_at
    )

    return Response({
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "read write"
    })


