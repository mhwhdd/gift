from django.shortcuts import render
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer


# Create your views here.
class UserListAPIView(APIView):
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """获取所有用户列表"""
        users = User.objects.filter(is_deleted=False)
        serializer = UserSerializer(users, many=True)
        return Response({
            'code': 200,
            'message': '获取用户列表成功',
            'data': serializer.data
        })

    def post(self, request):
        """创建新用户"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 201,
                'message': '用户创建成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        })