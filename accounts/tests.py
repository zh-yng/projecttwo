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
                "first_name": "Jamie",
                "middle_name": "Taylor",
                "last_name": "Doe",
                "headline": "Python developer",
                "skills": "Python, Django, SQL",
                "education": "B.S. Computer Science | Georgia Tech | 2026",
                "work_experience": "Software Intern | Example Inc. | Summer 2025 | Built a recruiting dashboard",
                "links": "https://github.com/jobseeker\nhttps://linkedin.com/in/jobseeker",
                "profile_visible_to_recruiters": "on",
                "show_headline": "on",
                "show_skills": "on",
                "show_education": "on",
                "show_work_experience": "on",
                "show_links": "on",
            },
        )

        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jamie")
        self.assertEqual(self.user.middle_name, "Taylor")
        self.assertEqual(self.user.last_name, "Doe")
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

    def test_job_seeker_can_save_privacy_settings(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Jamie",
                "last_name": "Doe",
                "headline": "Python developer",
                "skills": "Python, Django",
                "profile_visible_to_recruiters": "on",
                "show_skills": "on",
            },
        )

        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_visible_to_recruiters)
        self.assertTrue(self.user.show_skills)
        self.assertFalse(self.user.show_headline)
        self.assertFalse(self.user.show_education)
        self.assertFalse(self.user.show_work_experience)
        self.assertFalse(self.user.show_links)

    def test_profile_requires_first_and_last_name(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:profile"),
            {"first_name": "Jamie", "headline": "Python developer"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_username_is_prefilled_and_cannot_be_changed(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertContains(response, 'value="jobseeker"')
        self.assertContains(response, "disabled")
        self.client.post(
            reverse("accounts:profile"),
            {
                "username": "changed-username",
                "first_name": "Jamie",
                "last_name": "Doe",
            },
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "jobseeker")

    def test_full_name_includes_optional_middle_name(self):
        self.user.first_name = "Jamie"
        self.user.middle_name = "Taylor"
        self.user.last_name = "Doe"

        self.assertEqual(self.user.get_full_name(), "Jamie Taylor Doe")

    def test_recruiter_can_browse_visible_candidates(self):
        recruiter = User.objects.create_user(
            username="recruiter",
            password="test-password",
            role=User.Role.RECRUITER,
        )
        hidden_user = User.objects.create_user(
            username="hidden-jobseeker",
            password="test-password",
            role=User.Role.JOB_SEEKER,
            profile_visible_to_recruiters=False,
        )
        self.client.force_login(recruiter)

        response = self.client.get(reverse("accounts:recruiter_candidates"))

        self.assertContains(response, self.user.username)
        self.assertNotContains(response, hidden_user.username)

    def test_candidate_directory_hides_disabled_summary_fields(self):
        recruiter = User.objects.create_user(
            username="recruiter",
            password="test-password",
            role=User.Role.RECRUITER,
        )
        self.user.headline = "Private headline"
        self.user.skills = ["Private skill"]
        self.user.show_headline = False
        self.user.show_skills = False
        self.user.save()
        self.client.force_login(recruiter)

        response = self.client.get(reverse("accounts:recruiter_candidates"))

        self.assertNotContains(response, "Private headline")
        self.assertNotContains(response, "Private skill")

    def test_recruiter_profile_only_shows_allowed_fields(self):
        recruiter = User.objects.create_user(
            username="recruiter",
            password="test-password",
            role=User.Role.RECRUITER,
        )
        self.user.headline = "Visible headline"
        self.user.skills = ["Python"]
        self.user.links = [{"url": "https://example.com/private"}]
        self.user.show_links = False
        self.user.save()
        self.client.force_login(recruiter)

        response = self.client.get(
            reverse("accounts:recruiter_profile", args=[self.user.pk])
        )

        self.assertContains(response, "Visible headline")
        self.assertNotContains(response, "private")

    def test_recruiter_cannot_open_hidden_profile_directly(self):
        recruiter = User.objects.create_user(
            username="recruiter",
            password="test-password",
            role=User.Role.RECRUITER,
        )
        self.user.profile_visible_to_recruiters = False
        self.user.save(update_fields=("profile_visible_to_recruiters",))
        self.client.force_login(recruiter)

        response = self.client.get(
            reverse("accounts:recruiter_profile", args=[self.user.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_job_seeker_cannot_browse_recruiter_candidates(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:recruiter_candidates"))

        self.assertEqual(response.status_code, 404)

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
