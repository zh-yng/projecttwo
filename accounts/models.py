from django.db import models
from django.contrib.auth.models import AbstractUser 
#retain default fields while making custom user model 

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = "JOB_SEEKER", "Job Seeker"
        RECRUITER = "RECRUITER", "Recruiter"
        ADMIN = "ADMIN", "Administrator"

    class EducationType(models.TextChoices):
        HIGH_SCHOOL = "HIGH_SCHOOL", "High School"
        BACHELORS = "BACHELORS", "Bachelors"
        MASTERS = "MASTERS", "Masters"
        PHD = "PHD", "PhD"

    class WorkExperienceType(models.TextChoices):
        INTERN = "INTERN", "Intern"
        ENTRY_LEVEL = "ENTRY_LEVEL", "Entry-Level"
        MID_LEVEL = "MID_LEVEL", "Mid-Level"
        SENIOR = "SENIOR", "Senior"
        LEAD = "LEAD", "Lead"

    headline=models.CharField(max_length=255, blank=True, null=True)
    skills=models.JSONField(blank=True, null=True)

    # JSON field. remember to specify the structure (i.e. institution + education type)!!!
    education=models.JSONField(blank=True, null=True)

    # same goes for this one. a todo is to specify structure of each entry
    work_experience=models.JSONField(blank=True, null=True)
    links=models.JSONField(blank=True, null=True)

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.JOB_SEEKER,
    )
    #admin role is the superuser 
    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN: 
            self.is_staff = True 
            self.is_superuser = True 
        super().save(*args, **kwargs)

    def __str__(self):
        return f" {self.username} ({self.get_role_display()})"
