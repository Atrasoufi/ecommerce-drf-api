from django.urls import path

from .views.views import CommentViewSet


comment_list = CommentViewSet.as_view({ "get": "list", "post": "create",})

comment_detail = CommentViewSet.as_view({ "get": "retrieve", "delete": "destroy",})

comment_approve = CommentViewSet.as_view({ "post": "approve",})

comment_reject = CommentViewSet.as_view({"post": "reject",})


urlpatterns = [
    path("comments/",comment_list,name="comment-list",),
    path("comments/<int:pk>/",comment_detail,name="comment-detail",),
    path("comments/<int:pk>/approve/",comment_approve,name="comment-approve",),
    path("comments/<int:pk>/reject/",comment_reject,name="comment-reject",),
]