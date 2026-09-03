from django.db import models

# get user and create object


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.BooleanField(default=False)
    author = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(blank=True, null=True, upload_to="images/")
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.title

    def get_snippets(self):
        return self.content[0:5]


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
