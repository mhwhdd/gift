# filters.py
import django_filters
from apps.user.models import User


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='contains')

    class Meta:
        model = User
        fields = {
            'user_id': ['exact'],
            'username': ['exact', 'contains'],#支持模糊查询
            'age': ['exact', 'gte', 'lte'],  # 支持等于、大于等于、小于等于
            'birthday': ['exact', 'gte', 'lte'],
            'gender': ['exact'],
            'create_time': ['exact', 'gte', 'lte', 'range'],# 支持等于、大于等于、范围
            'phone_number': ['exact', 'contains'],
        }
