from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from utils.token_utils import JWTTokenManager
import re


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    JWT认证中间件
    支持白名单配置和灵活的token获取方式
    """

    def process_request(self, request):
        """
        处理请求，进行JWT认证
        """
        # 获取请求路径
        path = request.path

        # 白名单路径（不需要认证的接口）
        white_list = self.get_white_list()
        print("99=====white_list===={}".format(white_list))
        print("99=====white_list===={}".format(self.is_white_list_path(path, white_list)))
        # 检查是否在白名单中
        if self.is_white_list_path(path, white_list):
            return None  # 白名单路径，跳过认证

        # 从请求中获取token
        token = JWTTokenManager.get_token_from_request(request)

        if not token:
            return JsonResponse({
                'code': 401,
                'success': False,
                'message': '未提供认证Token，请登录后访问',
                'data': None
            }, status=401)

        # 验证token
        is_valid, result = JWTTokenManager.verify_token(token)

        if not is_valid:
            return JsonResponse({
                'code': 401,
                'success': False,
                'message': result,  # 错误信息
                'data': None
            }, status=401)

        # token验证成功，将用户信息添加到request对象中
        request.user_info = result
        request.token = token
        return None

    def get_white_list(self):
        """
        获取白名单配置，可以从settings中读取或使用默认值
        """

        from django.conf import settings
        # print("get_white_list============{}".format()
        # 默认白名单
        # default_white_list = [
        #     '/api/login/',
        #     '/api/register/',
        #     '/admin/',
        #     '/api/docs/',
        #     '/health/',
        #     r'^/media/',  # 媒体文件
        #     r'^/static/',  # 静态文件
        # ]

        # 从settings中获取自定义白名单
        custom_white_list = settings.JWT_CONFIG['WHITE_LIST']
        print("custom_white_list===={}".format(custom_white_list))
        return custom_white_list  #+default_white_list

    def is_white_list_path(self, path, white_list):
        """
        检查路径是否在白名单中
        """
        for pattern in white_list:
            # 如果是正则表达式
            if pattern.startswith('^'):
                if re.match(pattern, path):
                    return True
            # 如果是精确匹配
            elif path == pattern:
                return True
            # 如果是前缀匹配
            elif path.startswith(pattern.rstrip('*')):
                return True

        return False

    def process_response(self, request, response):
        """
        处理响应，可以在这里添加响应头等
        """
        # 可以在这里添加Token刷新逻辑等
        return response