from rest_framework import permissions


class AdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class AdminOrReadOnlyPermission(AdminPermission):

    def has_permission(self, request, view):
        permission = super().has_permission(request, view)
        return (request.method in permissions.SAFE_METHODS
                or permission)


class AuthorModeratorAdminPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
