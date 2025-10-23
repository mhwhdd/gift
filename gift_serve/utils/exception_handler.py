from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    自定义异常处理，统一返回格式
    """
    # 调用DRF默认异常处理
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'code': response.status_code,
            'success': False,
            'message': str(exc),
            'data': None
        }

    return response