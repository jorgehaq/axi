from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone
from .models import OAuthToken


class OAuth2AuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle OAuth2 Bearer token authentication
    """

    def process_request(self, request):
        # Skip OAuth2 for certain paths
        skip_paths = [
            '/api/v1/oauth/token',  # Token endpoint
            '/admin/',              # Django admin
            '/api/docs/',          # API docs
        ]

        if any(request.path.startswith(path) for path in skip_paths):
            return None

        # Only check OAuth2 for API endpoints that need protection
        protected_paths = [
            '/api/v1/datasets/',
            '/api/me/',
        ]

        should_check_oauth = any(request.path.startswith(path) for path in protected_paths)
        if not should_check_oauth:
            return None

        # Check for Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'error': 'unauthorized',
                'message': 'Bearer token required'
            }, status=401)

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        try:
            oauth_token = OAuthToken.objects.select_related('application').get(
                token=token,
                expires_at__gt=timezone.now()
            )

            # Attach token info to request
            request.oauth_token = oauth_token
            request.oauth_scopes = oauth_token.scope.split(',') if oauth_token.scope else []

            # Set a dummy user for compatibility with IsAuthenticated
            # In a real implementation, you'd associate tokens with users
            from django.contrib.auth.models import AnonymousUser
            if not hasattr(request, 'user') or request.user.is_anonymous:
                # Create a simple user representation for OAuth2
                class OAuth2User:
                    is_authenticated = True
                    is_anonymous = False
                    id = f"oauth_{oauth_token.application.client_id}"
                    username = f"oauth_user_{oauth_token.application.name}"
                    email = f"{oauth_token.application.client_id}@oauth.local"

                request.user = OAuth2User()

        except OAuthToken.DoesNotExist:
            return JsonResponse({
                'error': 'invalid_token',
                'message': 'Invalid or expired token'
            }, status=401)

        return None