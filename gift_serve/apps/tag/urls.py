from django.urls import path
from . import views

urlpatterns = [
    path('tags/', views.TagListAPIView.as_view(), name='tag-list'),
    path('tags/<int:tag_id>/', views.TagDetailAPIView.as_view(), name='tag-detail'),
    # 用户标签关联的基本CRUD操作
    path(
        'user-tag-relationships/',
        views.UserTagRelationshipListCreateView.as_view(),
        name='user-tag-relationship-list-create'
    ),
    path(
        'user-tag-relationships/<int:relation_id>/',
        views.UserTagRelationshipDetailView.as_view(),
        name='user-tag-relationship-detail'
    ),

    # 获取用户的所有标签
    path(
        'users/<int:user_id>/tags/',
        views.UserTagsView.as_view(),
        name='user-tags'
    ),

    # 获取标签的所有用户
    path(
        'tags/<int:tag_id>/users/',
        views.TagUsersView.as_view(),
        name='tag-users'
    ),
]