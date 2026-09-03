from django.contrib import admin
from .models import Post, Category


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "image",
        "title",
        "author",
        "status",
        "created_at",
        "updated_at",
        "category",
    )
    ordering = ("-created_at",)
    search_fields = ("title",)
    list_filter = ("status",)


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
