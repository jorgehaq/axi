from rest_framework.permissions import BasePermission


class HasOAuth2Scope(BasePermission):
    """
    Permission class to check OAuth2 scopes
    """
    required_scopes = []

    def has_permission(self, request, view):
        # Check if request has OAuth2 token attached by middleware
        if not hasattr(request, 'oauth_token'):
            return False

        if not hasattr(request, 'oauth_scopes'):
            return False

        # Check if any required scope is present
        if not self.required_scopes:
            return True

        return any(scope in request.oauth_scopes for scope in self.required_scopes)


class ReadScope(HasOAuth2Scope):
    """Permission requiring 'read' scope"""
    required_scopes = ['read']


class WriteScope(HasOAuth2Scope):
    """Permission requiring 'write' scope"""
    required_scopes = ['write']


class ReadWriteScope(HasOAuth2Scope):
    """Permission requiring both 'read' and 'write' scopes"""
    required_scopes = ['read', 'write']