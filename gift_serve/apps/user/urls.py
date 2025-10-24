from django.urls import path
from .views import (UserListAPIView,UserRegistrationAPIView,LoginView,
                    UserUpdateAPIView,UserUpdatePasswordAPIView,UserDeleteAPIView,
                    UserDestroyAPIView,LogoutAPIView
                    )

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('updatepwd/', UserUpdatePasswordAPIView.as_view(), name='update-password'),
    path('delete/', UserDeleteAPIView.as_view(), name='user-delete'),
    path('destroy/', UserDestroyAPIView.as_view(), name='user-destroy'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),

]