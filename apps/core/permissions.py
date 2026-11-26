from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrReadOnly(BasePermission):
    """Allow read-only access to everyone; restrict writes to staff users."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsOwnerOrStaffOrReadOnly(BasePermission):
    """Allow reads, but restrict writes to the object owner or staff users."""

    owner_field = "user"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return getattr(obj, self.owner_field, None) == request.user


class IsAuthorOrStaffOrReadOnly(IsOwnerOrStaffOrReadOnly):
    """Variant of ``IsOwnerOrStaffOrReadOnly`` for models with an author."""

    owner_field = "author"
