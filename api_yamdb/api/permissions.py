from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class ModeratorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.method in permissions.SAFE_METHODS
                     or request.user.is_moderator))


class UserReadOnlyPermission(IsAuthenticatedOrReadOnly):

    def has_permission(self, request, view):
        permission = super().has_permission(request, view)

        if permission and request.method in ('POST', 'PATCH', 'DELETE'):
            return False
        return permission
