def get_current_user(request):
    """
    从request中获取当前用户信息
    """
    return getattr(request, 'user_info', None)

def login_required(view_func):
    """
    登录验证装饰器，用于函数视图
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user_info') or not request.user_info:
            from django.http import JsonResponse
            return JsonResponse({
                'code': 401,
                'success': False,
                'message': '请先登录',
                'data': None
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper