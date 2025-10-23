from apps.user.models import User
from utils.encrypt import PasswordEncryptor
from rest_framework import serializers
class UserDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id']
        extra_kwargs = {
            'user_id': {'required': True}
        }



