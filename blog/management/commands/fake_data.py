from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User, Profile
from blog.models import Post, Category, Comment
import random

category_list = [
    "IT",
    "TECH",
    "SPORT",
    "MUSIC",
]


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        user = User.objects.create_user(
            email=self.fake.email(),
            password="@ASDF!@#",
        )

        profile = Profile.objects.get(user=user)

        profile.first_name = self.fake.first_name()
        profile.last_name = self.fake.last_name()
        profile.description = self.fake.paragraph(nb_sentences=3)
        profile.save()

        for name in category_list:
            Category.objects.get_or_create(name=name)

        for _ in range(10):
            post = Post.objects.create(
                author=profile,
                title=self.fake.sentence(nb_words=3),
                content=self.fake.paragraph(nb_sentences=3),
                status=random.choice([True, False]),
                category=Category.objects.get(
                    name=random.choice(category_list)
                ),
            )

            for _ in range(3):
                comment = Comment.objects.create(
                    author=profile,
                    content=self.fake.paragraph(nb_sentences=3),
                    post=post,
                    status=random.choice([True, False]),
                )

                create_reply = random.choice([True, False])

                if create_reply:
                    Comment.objects.create(
                        author=profile,
                        content=self.fake.paragraph(nb_sentences=3),
                        post=post,
                        parent=comment,
                        status=random.choice([True, False]),
                    )
