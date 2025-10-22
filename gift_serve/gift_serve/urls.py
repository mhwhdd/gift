from django.contrib import admin
from django.urls import path, include

from apps import user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.user.urls')),
    # path('api/', include('user.urls')),
]
