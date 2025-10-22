from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer
from utils.encrypt import PasswordEncryptor


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


class UserRegistrationAPIView(APIView):
    """
    用户注册接口
    支持字段：用户名、密码、手机号码、年龄、性别
    """
    # permission_classes = [AllowAny]  # 允许匿名用户访问

    def post(self, request):
        try:
            # 使用序列化器验证数据
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                # 保存用户
                user = serializer.save()

                # 返回成功响应
                response_data = {
                    'code': status.HTTP_201_CREATED,
                    'message': '注册成功',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                # 返回验证错误
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': '参数验证失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # 处理意外错误
            return Response({
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': '服务器内部错误',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    """支持用户名和手机号登录的接口"""

    def post(self, request):
        login_type = request.data.get('login_type')  # 'username' 或 'phone'
        password = request.data.get('password')

        # 参数校验
        if not login_type or not password:
            return Response({
                'code': 400,
                'message': '缺少必要参数: login_type 和 password'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 根据登录类型获取用户名或手机号
        if login_type == 'username':
            username = request.data.get('username')
            if not username:
                return Response({
                    'code': 400,
                    'message': '用户名登录方式需要提供 username 参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            user = self.authenticate_by_username(username, password)

        elif login_type == 'phone':
            phone_number = request.data.get('phone_number')
            if not phone_number:
                return Response({
                    'code': 400,
                    'message': '手机号登录方式需要提供 phone_number 参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            user = self.authenticate_by_phone(phone_number, password)

        else:
            return Response({
                'code': 400,
                'message': '不支持的登录类型，请使用 username 或 phone'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证用户
        if user is not None:
            print("======================{}".format(user))
            if not user.is_deleted:
                # login(request, user)  # Django 会话登录
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'user_id': user.user_id,
                        'username': user.username,
                        'login_type': login_type
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'code': 403,
                    'message': '用户账户已被禁用'
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({
                'code': 401,
                'message': '用户名/手机号或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)

    def authenticate_by_username(self, username, password):
        """通过用户名认证"""
        try:
            user = User.objects.filter(username=username).first()
            ser_data = UserSerializer(user).data
            db_password=ser_data['password']
            # 调用工具中的 check_password 方法验证密码
            if  PasswordEncryptor.check_password(password, db_password):  # 假设 check_password 接受明文密码和加密密码
                return user
        except User.DoesNotExist:
            pass
        return None

    def authenticate_by_phone(self, phone_number, password):
        """通过手机号认证"""
        try:
            user = User.objects.get(phone_number=phone_number)
            ser_data = UserSerializer(user).data
            db_password = ser_data['password']
            # 调用工具中的 check_password 方法验证密码
            if PasswordEncryptor.check_password(password, db_password):
                return user
        except User.DoesNotExist:
            pass
        return None