from django.utils import timezone
from rest_framework import serializers
from .models import Tag


class TagListSerializer(serializers.ModelSerializer):
    """
    标签列表序列化器（用于分页列表）
    """
    tag_type_display = serializers.CharField(source='get_tag_type_display', read_only=True)
    # 自定义时间序列化格式
    created_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S',
        read_only=True,
        default=timezone.now
    )
    class Meta:
        model = Tag
        fields = ['tag_id', 'tag_type', 'tag_type_display', 'tag_name', 'description', 'is_active', 'created_time']


class TagDetailSerializer(serializers.ModelSerializer):
    """
    标签详情序列化器（用于单个标签操作）
    """

    class Meta:
        model = Tag
        fields = ['tag_id', 'tag_type', 'tag_name', 'description', 'is_active', 'created_time']
        read_only_fields = ['tag_id', 'created_time']

    def validate_tag_name(self, value):
        """验证标签名称唯一性"""
        instance = self.instance
        if instance and Tag.objects.filter(tag_name=value).exclude(tag_id=instance.tag_id).exists():
            raise serializers.ValidationError("标签名称已存在")
        elif not instance and Tag.objects.filter(tag_name=value).exists():
            raise serializers.ValidationError("标签名称已存在")
        return value

    def validate(self, attrs):
        """全局验证钩子"""
        tag_type = attrs.get('tag_type', getattr(self.instance, 'tag_type', None))

        # 系统标签不允许修改为其他类型
        if self.instance and self.instance.tag_type == 'system' and tag_type != 'system':
            raise serializers.ValidationError("系统标签类型不可修改")

        return attrs