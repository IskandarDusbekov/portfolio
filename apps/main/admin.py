from django.contrib import admin

from .models import ContactMessage, Profile, Project, Skill, SocialLink


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "contact_email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("full_name", "role", "contact_email")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_class", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active", "updated_at")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description", "tech_stack")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "url", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("platform", "url")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at", "updated_at")
    list_editable = ("is_read",)
