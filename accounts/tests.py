from django.test import TestCase
from django.urls import reverse

from .models import User


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jobseeker",
            password="test-password",
            role=User.Role.JOB_SEEKER,
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 302)

    def test_job_seeker_can_create_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "headline": "Python developer",
                "skills": "Python, Django, SQL",
                "education": "B.S. Computer Science | Georgia Tech | 2026",
                "work_experience": "Software Intern | Example Inc. | Summer 2025 | Built a recruiting dashboard",
                "links": "https://github.com/jobseeker\nhttps://linkedin.com/in/jobseeker",
            },
        )

        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.skills, ["Python", "Django", "SQL"])
        self.assertEqual(
            self.user.education,
            [
                {
                    "degree": "B.S. Computer Science",
                    "institution": "Georgia Tech",
                    "graduation_year": "2026",
                }
            ],
        )
        self.assertEqual(
            self.user.work_experience,
            [
                {
                    "title": "Software Intern",
                    "company": "Example Inc.",
                    "dates": "Summer 2025",
                    "description": "Built a recruiting dashboard",
                }
            ],
        )
        self.assertEqual(
            self.user.links,
            [
                {"url": "https://github.com/jobseeker"},
                {"url": "https://linkedin.com/in/jobseeker"},
            ],
        )

    def test_non_job_seekers_cannot_edit_profile(self):
        recruiter = User.objects.create_user(
            username="recruiter",
            password="test-password",
            role=User.Role.RECRUITER,
        )
        self.client.force_login(recruiter)

        response = self.client.get(reverse("accounts:profile"))

        self.assertRedirects(response, reverse("home.index"))


class RecruiterAccountTests(TestCase):
    def test_signup_can_create_recruiter(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "new-recruiter",
                "role": User.Role.RECRUITER,
                "password1": "strong-test-password-123",
                "password2": "strong-test-password-123",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertEqual(
            User.objects.get(username="new-recruiter").role,
            User.Role.RECRUITER,
        )

    def test_recruiter_login_redirects_to_dashboard(self):
        User.objects.create_user(
            username="recruiter",
            password="test-password",
            role=User.Role.RECRUITER,
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "recruiter", "password": "test-password"},
        )

        self.assertRedirects(response, reverse("jobs:dashboard"))

# Create your tests here.
