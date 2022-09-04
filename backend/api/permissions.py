from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Read only all users. Admin is full access."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class AuthorOrReadOnly(permissions.BasePermission):
    """Author is full access."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or (obj.author == request.user)
