from rest_framework.views import exception_handler
from rest_framework.response import Response
from utils.token import ResponseHelper


def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 401:
            return ResponseHelper.error('身份验证失败', 401)
        elif response.status_code == 403:
            return ResponseHelper.error('权限不足', 403)
        elif response.status_code == 404:
            return ResponseHelper.error('资源不存在', 404)
        elif response.status_code >= 500:
            return ResponseHelper.error('服务器内部错误', 500)

    return response