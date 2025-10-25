# serializers.py
from rest_framework import serializers
from .models import UserTagRelationship
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTagRelationshipListSerializer(serializers.ModelSerializer):
    """列表序列化器（简化版，用于列表查询）"""
    username = serializers.CharField(source='user.username', read_only=True)
    tag_name = serializers.CharField(source='tag.tag_name', read_only=True)

    class Meta:
        model = UserTagRelationship
        fields = [
            'relation_id', 'user', 'username',
            'tag', 'tag_name', 'relation_time', 'weight',
            'status', 'relation_description'
        ]
        read_only_fields = ['relation_id', 'relation_time']


class UserTagRelationshipDetailSerializer(serializers.ModelSerializer):
    """详情序列化器（完整版）"""
    username = serializers.CharField(source='user.username', read_only=True)
    tag_name = serializers.CharField(source='tag.tag_name', read_only=True)

    class Meta:
        model = UserTagRelationship
        fields = [
            'relation_id', 'user', 'username',  'tag', 'tag_name',
            'relation_time', 'weight', 'status', 'relation_description'
        ]
        read_only_fields = ['relation_id', 'relation_time']
        extra_kwargs = {
            'weight': {'min_value': 0.0, 'max_value': 1.0}
        }

    def validate(self, attrs):
        """验证用户和标签组合的唯一性"""
        user = attrs.get('user')
        tag = attrs.get('tag')

        if user and tag:
            instance = getattr(self, 'instance', None)
            queryset = UserTagRelationship.objects.filter(user=user, tag=tag)

            if instance:
                queryset = queryset.exclude(relation_id=instance.relation_id)

            if queryset.exists():
                raise serializers.ValidationError("该用户与此标签的关联关系已存在")

        return attrs