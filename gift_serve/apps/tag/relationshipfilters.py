# filters.py
import django_filters
from .models import UserTagRelationship


class UserTagRelationshipFilter(django_filters.FilterSet):
    """用户标签关联过滤器"""
    user = django_filters.NumberFilter(field_name='user__user_id')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='contains')
    tag = django_filters.NumberFilter(field_name='tag__tag_id')
    tag_name = django_filters.CharFilter(field_name='tag__tag_name', lookup_expr='contains')

    # 权重范围过滤
    min_weight = django_filters.NumberFilter(field_name='weight', lookup_expr='gte')
    max_weight = django_filters.NumberFilter(field_name='weight', lookup_expr='lte')

    # 时间范围过滤
    start_date = django_filters.DateTimeFilter(field_name='relation_time', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='relation_time', lookup_expr='lte')

    # 状态过滤
    status = django_filters.BooleanFilter(field_name='status')

    # 描述模糊搜索
    description = django_filters.CharFilter(field_name='relation_description', lookup_expr='contains')

    class Meta:
        model = UserTagRelationship
        fields = [
            'user', 'username', 'tag', 'tag_name',
            'status', 'min_weight', 'max_weight',
            'start_date', 'end_date', 'description'
        ]