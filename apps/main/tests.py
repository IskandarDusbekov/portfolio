from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage, Project


class IndexPageTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_contact_form_creates_message(self):
        response = self.client.post(
            reverse("submit_contact"),
            data={"name": "Ali", "email": "ali@example.com", "message": "Hello"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)


class ProjectModelTests(TestCase):
    def test_slug_is_generated(self):
        project = Project.objects.create(
            title="Gateway Service",
            description="Desc",
            tech_stack="Django, Redis",
        )
        self.assertEqual(project.slug, "gateway-service")
