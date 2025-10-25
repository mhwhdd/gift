from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardPagination(PageNumberPagination):
    """
    标准分页器 - 支持页码分页
    """
    page_size = 20  # 默认每页显示数量
    page_size_query_param = 'page_size'  # 每页数量参数
    page_query_param = 'page'  # 页码参数
    max_page_size = 100  # 每页最大显示数量

    def get_paginated_response(self, data):
        """
        自定义分页响应格式
        """
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'list': data,
                'pagination': {
                    'total_count': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'current_page': self.page.number,
                    'page_size': self.page_size,
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                }
            }
        })

class LargeResultsPagination(StandardPagination):
    """
    大数据集分页器
    """
    page_size = 100
    max_page_size = 500