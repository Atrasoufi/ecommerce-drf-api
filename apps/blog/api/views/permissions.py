from rest_framework.permissions import BasePermission


class IsCommentOwnerOrStaff(BasePermission):
    """
    فقط نویسنده کامنت یا staff اجازه حذف دارد.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                obj.user_id == request.user.id
                or request.user.is_staff
            )
        )
