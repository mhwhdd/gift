from apps.user.models import User
from utils.encrypt import PasswordEncryptor
from rest_framework import serializers
class UserUpdatePwdSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['user_id', 'password']
        extra_kwargs = {
            'user_id': {'required': True},
            'password': {'required': True},
        }

    def update(self, instance, validated_data):
        """
        重写update方法，处理密码加密。
        instance: 从数据库查询到的User对象
        validated_data: 通过验证的数据
        """
        # 获取前端传来的明文密码
        plain_password = validated_data['password']
        # 使用您的工具类加密密码
        encrypted_password = PasswordEncryptor.set_password(plain_password)
        # 将加密后的密码设置到用户实例上
        instance.password = encrypted_password
        # 调用save方法保存用户实例（只会更新变更的字段，这里是password）
        instance.save()
        return instance

