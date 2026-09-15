from rest_framework.permissions import (
    IsAuthenticated,

)

from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)

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

from .paginations import DefaultPagination, DefaultPaginationComments


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


class CategoryModelViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    serializer_class = CategorySerializer


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related(
        "author",
        "post",
        "parent",
    )

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
