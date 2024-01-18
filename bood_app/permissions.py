from rest_framework import permissions


class IsOwnerOrAdminPersonCard(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.is_staff or request.user == obj.person


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.is_staff or request.user == obj.person_card.person
