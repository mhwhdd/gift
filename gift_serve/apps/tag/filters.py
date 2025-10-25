import django_filters
from django.db.models import Q
from .models import Tag


class TagFilter(django_filters.FilterSet):
    """
    标签过滤器 - 支持模糊查询、组合查询和分页
    """
    # 模糊查询
    tag_name = django_filters.CharFilter(
        field_name='tag_name',
        lookup_expr='contains',
        label='标签名称模糊查询'
    )

    # 精确查询
    tag_type = django_filters.ChoiceFilter(
        choices=Tag.TAG_TYPE_CHOICES,
        label='标签类型精确查询'
    )

    is_active = django_filters.BooleanFilter(
        label='激活状态查询'
    )

    # 多标签类型查询
    tag_type_in = django_filters.MultipleChoiceFilter(
        field_name='tag_type',
        choices=Tag.TAG_TYPE_CHOICES,
        lookup_expr='in',
        label='多标签类型查询'
    )

    # 综合搜索
    search = django_filters.CharFilter(method='filter_search', label='综合搜索')

    # 创建时间范围查询
    created_after = django_filters.DateTimeFilter(
        field_name='created_time',
        lookup_expr='gte',
        label='创建时间之后'
    )

    created_before = django_filters.DateTimeFilter(
        field_name='created_time',
        lookup_expr='lte',
        label='创建时间之前'
    )

    def filter_search(self, queryset, name, value):
        """自定义搜索方法"""
        if value:
            return queryset.filter(
                Q(tag_name__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset

    class Meta:
        model = Tag
        fields = {
            'tag_name': ['exact', 'contains'],
            'tag_type': ['exact', 'in'],
            'is_active': ['exact'],
            'created_time': ['gte', 'lte'],
        }