from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from .models import Tag, UserTagRelationship
from .relationshioser import UserTagRelationshipDetailSerializer,UserTagRelationshipListSerializer
from .relationshipfilters import UserTagRelationshipFilter

from .serializers import TagListSerializer, TagDetailSerializer
from .filters import TagFilter
from utils.pagination import StandardPagination, LargeResultsPagination
User = get_user_model()

class TagListAPIView(APIView):
    """
    标签列表接口 - 支持分页、过滤、搜索
    """
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TagFilter
    pagination_class = StandardPagination

    def get_paginator(self):
        """获取分页器实例"""
        paginator = self.pagination_class()
        return paginator

    def get(self, request):
        """
        获取标签列表 - 支持分页和多种过滤条件
        查询参数示例：
        - 分页: ?page=2&page_size=20
        - 过滤: ?tag_name=python&tag_type=skill
        - 搜索: ?search=编程
        - 组合: ?tag_type=skill&is_active=true&page=1&page_size=10
        """
        try:
            # 获取基础查询集
            queryset = Tag.objects.all()

            # 应用过滤器
            tag_filter = TagFilter(request.GET, queryset=queryset)
            filtered_queryset = tag_filter.qs

            # 排序处理
            ordering = request.GET.get('ordering', '-created_time')
            if ordering.lstrip('-') in ['tag_id', 'tag_name', 'created_time', 'tag_type']:
                filtered_queryset = filtered_queryset.order_by(ordering)

            # 分页处理
            paginator = self.get_paginator()
            page = paginator.paginate_queryset(filtered_queryset, request, view=self)

            if page is not None:
                serializer = TagListSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            # 如果没有分页，返回所有数据（不推荐用于大数据集）
            serializer = TagListSerializer(filtered_queryset, many=True)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'list': serializer.data,
                    'total_count': filtered_queryset.count()
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """创建新标签"""
        serializer = TagDetailSerializer(data=request.data)

        if serializer.is_valid():
            tag = serializer.save()
            return Response({
                'code': 201,
                'message': '标签创建成功',
                'data': TagDetailSerializer(tag).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'code': 400,
                'message': '数据验证失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class TagDetailAPIView(APIView):
    """
    标签详情接口
    """

    def get_object(self, tag_id):
        """获取标签对象，包含异常处理"""
        return get_object_or_404(Tag, tag_id=tag_id)

    def get(self, request, tag_id):
        """获取单个标签详情"""
        try:
            tag = self.get_object(tag_id)
            serializer = TagDetailSerializer(tag)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 404,
                'message': '标签不存在'
            }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, tag_id):
        """全量更新标签信息"""
        try:
            tag = self.get_object(tag_id)
            serializer = TagDetailSerializer(instance=tag, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 200,
                    'message': '标签更新成功',
                    'data': serializer.data
                })
            else:
                return Response({
                    'code': 400,
                    'message': '数据验证失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'code': 404,
                'message': '标签不存在'
            }, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, tag_id):
        """部分更新标签信息"""
        try:
            tag = self.get_object(tag_id)
            serializer = TagDetailSerializer(instance=tag, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 200,
                    'message': '标签部分更新成功',
                    'data': serializer.data
                })
            else:
                return Response({
                    'code': 400,
                    'message': '数据验证失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'code': 404,
                'message': '标签不存在'
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, tag_id):
        """软删除标签"""
        try:
            tag = self.get_object(tag_id)

            if tag.tag_type == 'system':
                return Response({
                    'code': 403,
                    'message': '系统标签不允许删除'
                }, status=status.HTTP_403_FORBIDDEN)

            tag.is_active = False
            tag.save()

            return Response({
                'code': 200,
                'message': '标签删除成功'
            })

        except Exception as e:
            return Response({
                'code': 404,
                'message': '标签不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class UserTagRelationshipListCreateView(APIView):
    """
    用户标签关联列表和创建视图（支持分页和过滤）
    GET: 获取分页和过滤后的用户标签关联列表
    POST: 创建新的用户标签关联
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserTagRelationshipFilter
    search_fields = ['relation_description', 'user__username', 'tag__name']
    ordering_fields = ['relation_time', 'weight', 'user__username']
    ordering = ['-relation_time']

    def get_queryset(self):
        """获取基础查询集"""
        queryset = UserTagRelationship.objects.all()

        # 基础过滤条件
        user_id = self.request.query_params.get('user_id')
        tag_id = self.request.query_params.get('tag_id')
        status_param = self.request.query_params.get('status')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if tag_id:
            queryset = queryset.filter(tag_id=tag_id)
        if status_param is not None:
            status_bool = status_param.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(status=status_bool)

        return queryset

    def get(self, request):
        """获取分页和过滤后的列表"""
        # 判断是否使用大数据集分页
        use_large_pagination = request.query_params.get('large') == 'true'
        pagination_class = LargeResultsPagination if use_large_pagination else StandardPagination

        # 应用过滤
        queryset = self.get_queryset()
        filtered_queryset = UserTagRelationshipFilter(request.GET, queryset=queryset).qs

        # 应用搜索和排序
        for backend in list(self.filter_backends):
            if hasattr(backend, 'filter_queryset'):
                filtered_queryset = backend().filter_queryset(request, filtered_queryset, self)

        # 应用分页
        paginator = pagination_class()
        page = paginator.paginate_queryset(filtered_queryset, request, view=self)

        if page is not None:
            serializer = UserTagRelationshipListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # 如果没有分页，返回所有结果
        serializer = UserTagRelationshipListSerializer(filtered_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """创建新的关联"""
        serializer = UserTagRelationshipDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '用户标签关联创建成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'message': '创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserTagRelationshipDetailView(APIView):
    """
    用户标签关联详情、更新和删除视图
    """

    def get_object(self, relation_id):
        """获取关联对象或返回404"""
        return get_object_or_404(UserTagRelationship, relation_id=relation_id)

    def get(self, request, relation_id):
        """获取详情"""
        relationship = self.get_object(relation_id)
        serializer = UserTagRelationshipDetailSerializer(relationship)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, relation_id):
        """更新关联信息"""
        relationship = self.get_object(relation_id)
        serializer = UserTagRelationshipDetailSerializer(
            relationship,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '用户标签关联更新成功',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, relation_id):
        """删除关联"""
        relationship = self.get_object(relation_id)
        relationship.delete()
        return Response({
            'message': '用户标签关联删除成功'
        }, status=status.HTTP_204_NO_CONTENT)


class UserTagsView(APIView):
    """
    获取用户的所有标签关联（支持分页和过滤）
    """

    def get(self, request, user_id):
        """获取用户的所有标签"""
        # 验证用户是否存在
        user = get_object_or_404(User, id=user_id)

        user_relationships = UserTagRelationship.objects.filter(
            user_id=user_id,
            status=True
        )

        # 应用过滤
        tag_filter = UserTagRelationshipFilter(
            request.GET,
            queryset=user_relationships
        )
        filtered_queryset = tag_filter.qs

        # 应用分页
        paginator = StandardPagination()
        page = paginator.paginate_queryset(filtered_queryset, request, view=self)

        if page is not None:
            serializer = UserTagRelationshipListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = UserTagRelationshipListSerializer(filtered_queryset, many=True)
        return Response({
            'user_id': user_id,
            'username': user.username,
            'count': filtered_queryset.count(),
            'tags': serializer.data
        }, status=status.HTTP_200_OK)


class TagUsersView(APIView):
    """
    获取标签的所有用户关联（支持分页和过滤）
    """

    def get(self, request, tag_id):
        """获取标签的所有用户"""
        # 验证标签是否存在
        tag = get_object_or_404(Tag, id=tag_id)

        tag_relationships = UserTagRelationship.objects.filter(
            tag_id=tag_id,
            status=True
        )

        # 应用过滤
        tag_filter = UserTagRelationshipFilter(
            request.GET,
            queryset=tag_relationships
        )
        filtered_queryset = tag_filter.qs

        # 应用分页
        paginator = StandardPagination()
        page = paginator.paginate_queryset(filtered_queryset, request, view=self)

        if page is not None:
            serializer = UserTagRelationshipListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = UserTagRelationshipListSerializer(filtered_queryset, many=True)
        return Response({
            'tag_id': tag_id,
            'tag_name': tag.name,
            'count': filtered_queryset.count(),
            'users': serializer.data
        }, status=status.HTTP_200_OK)