from django.contrib import admin
from .models import Job 

# Register your models here.
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "recruiter", "status", "created_at"]
    list_filter = ["status"]
    actions = ["mark_removed"]

    @admin.action(description="Remove selected job posts")
    def mark_removed(self, request, queryset): 
        updated=queryset.update(status=Job.Status.REMOVED)
        self.message_user(request, f"Removed {updated} job post(s).")

    @admin.action(description="Flag selected job posts")
    def mark_flagged(self, request, queryset):
        updated = queryset.update(status=Job.Status.FLAGGED)
        self.message_user(request, f"Flagged {updated} job post(s).")

    @admin.action(description="Restore selected job posts")
    def mark_flagged(self, request, queryset):
        updated = queryset.update(status=Job.Status.ACTIVE)
        self.message_user(request, f"Restored {updated} job post(s).")
    