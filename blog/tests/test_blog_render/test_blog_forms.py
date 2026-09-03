'''from django.test import TestCase, Client
from ...forms import PostForm
from accounts.models import Profile, User
from ...models import Category


class TestBlogForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(
            email="testform@gmail.com", password="@ASDf123"
        )

        cls.profile = Profile.objects.get(user=cls.user)
        cls.category = Category.objects.create(
            name="test",
        )

    def test_form_post_valid(self):

        form_data = {
            "title": "new test",
            "content": "test content",
            "category": self.category.id,
            "status": True,
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_post_invalid(self):
        form_data = {
            "content": "test content",
            "category": self.category.id,
            "status": True,
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
'''