from rest_framework import serializers

from utils.encrypt import PasswordEncryptor
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
        fields = '__all__'
        # fields = ['username', 'password',  'phone_number', 'age', 'gender']
        read_only_fields = ['user_id', 'create_time']
        extra_kwargs = {
            'username': {'required': True},
            'password': { 'required': True},
            'phone_number': {'required': True}
        }

    def validate_phone_number(self, value):
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号码格式不正确")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("手机号码已被注册")
        return value

    def create(self, validated_data):
        """创建用户时自动设置user_id从10000开始"""
        # 获取当前最大的user_id
        last_user = User.objects.all().order_by('-user_id').first()
        if last_user:
            validated_data['user_id'] = last_user.user_id + 1
        else:
            validated_data['user_id'] = 10000
        plain_password = validated_data['password']
        validated_data['password'] = PasswordEncryptor.set_password(plain_password)
        return super().create(validated_data)