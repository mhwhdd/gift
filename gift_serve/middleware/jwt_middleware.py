# # your_app/middleware.py
# from django.utils.deprecation import MiddlewareMixin
# from django.http import JsonResponse
# from django.conf import settings
# from utils.token_utils import get_token_from_request, TokenManager
# import logging
#
# logger = logging.getLogger('django')
#
#
# class JWTAuthenticationMiddleware(MiddlewareMixin):
#     """
#     JWT认证中间件（使用MiddlewareMixin确保兼容性）[6,7](@ref)
#     """
#
#     def process_request(self, request):
#         """
#         处理请求，进行JWT认证
#         """
#         # 检查是否在白名单中
#         if self._is_no_auth_required(request):
#             return None
#
#         # 获取token
#         token = get_token_from_request(request)
#         if not token:
#             return JsonResponse({
#                 'code': 401,
#                 'message': '未提供认证Token',
#                 'detail': '请在URL参数中添加token或设置Authorization请求头'
#             }, status=401)
#
#         # 验证token
#         is_valid, payload, error_msg = TokenManager.verify_token(token)
#
#         if not is_valid:
#             return JsonResponse({
#                 'code': 401,
#                 'message': '认证失败',
#                 'detail': error_msg
#             }, status=401)
#
#         # 将用户信息添加到request对象中
#         request.user_info = payload.get('data', {})
#         request.token_payload = payload
#         request.token = token
#
#         return None
#
#     def process_response(self, request, response):
#         """
#         处理响应
#         """
#         if hasattr(response, 'headers'):
#             response.headers['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
#         return response
#
#     def process_exception(self, request, exception):
#         """
#         处理异常[1](@ref)
#         """
#         logger.error(f'JWT中间件异常: {str(exception)}')
#         return JsonResponse({
#             'code': 500,
#             'message': '服务器内部错误',
#             'detail': str(exception)
#         }, status=500)
#
#     def _is_no_auth_required(self, request):
#         """检查当前请求是否需要认证"""
#         path = request.path
#
#         for white_path in settings.NO_AUTH_REQUIRED:
#             if path.startswith(white_path):
#                 return True
#
#         if request.method == 'OPTIONS':
#             return True
#
#         return False

import re
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse
from utils.token import TokenManager, ResponseHelper


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """JWT认证中间件"""

    def process_request(self, request):
        """处理请求前的认证逻辑"""

        # 检查是否在白名单中
        if self._is_white_listed(request.path):
            return None

        # 获取Token
        token = TokenManager.get_token_from_request(request)
        if not token:
            return ResponseHelper.error('未提供认证Token', 401)

        # 验证Token
        is_valid, payload = TokenManager.verify_token(token)
        print("验证Token==={}".format(payload) )
        print("is_valid==={}".format(is_valid) )

        if not is_valid:
            return ResponseHelper.error(payload['error'], payload.get('code', 401))

        # 将用户信息添加到request对象中
        request.user_id = payload['user_id']
        request.username = payload['username']
        request.token_payload = payload
        print("request==={}".format(request) )

        return None

    def _is_white_listed(self, path):
        """检查路径是否在白名单中"""
        for white_path in settings.WHITE_LIST:
            if white_path.endswith('/') and path == white_path[:-1]:
                return True
            if re.match(white_path.replace('*', '.*'), path):
                return True
        return False

    def process_response(self, request, response):
        """处理响应"""
        return response