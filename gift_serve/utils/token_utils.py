import jwt
import datetime
from django.conf import settings
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError


class JWTTokenManager:
    """JWT Token管理工具类"""

    # 使用Django的SECRET_KEY作为盐值
    _secret_key = settings.SECRET_KEY
    _algorithm = 'HS256'

    @classmethod
    def create_token(cls, username, password, expiry_days=7):
        """
        创建JWT Token
        Args:
            username: 用户名
            password: 密码（用于加强安全性）
            expiry_days: 过期天数，默认7天
        Returns:
            token字符串
        """
        try:
            # 创建payload，包含用户名、密码哈希和过期时间
            payload = {
                'username': username,
                'password_hash': str(hash(password)),  # 对密码进行哈希处理增强安全性
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expiry_days),
                'iat': datetime.datetime.utcnow(),  # 签发时间
                'iss': 'django-app'  # 签发者
            }

            # 生成token
            token = jwt.encode(payload, cls._secret_key, algorithm=cls._algorithm)
            return token

        except Exception as e:
            raise Exception(f"Token创建失败: {str(e)}")

    @classmethod
    def verify_token(cls, token):
        """
        验证JWT Token
        Args:
            token: token字符串
        Returns:
            tuple: (验证状态, payload数据或错误信息)
        """
        try:
            # 解码token
            payload = jwt.decode(token, cls._secret_key, algorithms=[cls._algorithm])
            return True, payload

        except ExpiredSignatureError:
            return False, "Token已过期，请重新登录"
        except InvalidTokenError:
            return False, "无效的Token"
        except PyJWTError as e:
            return False, f"Token验证异常: {str(e)}"
        except Exception as e:
            return False, f"Token验证失败: {str(e)}"

    @classmethod
    def get_token_from_request(cls, request):
        """
        从请求中获取token，优先从URL参数，其次从请求头
        Args:
            request: Django请求对象
        Returns:
            token字符串或None
        """
        # 1. 优先从URL参数获取
        token = request.GET.get('token')
        if token:
            return token

        # 2. 从Authorization头获取
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        elif auth_header.startswith('Token '):
            return auth_header.split(' ')[1]

        # 3. 从自定义头获取
        token = request.META.get('HTTP_X_AUTH_TOKEN')
        if token:
            return token

        return None