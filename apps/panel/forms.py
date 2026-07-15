from django import forms

from apps.blog.models import BlogCategory, BlogPost
from apps.main.models import BlockedIP, Profile, Project, Skill, SocialLink


class BlockedIPForm(forms.ModelForm):
    class Meta:
        model = BlockedIP
        fields = ["ip_address", "reason"]
        widgets = {
            "ip_address": forms.TextInput(attrs={"class": "form-input", "placeholder": "192.168.1.1"}),
            "reason": forms.TextInput(attrs={"class": "form-input", "placeholder": "Sabab (ixtiyoriy)"}),
        }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            "title",
            "title_en",
            "slug",
            "category",
            "cover_image",
            "cover_image_url",
            "excerpt",
            "excerpt_en",
            "content",
            "content_en",
            "read_time_minutes",
            "views_count",
            "is_featured",
            "is_published",
            "published_at",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "Post title (UZ)"}),
            "title_en": forms.TextInput(attrs={"class": "form-input", "placeholder": "Post title (EN)"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "placeholder": "post-slug"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "cover_image": forms.ClearableFileInput(attrs={"class": "form-input", "accept": "image/*"}),
            "cover_image_url": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://... (ixtiyoriy)"}),
            "excerpt": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Short excerpt (UZ)"}),
            "excerpt_en": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Short excerpt (EN)"}),
            "content": forms.Textarea(attrs={"class": "form-input", "rows": 10, "placeholder": "Full content (UZ)"}),
            "content_en": forms.Textarea(attrs={"class": "form-input", "rows": 10, "placeholder": "Full content (EN)"}),
            "read_time_minutes": forms.NumberInput(attrs={"class": "form-input", "min": 1}),
            "views_count": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
            "published_at": forms.DateTimeInput(attrs={"class": "form-input", "type": "datetime-local"}),
        }


class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ["name", "slug", "sort_order", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Category name"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "placeholder": "category-slug"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "slug", "icon_class", "description", "tech_stack", "sort_order", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "Project title"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "placeholder": "project-slug"}),
            "icon_class": forms.TextInput(attrs={"class": "form-input", "placeholder": "fas fa-code"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 5, "placeholder": "Project details"}),
            "tech_stack": forms.TextInput(attrs={"class": "form-input", "placeholder": "Django, PostgreSQL, Redis"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "icon_class", "sort_order", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Skill name"}),
            "icon_class": forms.TextInput(attrs={"class": "form-input", "placeholder": "fab fa-python"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
        }


class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ["platform", "url", "icon_class", "sort_order", "is_active"]
        widgets = {
            "platform": forms.TextInput(attrs={"class": "form-input", "placeholder": "GitHub"}),
            "url": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://..."}),
            "icon_class": forms.TextInput(attrs={"class": "form-input", "placeholder": "fab fa-github"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "role",
            "hero_title",
            "hero_description",
            "about_title",
            "about_description",
            "location",
            "availability",
            "contact_email",
            "github_username",
            "years_experience",
            "uptime_sla",
            "profile_image",
            "is_active",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Full name"}),
            "role": forms.TextInput(attrs={"class": "form-input", "placeholder": "Backend Engineer"}),
            "hero_title": forms.TextInput(attrs={"class": "form-input"}),
            "hero_description": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "about_title": forms.TextInput(attrs={"class": "form-input"}),
            "about_description": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "location": forms.TextInput(attrs={"class": "form-input"}),
            "availability": forms.TextInput(attrs={"class": "form-input"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-input"}),
            "github_username": forms.TextInput(attrs={"class": "form-input"}),
            "years_experience": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
            "uptime_sla": forms.TextInput(attrs={"class": "form-input", "placeholder": "99.9%"}),
        }
