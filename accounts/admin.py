from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Profile

# Register your models here.


class CustomUserAdmin(UserAdmin):

    model = User
    list_display = ("email", "is_superuser", "is_active",)
    list_filter = ("email", "is_superuser", "is_active",)
    fieldsets = (
        ("Authenticate", {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active","is_superuser")}),
        ("group permissions", {"fields": ("groups", "user_permissions")}),
        ("important fields", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        ("create user", {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active","is_superuser",
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name")
    search_fields = ("user__email", "first_name", "last_name")
    ordering = ["create_date"]
    empty_value_display = "-empty-"


admin.site.register(Profile,ProfileAdmin)
admin.site.register(User, CustomUserAdmin)