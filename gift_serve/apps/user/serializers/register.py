from apps.user.models import User
from utils.encrypt import PasswordEncryptor
from .base import UserSerializer
from rest_framework import serializers
class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','user_icon', 'birthday', 'age', 'gender', 'phone_number','password']
        # 可以为字段额外添加属性，例如使其均为非必填
        extra_kwargs = {
            'username': {'required': True},
            'user_icon': {'required': False},
            'birthday': {'required': False},
            'age': {'required': False},
            'gender': {'required': False},
            'phone_number': {'required': True},
            'password': {'required': True},
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
