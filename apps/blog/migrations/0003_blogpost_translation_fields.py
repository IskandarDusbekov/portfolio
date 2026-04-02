from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_blogpost_views_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="content_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="excerpt_en",
            field=models.CharField(blank=True, max_length=320),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="title_en",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
