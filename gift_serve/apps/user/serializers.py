from rest_framework import serializers
from .models import User
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    # 自定义时间序列化格式
    create_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S',
        read_only=True,
        default=timezone.now
    )

    # 显示性别选择项的显示值而非数字
    gender_display = serializers.CharField(
        source='get_gender_display',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'age', 'gender', 'gender_display',
            'create_time', 'is_deleted', 'introduction', 'address', 'phone_number'
        ]
        read_only_fields = ['user_id', 'create_time']

    def validate_phone_number(self, value):
        """自定义电话号码验证"""
        if value and not value.isdigit():
            raise serializers.ValidationError("电话号码只能包含数字")
        return value

    def create(self, validated_data):
        """创建用户时自动设置user_id从10000开始"""
        # 获取当前最大的user_id
        last_user = User.objects.all().order_by('-user_id').first()
        if last_user:
            validated_data['user_id'] = last_user.user_id + 1
        else:
            validated_data['user_id'] = 10000
        return super().create(validated_data)