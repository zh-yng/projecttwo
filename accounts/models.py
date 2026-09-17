from django.db import models
from django.contrib.auth.models import AbstractUser 
#retain default fields while making custom user model 

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = "JOB_SEEKER", "Job Seeker"
        RECRUITER = "RECRUITER", "Recruiter"
        ADMIN = "ADMIN", "Administrator"

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
