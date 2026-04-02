from django.contrib import admin

from .models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "title_en", "category", "views_count", "is_featured", "is_published", "published_at")
    list_filter = ("is_published", "is_featured", "category")
    list_editable = ("views_count", "is_featured", "is_published")
    search_fields = ("title", "title_en", "excerpt", "excerpt_en", "content", "content_en")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category",)
    fieldsets = (
        (
            "Uzbek Content",
            {
                "fields": ("title", "excerpt", "content"),
            },
        ),
        (
            "English Content",
            {
                "fields": ("title_en", "excerpt_en", "content_en"),
            },
        ),
        (
            "Meta",
            {
                "fields": (
                    "slug",
                    "category",
                    "cover_image_url",
                    "read_time_minutes",
                    "views_count",
                    "is_featured",
                    "is_published",
                    "published_at",
                ),
            },
        ),
    )
