'''from django.test import TestCase, Client
from accounts.models import Profile, User
from django.urls import reverse

from ...models import Category, Post


class TestBlogView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(
            email="test@gmail.com", password="@ASdf123"
        )

        cls.profile = Profile.objects.get(user=cls.user)

        cls.profile.first_name = "test"
        cls.profile.last_name = "test"
        cls.profile.save()
        cls.category = Category.objects.create(
            name="test",
        )
        cls.post = Post.objects.create(
            title="test",
            content="test content",
            author=cls.profile,
            category=cls.category,
            status=True,
        )

    def test_post_list_successfully_response(self):
        self.client.force_login(self.user)
        url = reverse("blog:post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_list.html")

    def test_post_detail_logged_in(self):
        self.client.force_login(self.user)
        url = reverse("blog:post-detail", kwargs={"pk": self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_detail_not_logged_in(self):
        self.client.logout()
        url = reverse("blog:post-detail", kwargs={"pk": self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_create_successfully(self):
        self.client.force_login(self.user)

        url = reverse("blog:post-create")

        form_data = {
            "title": "new test",
            "content": "test content",
            "category": self.category.id,
            "status": True,
        }

        response = self.client.post(url, form_data)

        post = Post.objects.get(title="new test")
        self.assertTrue(Post.objects.filter(title="new test").exists())
        self.assertRedirects(response, reverse("blog:post-list"))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(post.author, self.profile)

    def test_post_create_not_logged_in(self):
        self.client.logout()
        url = reverse("blog:post-create")
        form_data = {
            "title": "not logged in test",
            "content": "test content",
            "category": self.category.id,
        }
        response = self.client.post(url, form_data)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('blog:post-create')}",
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Post.objects.filter(title="not logged in test").exists()
        )

    def test_post_update_successfully(self):
        self.client.force_login(self.user)
        url = reverse("blog:post-update", kwargs={"pk": self.post.id})
        form_data = {
            "title": "updated test",
            "content": "test content",
            "category": self.category.id,
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:post-list"))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "updated test")

    def test_post_update_not_logged_in(self):
        self.client.logout()
        url = reverse("blog:post-update", kwargs={"pk": self.post.pk})
        form_data = {
            "title": "updated test not logged in",
            "content": "test content",
            "category": self.category.id,
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.title, "updated test not logged in")
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={url}"
        )

    def test_post_update_logged_in_invalid_data(self):
        self.client.force_login(self.user)
        url = reverse("blog:post-update", kwargs={"pk": self.post.pk})
        form_data = {
            "title": "updated test invalid data",
            "content": "test content",
            "category": "hello",
        }
        response = self.client.post(url, form_data)
        old_title = self.post.title
        old_category = self.post.category
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, old_title)
        self.assertEqual(self.post.category, old_category)

    def test_post_delete_successfully(self):
        self.client.force_login(self.user)
        url = reverse("blog:post-delete", kwargs={"pk": self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

        self.assertRedirects(response, reverse("blog:post-list"))

    def test_post_delete_not_logged_in(self):
        self.client.logout()
        url = reverse("blog:post-delete", kwargs={"pk": self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={url}"
        )
'''