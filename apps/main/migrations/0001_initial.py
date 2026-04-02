# Generated manually to keep project runnable without local makemigrations execution.
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(default="Alex Morgan", max_length=120)),
                ("role", models.CharField(default="Backend Engineer", max_length=120)),
                ("hero_title", models.CharField(default="Building scalable systems", max_length=180)),
                (
                    "hero_description",
                    models.TextField(
                        default="Python - Django - FastAPI - PostgreSQL - I design robust APIs, microservices, and cloud-native architectures that power modern applications."
                    ),
                ),
                ("about_title", models.CharField(default="Backend Architect & Problem Solver", max_length=180)),
                (
                    "about_description",
                    models.TextField(
                        default="I'm Alex Morgan - backend developer with 6+ years of experience designing high-performance APIs and distributed systems."
                    ),
                ),
                ("location", models.CharField(default="Austin, TX", max_length=120)),
                ("availability", models.CharField(default="Remote worldwide", max_length=120)),
                ("contact_email", models.EmailField(default="alex.morgan@backend.dev", max_length=254)),
                ("github_username", models.CharField(default="alexmorgan", max_length=80)),
                ("years_experience", models.PositiveSmallIntegerField(default=6)),
                ("uptime_sla", models.CharField(default="99.9%", max_length=16)),
                ("profile_image", models.ImageField(blank=True, null=True, upload_to="profiles/")),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["-is_active", "id"]},
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=120)),
                ("slug", models.SlugField(blank=True, max_length=140, unique=True)),
                ("icon_class", models.CharField(default="fas fa-code", max_length=80)),
                ("description", models.TextField()),
                (
                    "tech_stack",
                    models.CharField(
                        help_text="Comma separated. Example: Django, PostgreSQL, Redis",
                        max_length=300,
                    ),
                ),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["sort_order", "title"]},
        ),
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80)),
                ("icon_class", models.CharField(default="fas fa-code", max_length=80)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="SocialLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("platform", models.CharField(max_length=40)),
                ("url", models.URLField()),
                ("icon_class", models.CharField(default="fab fa-link", max_length=80)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["sort_order", "platform"]},
        ),
    ]
