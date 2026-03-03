from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _

admin.site.site_header = 'Barey'
EMPTY_VALUE_DISPLAY = '<пусто>'

@admin.register(User)
class UserAdmin(UserAdmin):
    """Панель настройки пользователей"""
    list_display = ["username", "email", "first_name",
                    "last_name", "last_login"]
    search_fields = ["username", "email", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Личная информация"),
            {"fields":
                ("last_name", "first_name", "email",)}),
        (_("Permissions"),
            {"fields":
                ("is_active", "is_staff", "is_superuser",
                    "groups", "user_permissions")}),
        (_("Important dates"),
            {"fields":
                ("last_login", "date_joined")})
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "first_name",
                "last_name",
                "password1",
                "password2",
                "email",
                "work_phone",
                "department"
            ),
        }),
    )
    readonly_fields = ("last_login", "date_joined")