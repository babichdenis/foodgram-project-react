from rest_framework import permissions


class OwnerOnlyPermission(permissions.BasePermission):
    """
    Пользовательское разрешение.

    Разрешает чтение или изменение/удаление объекта только автору объекта.
    """

    def has_permission(self, request, view):
        """Определяет право доступа пользователя к представлению."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Определяет право доступа пользователя к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )