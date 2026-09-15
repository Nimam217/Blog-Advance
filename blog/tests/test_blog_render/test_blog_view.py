from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Profile, User
from ...models import Category, Post, Comment


class TestBlogView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        cls.user = User.objects.create_user(
            email="test@gmail.com",
            password="@ASdf123",
        )

        cls.profile = Profile.objects.get(user=cls.user)

        cls.profile.first_name = "test"
        cls.profile.last_name = "test"
        cls.profile.save()

        cls.other_user = User.objects.create_user(
            email="other@gmail.com",
            password="@ASdf123",
        )

        cls.other_profile = Profile.objects.get(user=cls.other_user)

        cls.other_profile.first_name = "other"
        cls.other_profile.last_name = "user"
        cls.other_profile.save()

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

        cls.comment = Comment.objects.create(
            name=cls.profile.get_full_name(),
            content="test comment",
            author=cls.profile,
            post=cls.post,
        )

        cls.reply = Comment.objects.create(
            name=cls.other_profile.get_full_name(),
            content="test reply",
            author=cls.other_profile,
            post=cls.post,
            parent=cls.comment,
        )

    # =========================
    # Post List
    # =========================

    def test_post_list_successfully_response(self):
        self.client.force_login(self.user)

        url = reverse("blog:post-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "blog/post_list.html",
        )

        self.assertIn(
            self.post,
            response.context["posts"],
        )

    # =========================
    # Post Detail
    # =========================

    def test_post_detail_logged_in(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "blog/post_detail.html",
        )

        self.assertEqual(
            response.context["post"],
            self.post,
        )

    def test_post_detail_not_logged_in(self):
        self.client.logout()

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_post_detail_contains_comments(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        response = self.client.get(url)

        comments = response.context["comments"]

        self.assertIn(
            self.comment,
            comments,
        )

        self.assertNotIn(
            self.reply,
            comments,
        )

    # =========================
    # Post Create
    # =========================

    def test_post_create_successfully(self):
        self.client.force_login(self.user)

        url = reverse("blog:post-create")

        form_data = {
            "title": "new test",
            "content": "test content",
            "category": self.category.id,
            "status": True,
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            reverse("blog:post-list"),
        )

        post = Post.objects.get(title="new test")

        self.assertEqual(
            post.author,
            self.profile,
        )

    def test_post_create_not_logged_in(self):
        self.client.logout()

        url = reverse("blog:post-create")

        form_data = {
            "title": "not logged in test",
            "content": "test content",
            "category": self.category.id,
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={url}",
        )

        self.assertFalse(
            Post.objects.filter(title="not logged in test").exists()
        )

    # =========================
    # Post Update
    # =========================

    def test_post_update_successfully(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-update",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "title": "updated test",
            "content": "test content",
            "category": self.category.id,
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            reverse("blog:post-list"),
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.title,
            "updated test",
        )

    def test_post_update_not_logged_in(self):
        self.client.logout()

        url = reverse(
            "blog:post-update",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "title": "updated test not logged in",
            "content": "test content",
            "category": self.category.id,
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={url}",
        )

        self.post.refresh_from_db()

        self.assertNotEqual(
            self.post.title,
            "updated test not logged in",
        )

    def test_post_update_logged_in_invalid_data(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-update",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "title": "updated test invalid data",
            "content": "test content",
            "category": "hello",
        }

        old_title = self.post.title
        old_category = self.post.category

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 200)

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.title,
            old_title,
        )

        self.assertEqual(
            self.post.category,
            old_category,
        )

    # =========================
    # Post Delete
    # =========================

    def test_post_delete_successfully(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-delete",
            kwargs={"pk": self.post.pk},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

        self.assertRedirects(
            response,
            reverse("blog:post-list"),
        )

    def test_post_delete_not_logged_in(self):
        self.client.logout()

        url = reverse(
            "blog:post-delete",
            kwargs={"pk": self.post.pk},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={url}",
        )

    # =========================
    # Comment Create
    # =========================

    def test_comment_create_successfully(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "action": "create",
            "content": "new comment",
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            url,
        )

        comment = Comment.objects.get(
            content="new comment",
        )

        self.assertEqual(
            comment.author,
            self.profile,
        )

        self.assertEqual(
            comment.post,
            self.post,
        )

        self.assertEqual(
            comment.name,
            self.profile.get_full_name(),
        )

        self.assertIsNone(
            comment.parent,
        )

    def test_comment_create_not_logged_in(self):
        self.client.logout()

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "action": "create",
            "content": "not logged in comment",
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            Comment.objects.filter(content="not logged in comment").exists()
        )

    # =========================
    # Comment Reply
    # =========================

    def test_comment_reply_successfully(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "action": "create",
            "content": "new reply",
            "parent": self.comment.pk,
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        reply = Comment.objects.get(
            content="new reply",
        )

        self.assertEqual(
            reply.parent,
            self.comment,
        )

        self.assertEqual(
            reply.post,
            self.post,
        )

        self.assertIn(
            reply,
            self.comment.replies.all(),
        )

    # =========================
    # Comment Update
    # =========================

    def test_comment_update_successfully(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "action": "update",
            "comment_id": self.comment.pk,
            "content": "updated comment",
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            url,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.content,
            "updated comment",
        )

    def test_comment_update_other_user(self):
        self.client.force_login(self.other_user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "action": "update",
            "comment_id": self.comment.pk,
            "content": "hacked comment",
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.content,
            "test comment",
        )

    # =========================
    # Comment Delete
    # =========================

    def test_comment_delete_successfully(self):
        self.client.force_login(self.user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "action": "delete",
            "comment_id": self.comment.pk,
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            url,
        )

        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_comment_delete_other_user(self):
        self.client.force_login(self.other_user)

        url = reverse(
            "blog:post-detail",
            kwargs={"pk": self.post.pk},
        )

        form_data = {
            "action": "delete",
            "comment_id": self.comment.pk,
        }

        response = self.client.post(
            url,
            form_data,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())
