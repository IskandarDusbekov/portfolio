from django.test import TestCase
from django.urls import reverse

from .models import BlogCategory, BlogPost


class BlogPagesTests(TestCase):
    def setUp(self):
        category = BlogCategory.objects.create(name="Database")
        BlogPost.objects.create(
            title="Django ORM Tips",
            category=category,
            excerpt="Short",
            content="Long content",
            read_time_minutes=7,
        )

    def test_blog_page_loads(self):
        response = self.client.get(reverse("blog"))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_loads(self):
        response = self.client.get(reverse("view_post", kwargs={"slug": "django-orm-tips"}))
        self.assertEqual(response.status_code, 200)
