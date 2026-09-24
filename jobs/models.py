from django.db import models
from django.conf import settings

# Create your models here.
class Job(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        FLAGGED = "FLAGGED", "Flagged"
        REMOVED = "REMOVED", "Removed"
        CLOSED = "CLOSED", "Closed"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full-time"
        PART_TIME = "PART_TIME", "Part-time"
        CONTRACT = "CONTRACT", "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    skills = models.TextField(blank=True)
    closing_date = models.DateField(blank=True, null=True)
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs_posted"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title