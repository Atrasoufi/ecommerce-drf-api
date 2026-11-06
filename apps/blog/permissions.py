from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access for public users (filtered by view),
    but restrict write/update/delete operations strictly to authors or staff members.
    """

    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deny access if the user is not authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Staff and admins have full control over all posts
        if request.user.is_staff:
            return True

        # Check if the requesting user is the actual author of the post
        return obj.author == request.user


class IsCommentOwnerOrStaff(BasePermission):
    """
    Allow comment deletion only if the requesting user is the owner of the comment or a staff member.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                obj.user_id == request.user.id
                or request.user.is_staff
            )
        )