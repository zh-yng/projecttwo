from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Application, Job


class JobViewTests(TestCase):
	def setUp(self):
		self.recruiter = User.objects.create_user(
			username="recruiter",
			password="test-password",
			role=User.Role.RECRUITER,
		)
		self.other_recruiter = User.objects.create_user(
			username="other-recruiter",
			password="test-password",
			role=User.Role.RECRUITER,
		)
		self.job = Job.objects.create(
			title="Backend Engineer",
			description="Build recruiting tools.",
			recruiter=self.recruiter,
		)

	def test_recruiter_can_create_job(self):
		self.client.force_login(self.recruiter)

		response = self.client.post(
			reverse("jobs:create"),
			{
				"title": "Frontend Engineer",
				"description": "Build a great interface.",
				"location": "Atlanta",
				"is_remote": "on",
				"employment_type": Job.EmploymentType.FULL_TIME,
				"salary_min": "90000",
				"salary_max": "120000",
				"skills": "Django, JavaScript",
			},
		)

		self.assertRedirects(response, reverse("jobs:dashboard"))
		created_job = Job.objects.get(title="Frontend Engineer")
		self.assertEqual(created_job.recruiter, self.recruiter)
		self.assertTrue(created_job.is_remote)

	def test_job_seeker_cannot_create_job(self):
		job_seeker = User.objects.create_user(
			username="jobseeker",
			password="test-password",
			role=User.Role.JOB_SEEKER,
		)
		self.client.force_login(job_seeker)

		response = self.client.get(reverse("jobs:create"))

		self.assertEqual(response.status_code, 404)

	def test_recruiter_can_edit_owned_job(self):
		self.client.force_login(self.recruiter)

		response = self.client.post(
			reverse("jobs:edit", args=[self.job.pk]),
			{
				"title": "Senior Backend Engineer",
				"description": "Lead the platform.",
				"employment_type": Job.EmploymentType.FULL_TIME,
			},
		)

		self.assertRedirects(response, reverse("jobs:dashboard"))
		self.job.refresh_from_db()
		self.assertEqual(self.job.title, "Senior Backend Engineer")

	def test_recruiter_cannot_edit_another_recruiters_job(self):
		self.client.force_login(self.other_recruiter)

		response = self.client.get(reverse("jobs:edit", args=[self.job.pk]))

		self.assertEqual(response.status_code, 404)

	def test_recruiter_can_close_owned_job(self):
		self.client.force_login(self.recruiter)

		response = self.client.post(reverse("jobs:close", args=[self.job.pk]))

		self.assertRedirects(response, reverse("jobs:dashboard"))
		self.job.refresh_from_db()
		self.assertEqual(self.job.status, Job.Status.CLOSED)

	def test_dashboard_separates_open_and_closed_jobs(self):
		closed_job = Job.objects.create(
			title="Closed Engineer",
			description="No longer accepting applications.",
			recruiter=self.recruiter,
		status=Job.Status.CLOSED,
		)
		self.client.force_login(self.recruiter)

		response = self.client.get(reverse("jobs:dashboard"))

		self.assertContains(response, "Open Jobs")
		self.assertContains(response, "Closed Jobs")
		self.assertContains(response, self.job.title)
		self.assertContains(response, closed_job.title)
		self.assertContains(response, reverse("jobs:edit", args=[self.job.pk]))
		self.assertContains(response, reverse("jobs:close", args=[self.job.pk]))
		self.assertNotContains(response, reverse("jobs:edit", args=[closed_job.pk]))
		self.assertNotContains(response, reverse("jobs:close", args=[closed_job.pk]))

	def test_closed_job_cannot_be_edited_or_closed_again(self):
		self.job.status = Job.Status.CLOSED
		self.job.save(update_fields=("status", "updated_at"))
		self.client.force_login(self.recruiter)

		edit_response = self.client.get(reverse("jobs:edit", args=[self.job.pk]))
		close_response = self.client.post(reverse("jobs:close", args=[self.job.pk]))

		self.assertEqual(edit_response.status_code, 404)
		self.assertEqual(close_response.status_code, 404)
		self.job.refresh_from_db()
		self.assertEqual(self.job.status, Job.Status.CLOSED)

	def test_closed_job_is_not_public(self):
		self.job.status = Job.Status.CLOSED
		self.job.save(update_fields=("status", "updated_at"))

		response = self.client.get(reverse("jobs:list"))

		self.assertNotContains(response, self.job.title)

	def test_recruiter_can_view_per_job_application_board(self):
		applicant = User.objects.create_user(
			username="applicant",
			password="test-password",
			role=User.Role.JOB_SEEKER,
		)
		application = Application.objects.create(
			job=self.job,
			applicant=applicant,
			full_name="Jamie Doe",
			email="jamie@example.com",
		)
		self.client.force_login(self.recruiter)

		response = self.client.get(reverse("jobs:application_board", args=[self.job.pk]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Applied")
		self.assertContains(response, application.full_name)

	def test_recruiter_can_move_application_and_close_is_not_delete(self):
		applicant = User.objects.create_user(
			username="applicant",
			password="test-password",
			role=User.Role.JOB_SEEKER,
		)
		application = Application.objects.create(
			job=self.job,
			applicant=applicant,
			full_name="Jamie Doe",
			email="jamie@example.com",
		)
		self.client.force_login(self.recruiter)

		response = self.client.post(
			reverse("jobs:update_application_status", args=[application.pk]),
			{"status": Application.Status.CLOSED},
		)

		self.assertRedirects(response, reverse("jobs:application_board", args=[self.job.pk]))
		application.refresh_from_db()
		self.assertEqual(application.status, Application.Status.CLOSED)

		delete_response = self.client.post(
			reverse("jobs:delete_application", args=[application.pk]),
		)
		self.assertRedirects(delete_response, reverse("jobs:application_board", args=[self.job.pk]))
		application.refresh_from_db()
		self.assertEqual(application.status, Application.Status.DELETED)

	def test_recruiter_cannot_manage_another_recruiters_application(self):
		applicant = User.objects.create_user(
			username="applicant",
			password="test-password",
			role=User.Role.JOB_SEEKER,
		)
		application = Application.objects.create(
			job=self.job,
			applicant=applicant,
			full_name="Jamie Doe",
			email="jamie@example.com",
		)
		self.client.force_login(self.other_recruiter)

		response = self.client.post(
			reverse("jobs:update_application_status", args=[application.pk]),
			{"status": Application.Status.SCREENED},
		)

		self.assertEqual(response.status_code, 404)
		application.refresh_from_db()
		self.assertEqual(application.status, Application.Status.APPLIED)
