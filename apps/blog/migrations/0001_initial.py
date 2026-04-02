# Generated manually to keep project runnable without local makemigrations execution.
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BlogCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=90, unique=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"verbose_name_plural": "Blog categories", "ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("cover_image_url", models.URLField(blank=True)),
                ("excerpt", models.CharField(max_length=320)),
                ("content", models.TextField()),
                ("read_time_minutes", models.PositiveSmallIntegerField(default=5)),
                ("is_featured", models.BooleanField(default=False)),
                ("is_published", models.BooleanField(default=True)),
                ("published_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="posts",
                        to="blog.blogcategory",
                    ),
                ),
            ],
            options={"ordering": ["-published_at", "-id"]},
        ),
    ]
