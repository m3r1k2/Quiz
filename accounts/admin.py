from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональна інформація", {"fields": ("email", "bio", "avatar")}),
        ("Ролі та права", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    def get_readonly_fields(self, request, obj=None):

        if not request.user.is_superuser:
            return self.readonly_fields + ("role",)
        return self.readonly_fields