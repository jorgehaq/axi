from rest_framework.permissions import BasePermission


class IsOwnerOfDataFile(BasePermission):
    """Permiso: el usuario debe ser propietario del DataFile."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.uploaded_by_id == request.user.id

