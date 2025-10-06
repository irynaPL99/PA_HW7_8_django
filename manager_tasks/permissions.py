# hw19, new field owner, new customers permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение, которое позволяет:
    - Любому пользователю выполнять безопасные методы (GET, HEAD, OPTIONS).
    - Только авторизованному пользователю выполнять POST.
    - Только владельцу объекта выполнять PUT, PATCH, DELETE.
    """
    def has_permission(self, request, view):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем
        if request.method in SAFE_METHODS:
            return True
        # Для POST требуется авторизация
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
    # Разрешаем безопасные методы всем
        if request.method in SAFE_METHODS:
            return True
        # Для PUT, PATCH, DELETE проверяем, является ли пользователь владельцем
        return obj.owner is not None and obj.owner == request.user
