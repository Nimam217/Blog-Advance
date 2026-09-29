import pytest
from django.urls import resolve, reverse

from blog.api.v1.views import (
    PostModelViewSet,
    CategoryModelViewSet,
    CommentModelViewSet,
)


@pytest.mark.django_db
class TestAPIURLs:

    def test_post_list_url(self):
        url = reverse("blog:api_v1:post-list")

        assert url == "/blog/api/v1/post/"

        match = resolve(url)

        assert match.func.cls == PostModelViewSet
        assert match.url_name == "post-list"

    def test_post_detail_url(self):
        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": 1},
        )

        assert url == "/blog/api/v1/post/1/"

        match = resolve(url)

        assert match.func.cls == PostModelViewSet
        assert match.url_name == "post-detail"

    def test_category_list_url(self):
        url = reverse("blog:api_v1:category-list")

        assert url == "/blog/api/v1/category/"

        match = resolve(url)

        assert match.func.cls == CategoryModelViewSet
        assert match.url_name == "category-list"

    def test_category_detail_url(self):
        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": 1},
        )

        assert url == "/blog/api/v1/category/1/"

        match = resolve(url)

        assert match.func.cls == CategoryModelViewSet
        assert match.url_name == "category-detail"

    def test_comment_list_url(self):
        url = reverse("blog:api_v1:comment-api-list")

        assert url == "/blog/api/v1/comment/"

        match = resolve(url)

        assert match.func.cls == CommentModelViewSet
        assert match.url_name == "comment-api-list"

    def test_comment_detail_url(self):
        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": 1},
        )

        assert url == "/blog/api/v1/comment/1/"

        match = resolve(url)

        assert match.func.cls == CommentModelViewSet
        assert match.url_name == "comment-api-detail"
