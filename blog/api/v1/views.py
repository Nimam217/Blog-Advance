from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework import viewsets
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    PostSerializer,
    CategorySerializer,
    CommentSerializer,
)

from ...models import (
    Post,
    Category,
    Comment,
)

from .paginations import (
    DefaultPagination,
    DefaultPaginationComments,
    DefaultPaginationCategory,
)


class PostModelViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsOwnerOrReadOnly,
    ]

    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=True)

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        "category": ["exact", "in"],
        "author": ["exact"],
    }

    search_fields = [
        "title",
        "content",
    ]

    ordering_fields = [
        "created_at",
    ]

    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.urlencode()
        cache_key = f"post_list:{query_params}"

        cache_data = cache.get(cache_key)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:

            if cache_data is not None:
                return self.get_paginated_response(cache_data)

            serializer = self.get_serializer(page, many=True)

            cache.set(
                cache_key,
                serializer.data,
                timeout=20 * 60,
            )

            return self.get_paginated_response(serializer.data)

        if cache_data is not None:
            return Response(cache_data)

        serializer = self.get_serializer(queryset, many=True)

        cache.set(
            cache_key,
            serializer.data,
            timeout=20 * 60,
        )

        return Response(serializer.data)


class CategoryModelViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    serializer_class = CategorySerializer
    pagination_class = DefaultPaginationCategory

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page_number = request.query_params.get("page", 1)
        cache_key = f"category_list:{page_number}"
        cache_data = cache.get(cache_key)

        page = self.paginate_queryset(queryset)
        if page is not None:
            if cache_data is not None:
                return self.get_paginated_response(cache_data)
            serializer = self.get_serializer(page, many=True)
            cache.set(cache_key, serializer.data, timeout=20 * 60)
            return self.get_paginated_response(serializer.data)
        if cache_data is not None:
            return Response(cache_data)
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=20 * 60)
        return Response(serializer.data)


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related(
        "author",
        "post",
        "parent",
    ).filter(post__status=True, status=True)

    serializer_class = CommentSerializer

    permission_classes = [
        IsAuthenticated,
        IsOwnerOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        "post": ["exact"],
        "author": ["exact"],
        "parent": ["exact"],
    }

    search_fields = [
        "content",
        "name",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
    ]

    pagination_class = DefaultPaginationComments
