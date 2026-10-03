from django.contrib import admin
from . models import  User
from django.contrib.auth.admin import UserAdmin

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
        "role",
        "is_active",
        "is_staff",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (
        ("Helpdesk role", {"fields": ("role",)}),
    )

  # Create accounts through your API endpoints.
  # It disables creation of user through admin panel
    def has_add_permission(self, request):
        return False