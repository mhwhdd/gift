from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers.base import UserSerializer
from .serializers.register import UserRegisterSerializer
from .serializers.update import UserUpdateSerializer
from .serializers.filters import UserFilter
from  .serializers.pwd import UserUpdatePwdSerializer
from utils.encrypt import PasswordEncryptor
from rest_framework.generics import ListAPIView


# Create your views here.
class UserListAPIView(ListAPIView):
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer #序列化输出数据
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter # 过滤
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()) #过滤查询
        serializer = self.get_serializer(queryset, many=True) #序列化
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
            # 使用UserRegisterSerializer验证数据[2,7](@ref)
            serializer = UserRegisterSerializer(data=request.data)

            # 先验证数据，再访问数据[7](@ref)
            if serializer.is_valid():
                # 保存用户
                user = serializer.save()

                # 使用UserSerializer序列化输出数据[2](@ref)
                user_serializer = UserSerializer(user)

                # 返回成功响应
                response_data = {
                    'code': status.HTTP_201_CREATED,
                    'message': '注册成功',
                    'data': user_serializer.data  # 使用UserSerializer的数据
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

class UserUpdateAPIView(APIView):
    def post(self, request):
        """
                通过user_id更新用户信息
                - user_id必传，用于指定要修改的用户
                - 只允许修改username、birthday、age、gender、phone_number字段
                - 可少传，没传的字段不修改
                - 至少需要传递一个可修改字段（除了user_id）
                """
        # 使用序列化器进行验证
        serializer = UserUpdateSerializer(data=request.data)
        # return Response(serializer.data)
        if not serializer.is_valid():
            return Response(
                {"error": "数据验证失败", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        # 获取user_id并查询用户
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": f"用户不存在 (user_id: {user_id})"},
                status=status.HTTP_404_NOT_FOUND
            )
        # 检查权限：用户只能修改自己的信息，除非是管理员
        # if user != request.user and not request.user.is_staff:
        #     return Response(
        #         {"error": "您没有权限修改其他用户的信息"},
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        # 创建更新数据副本（移除user_id）
        update_data = request.data.copy()
        update_data.pop('user_id', None)
        # 执行更新
        update_serializer = UserSerializer(
            instance=user,
            data=update_data,
            partial=True
        )

        if update_serializer.is_valid():
            update_serializer.save()
            return Response({
                "message": "用户信息更新成功",
                "user_id": user_id,
                "data": update_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "更新失败",
                "details": update_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
class UserUpdatePasswordAPIView(APIView):
    def post(self, request):
        # 1. 使用 UserUpdatePwdSerializer 验证输入数据
        pwd_ser = UserUpdatePwdSerializer(data=request.data)
        if not pwd_ser.is_valid():
            return Response(
                {"error": "数据验证失败", "details": pwd_ser.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. 获取user_id并查询用户
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": f"用户不存在 (user_id: {user_id})"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. 直接使用验证后的序列化器执行更新！
        # 将数据库查询到的user实例和验证通过的数据传入
        updated_user = pwd_ser.update(user, pwd_ser.validated_data)
        return Response({
            "message": "密码更新成功",
            "user_id": UserSerializer(updated_user).data,
            # 注意：除非明确序列化，否则这里不应返回密码信息
        }, status=status.HTTP_200_OK)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
