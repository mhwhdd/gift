from rest_framework import serializers

from utils.encrypt import PasswordEncryptor
from apps.user.models import User
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    # 自定义时间序列化格式
    create_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S',
        read_only=True,
        default=timezone.now
    )
    birthday = serializers.DateField(format='%Y-%m-%d',default=None)

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


