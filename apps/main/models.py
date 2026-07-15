from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify


phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{7,20}$",
    message="Telefon raqamini to'g'ri kiriting. Masalan: +998901234567",
)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimestampedModel):
    full_name = models.CharField(max_length=120, default="Alex Morgan")
    role = models.CharField(max_length=120, default="Backend Engineer")
    hero_title = models.CharField(max_length=180, default="Building scalable systems")
    hero_description = models.TextField(
        default=(
            "Python - Django - FastAPI - PostgreSQL - I design robust APIs, "
            "microservices, and cloud-native architectures that power modern applications."
        )
    )
    about_title = models.CharField(max_length=180, default="Backend Architect & Problem Solver")
    about_description = models.TextField(
        default=(
            "I'm Alex Morgan - backend developer with 6+ years of experience designing "
            "high-performance APIs and distributed systems."
        )
    )
    location = models.CharField(max_length=120, default="Austin, TX")
    availability = models.CharField(max_length=120, default="Remote worldwide")
    contact_email = models.EmailField(default="alex.morgan@backend.dev")
    github_username = models.CharField(max_length=80, default="alexmorgan")
    years_experience = models.PositiveSmallIntegerField(default=6)
    uptime_sla = models.CharField(max_length=16, default="99.9%")
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_active", "id"]

    def __str__(self):
        return self.full_name


class Skill(TimestampedModel):
    name = models.CharField(max_length=80)
    icon_class = models.CharField(max_length=80, default="fas fa-code")
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Project(TimestampedModel):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon_class = models.CharField(max_length=80, default="fas fa-code")
    description = models.TextField()
    tech_stack = models.CharField(
        max_length=300,
        help_text="Comma separated. Example: Django, PostgreSQL, Redis",
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            idx = 1
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                idx += 1
                slug = f"{base_slug}-{idx}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def tech_tags(self):
        return [item.strip() for item in self.tech_stack.split(",") if item.strip()]


class SocialLink(TimestampedModel):
    platform = models.CharField(max_length=40)
    url = models.URLField()
    icon_class = models.CharField(max_length=80, default="fab fa-link")
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "platform"]

    def __str__(self):
        return self.platform


class ContactMessage(TimestampedModel):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, default="", validators=[phone_validator])
    email = models.EmailField(blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.phone}>"


class PageVisit(models.Model):
    """A single page view by a site visitor, used for the panel analytics."""

    path = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    user_agent = models.CharField(max_length=300, blank=True)
    referrer = models.CharField(max_length=300, blank=True)
    is_authenticated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at", "session_key"]),
        ]

    def __str__(self):
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M}"