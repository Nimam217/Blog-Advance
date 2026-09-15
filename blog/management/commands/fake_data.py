from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User, Profile
from blog.models import Post, Category
import random

category_list = [
    "IT",
    "TECH",
    "SPORT",
    "MUSIC",
]


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__()
        self.fake = Faker()

    def handle(self, *args, **options):
        user = User.objects.create_user(
            email=self.fake.name(), password="@ASDF!@#"
        )
        profile = Profile.objects.get(user=user)
        profile.first_name = str(self.fake.first_name())
        profile.last_name = str(self.fake.last_name())
        profile.description = str(self.fake.paragraph(nb_sentences=3))
        profile.save()

        for name in category_list:
            Category.objects.get_or_create(name=name)

        for _ in range(10):
            Post.objects.create(
                author=profile,
                title=str(self.fake.sentence(nb_words=3)),
                content=str(self.fake.paragraph(nb_sentences=3)),
                status=random.choice([True, False]),
                category=Category.objects.get(
                    name=random.choice(category_list)
                ),
            )
