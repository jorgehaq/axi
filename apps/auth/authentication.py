from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import OAuthToken


class OAuth2Authentication(BaseAuthentication):
    """
    DRF Authentication class for OAuth2 Bearer tokens
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        try:
            oauth_token = OAuthToken.objects.select_related('application').get(
                token=token,
                expires_at__gt=timezone.now()
            )

            # Create a simple user representation for OAuth2
            class OAuth2User:
                is_authenticated = True
                is_anonymous = False
                id = f"oauth_{oauth_token.application.client_id}"
                username = f"oauth_user_{oauth_token.application.name}"
                email = f"{oauth_token.application.client_id}@oauth.local"

                def __str__(self):
                    return self.username

            user = OAuth2User()

            # Attach token info to user for access in views
            user.oauth_token = oauth_token
            user.oauth_scopes = oauth_token.scope.split(',') if oauth_token.scope else []

            return (user, oauth_token)

        except OAuthToken.DoesNotExist:
            return None

    def authenticate_header(self, request):
        return 'Bearer'