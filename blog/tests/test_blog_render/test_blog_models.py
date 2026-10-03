from django.test import TestCase

from accounts.models import User, Profile
from blog.models import Post, Category, Comment


class TestBlogModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="@Asdf123"
        )

        self.profile = Profile.objects.get(user=self.user)

        self.category = Category.objects.create(
            name="test",
        )
        self.post = Post.objects.create(
            title="test",
            content="test content",
            author=self.profile,
            category=self.category,
            status=True,
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

    def test_comment_model(self):
        comment = Comment.objects.create(
            content="test content",
            author=self.profile,
            post=self.post,
        )
        self.assertTrue(isinstance(comment, Comment))

    def test_create_reply(self):
        comment = Comment.objects.create(
            content="Parent comment",
            author=self.profile,
            post=self.post,
        )

        reply = Comment.objects.create(
            content="Reply comment",
            author=self.profile,
            post=self.post,
            parent=comment,
        )

        self.assertEqual(reply.parent, comment)
        self.assertEqual(reply.parent_id, comment.id)

    def test_replies_relation(self):
        comment = Comment.objects.create(
            content="Parent comment",
            author=self.profile,
            post=self.post,
        )

        reply = Comment.objects.create(
            content="Reply comment",
            author=self.profile,
            post=self.post,
            parent=comment,
        )

        self.assertIn(reply, comment.replies.all())

    def test_comment_without_parent_is_main_comment(self):
        comment = Comment.objects.create(
            content="Main comment",
            author=self.profile,
            post=self.post,
        )

        self.assertIsNone(comment.parent_id)
        self.assertEqual(comment.replies.count(), 0)
