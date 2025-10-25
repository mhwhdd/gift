import jwt
import datetime
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from typing import Dict, Optional, Tuple


class TokenManager:
    """JWT Token管理器"""

    @staticmethod
    def create_token(user_id: int, username: str, token_type: str = 'access') -> str:
        """创建JWT Token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'type': token_type,
            'exp': datetime.datetime.utcnow() + (
                settings.JWT_CONFIG['ACCESS_TOKEN_LIFETIME'] if token_type == 'access'
                else settings.JWT_CONFIG['REFRESH_TOKEN_LIFETIME']
            ),
            'iat': datetime.datetime.utcnow(),
        }

        token = jwt.encode(
            payload,
            settings.JWT_CONFIG['SECRET_KEY'],
            algorithm=settings.JWT_CONFIG['ALGORITHM']
        )
        return token

    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Dict]:
        """验证Token有效性"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_CONFIG['SECRET_KEY'],
                algorithms=[settings.JWT_CONFIG['ALGORITHM']]
            )
            # 检查Token是否在黑名单中
            if TokenManager.is_blacklisted(token):
                print("==============")
                return False, {'error': 'Token已失效', 'code': 401}

            return True, payload

        except jwt.ExpiredSignatureError:
            return False, {'error': 'Token已过期', 'code': 401}
        except jwt.InvalidTokenError:
            return False, {'error': '无效的Token', 'code': 401}
        except Exception as e:
            return False, {'error': f'Token验证异常: {str(e)}', 'code': 500}

    @staticmethod
    def is_blacklisted(token: str) -> bool:
        """检查Token是否在黑名单中"""
        return cache.get(f'blacklist_{token}') is not None

    @staticmethod
    def add_to_blacklist(token: str, payload: Dict) -> bool:
        """将Token加入黑名单"""
        try:
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                # 计算剩余过期时间
                expire_seconds = exp_timestamp - int(datetime.datetime.utcnow().timestamp())
                if expire_seconds > 0:
                    cache.set(f'blacklist_{token}', 'blacklisted', expire_seconds)
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def refresh_token(refresh_token: str) -> Tuple[bool, Dict]:
        """刷新Token"""
        is_valid, payload = TokenManager.verify_token(refresh_token)
        if not is_valid or payload.get('type') != 'refresh':
            return False, {'error': '无效的刷新Token', 'code': 401}

        # 生成新的访问令牌
        new_access_token = TokenManager.create_token(
            payload['user_id'],
            payload['username'],
            'access'
        )

        return True, {
            'access_token': new_access_token,
            'user_id': payload['user_id'],
            'username': payload['username']
        }

    @staticmethod
    def get_token_from_request(request):
        """从请求中获取Token（支持Header和URL参数）"""
        # 从Authorization头获取
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print("auth_header==={}".format(auth_header))
        if auth_header.startswith('Bearer '):
            return auth_header[7:]

        # 从URL参数获取
        token = request.GET.get('token', '')
        if token:
            return token

        return None


class ResponseHelper:
    """响应助手类"""

    @staticmethod
    def success(data=None, message="操作成功", code=200):
        return JsonResponse({
            'code': code,
            'success': True,
            'message': message,
            'data': data
        })

    @staticmethod
    def error(message="操作失败", code=400, data=None):
        return JsonResponse({
            'code': code,
            'success': False,
            'message': message,
            'data': data
        }, status=code)