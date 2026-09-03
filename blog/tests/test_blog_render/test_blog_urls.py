from django.test import TestCase
from django.urls import resolve, reverse

from blog.views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
)


class TestBlogUrls(TestCase):

    def test_post_list_resolve(self):
        url = reverse("blog:post-list")
        self.assertEqual(resolve(url).func.view_class, PostListView)

    def test_post_detail_resolve(self):
        url = reverse("blog:post-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, PostDetailView)

    def test_post_create_resolve(self):
        url = reverse("blog:post-create")
        self.assertEqual(resolve(url).func.view_class, PostCreateView)

    def test_post_delete_resolve(self):
        url = reverse("blog:post-delete", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, PostDeleteView)

    def test_post_update_resolve(self):
        url = reverse("blog:post-update", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, PostUpdateView)
