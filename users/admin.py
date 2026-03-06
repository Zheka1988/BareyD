from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _

admin.site.site_header = 'Barey'
admin.site.empty_value_display = '<пусто>'


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name",
                    "last_name", "last_login"]
    list_display_links = ["username"]
    search_fields = ["username", "email", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Личная информация"),
            {"fields":
                ("last_name", "first_name", "email",)}),
        (_("Права доступа"),
            {"fields":
                ("is_active", "is_staff", "is_superuser",
                    "groups", "user_permissions")}),
        (_("Важные даты"),
            {"fields":
                ("last_login", "date_joined")}),
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
            ),
        }),
    )
    readonly_fields = ("last_login", "date_joined")
