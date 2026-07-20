from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

from .tracking.useragent import DEVICE_CHOICES


BLOCKED_IPS_CACHE_KEY = "blocked_ips_set"


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


class VisitorSession(models.Model):
    """Bitta tashrifchi sessiyasi - qurilma, manba va sayt bo'ylab yo'li.

    Har bir sahifa ko'rishi (PageVisit) shu sessiyaga bog'lanadi.
    """

    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    user_agent = models.TextField(blank=True)

    # User-Agent tahlili
    browser = models.CharField(max_length=60, blank=True, db_index=True)
    browser_version = models.CharField(max_length=30, blank=True)
    os = models.CharField(max_length=60, blank=True, db_index=True)
    os_version = models.CharField(max_length=30, blank=True)
    device_type = models.CharField(
        max_length=20, blank=True, db_index=True, choices=DEVICE_CHOICES
    )
    device_model = models.CharField(max_length=80, blank=True)

    # Klient ma'lumotlari
    language = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=60, blank=True)

    # Bot aniqlash
    is_bot = models.BooleanField(default=False, db_index=True)
    bot_name = models.CharField(max_length=60, blank=True)

    # Trafik manbasi
    referer = models.TextField(blank=True)
    referer_source = models.CharField(max_length=40, blank=True, db_index=True)

    # Sayt bo'ylab yo'l
    landing_page = models.CharField(max_length=255, blank=True)
    exit_page = models.CharField(max_length=255, blank=True)
    page_count = models.PositiveIntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_activity = models.DateTimeField(auto_now=True, db_index=True)

    # Geo ma'lumotlari - keyingi bosqichda GeoIP bilan to'ldiriladi
    country = models.CharField(max_length=60, blank=True, db_index=True)
    country_code = models.CharField(max_length=2, blank=True)
    region = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    isp = models.CharField(max_length=120, blank=True)
    asn = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["-last_activity", "is_bot"]),
            models.Index(fields=["started_at", "is_bot"]),
        ]

    def __str__(self):
        who = self.bot_name or self.browser or "Unknown"
        return f"{who} @ {self.ip_address or '-'}"

    @property
    def duration_seconds(self):
        """Sessiya davomiyligi (soniyada)."""
        if not self.started_at or not self.last_activity:
            return 0
        return max(0, int((self.last_activity - self.started_at).total_seconds()))

    @property
    def duration_label(self):
        """Davomiylikni o'qiladigan ko'rinishda qaytaradi."""
        total = self.duration_seconds
        if total < 60:
            return f"{total}s"
        minutes, seconds = divmod(total, 60)
        if minutes < 60:
            return f"{minutes}m {seconds}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes}m"


class PageVisit(models.Model):
    """A single page view by a site visitor, used for the panel analytics."""

    session = models.ForeignKey(
        VisitorSession,
        on_delete=models.CASCADE,
        related_name="visits",
        null=True,
        blank=True,
    )
    path = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    user_agent = models.CharField(max_length=300, blank=True)
    referrer = models.CharField(max_length=300, blank=True)
    is_authenticated = models.BooleanField(default=False)
    status_code = models.PositiveSmallIntegerField(default=200, db_index=True)
    is_bot = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at", "session_key"]),
            models.Index(fields=["created_at", "is_bot"]),
            models.Index(fields=["status_code", "created_at"]),
        ]

    def __str__(self):
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M}"


class BlockedIP(models.Model):
    """Bloklangan IP manzillar — bu IP'lardan kelgan so'rovlar rad etiladi."""

    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"

    def __str__(self):
        return self.ip_address

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(BLOCKED_IPS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(BLOCKED_IPS_CACHE_KEY)

    @classmethod
    def blocked_set(cls):
        """Bloklangan IP'lar to'plami (5 daqiqaga keshlanadi)."""
        ips = cache.get(BLOCKED_IPS_CACHE_KEY)
        if ips is None:
            ips = set(cls.objects.values_list("ip_address", flat=True))
            cache.set(BLOCKED_IPS_CACHE_KEY, ips, timeout=300)
        return ips