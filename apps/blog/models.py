from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Blog categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.PROTECT, related_name="posts")
    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    cover_image_url = models.URLField(blank=True)
    excerpt = models.CharField(max_length=320)
    excerpt_en = models.CharField(max_length=320, blank=True)
    content = models.TextField()
    content_en = models.TextField(blank=True)
    read_time_minutes = models.PositiveSmallIntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            idx = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                idx += 1
                slug = f"{base_slug}-{idx}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def cover_src(self):
        """Yuklangan rasmni afzal ko'radi, bo'lmasa eski URL maydonini qaytaradi."""
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url

    @property
    def read_time_label(self):
        return f"{self.read_time_minutes} min read"

    def get_title(self, lang):
        if lang == "en" and self.title_en:
            return self.title_en
        return self.title

    def get_excerpt(self, lang):
        if lang == "en" and self.excerpt_en:
            return self.excerpt_en
        return self.excerpt

    def get_content(self, lang):
        if lang == "en" and self.content_en:
            return self.content_en
        return self.content
