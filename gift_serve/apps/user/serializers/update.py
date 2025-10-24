from .base import UserSerializer
from rest_framework import serializers

from ..models import User


class UserUpdateSerializer(serializers.ModelSerializer):  # 继承原序列化器
    """
    用于更新用户信息的序列化器
    在原有字段基础上，增加更新操作特定的约束或字段
    """

    # 如果原序列化器已包含所有你需要的字段（username, birthday, age, gender, phone_number），
    # 你只需要重写 Meta 类或添加新的验证即可。

    class Meta:  # 继承原序列化器的Meta类
        user_id = serializers.IntegerField(required=True, write_only=True)
        model = User
        fields = ['user_id','username','user_icon', 'birthday', 'age', 'gender', 'phone_number']
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': False},
            'birthday': {'required': False},
            'user_icon': {'required': False},
            'age': {'required': False},
            'gender': {'required': False},
            'phone_number': {'required': False, 'allow_blank': False}
        }

    def validate(self, attrs):
        received_fields = set(self.initial_data.keys())
        allowed_fields = set(self.fields.keys())
        # 移除user_id，因为它不是可修改字段
        allowed_fields.discard('user_id')
        # 检查是否有不允许的字段
        invalid_fields = received_fields - allowed_fields - {'user_id'}
        if invalid_fields:
            raise serializers.ValidationError(
                f"不允许修改以下字段: {', '.join(invalid_fields)}"
            )

        # 检查是否至少传递了一个可修改字段（排除user_id）
        update_fields = received_fields & allowed_fields
        if not update_fields:
            raise serializers.ValidationError(
                "至少需要传递一个可修改的字段（username、birthday、age、gender、phone_number）"
            )

        return attrs