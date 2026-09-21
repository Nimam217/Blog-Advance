from django.contrib import admin
from .models import Post, Category, Comment


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
    search_fields = ("title", "author", "category")
    list_filter = ("status", "author", "category")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "status",
        "created_at",
        "updated_at",
        "parent",
        "post",
    )
    ordering = ("-created_at",)
    search_fields = ("author", "name", "post")
    list_filter = ("status", "author", "parent", "post")


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
