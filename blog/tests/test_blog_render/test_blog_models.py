'''from django.test import TestCase

from accounts.models import User, Profile
from blog.models import Post, Category


class TestBlogModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="@Asdf123"
        )

        self.profile = Profile.objects.get(user=self.user)

        self.category = Category.objects.create(
            name="test",
        )

    def test_post_model(self):
        post = Post.objects.create(
            title="test",
            content="test content",
            author=self.profile,
            category=self.category,
            status=True,
        )
        self.assertTrue(isinstance(post, Post))

    def test_category_model(self):
        category = Category.objects.create(name="test")
        self.assertTrue(isinstance(category, Category))
'''