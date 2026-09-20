from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import User 

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "role", "is_active"]
    list_filter = ["role", "is_active"]
    actions = ["deactivate_users", "reactivate_users"]
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ["role"]}),
        (
            "Job seeker profile",
            {"fields": ["headline", "skills", "education", "work_experience", "links"]},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (("Role", {"fields": ["role"]}),)

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f"Deactivated {updated} user(s).")

    @admin.action(description="Reactivate selected users")
    def reactivate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Reactivated {updated} user(s).")
