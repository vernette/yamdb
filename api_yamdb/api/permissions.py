from rest_framework import permissions


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.is_admin


class ModeratorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        else:
            if request.method in permissions.SAFE_METHODS:
                return True
            return request.user.is_moderator


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_anonymous:
            return False
        elif request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_anonymous:
            return False
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        return True


class UserReadOnlyPermission(UserPermission):
    def has_permission(self, request, view):
        permission = super().has_permission(request, view)

        if permission and request.method in ('POST', 'PATCH', 'DELETE'):
            return False
        return permission
