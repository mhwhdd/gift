from django.urls import path
from .views import UserListAPIView,UserRegistrationAPIView,LoginView
urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='login'),
]