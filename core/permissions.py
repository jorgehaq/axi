from rest_framework.permissions import BasePermission
from .models import DataFile

class IsOwnerOfDataFile(BasePermission):
    """
    Permite acceso solo si el usuario autenticado es el dueño del DataFile.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, DataFile):
            return obj.uploaded_by_id == request.user.id
        return True