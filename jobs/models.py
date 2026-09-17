from django.db import models
from django.conf import settings

# Create your models here.
class Job(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        FLAGGED = "FLAGGED", "Flagged"
        REMOVED = "REMOVED", "Removed"

    title = models.CharField(max_length=200)
    description=models.TextField()
    recruiter=models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="jobs_posted"
    )
    status=models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title