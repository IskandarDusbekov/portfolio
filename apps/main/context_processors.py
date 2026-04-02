from .models import Profile, SocialLink


def site_identity(request):
    profile = Profile.objects.filter(is_active=True).first()
    if not profile:
        profile = Profile(
            full_name="Alex Morgan",
            role="Backend Engineer",
            hero_title="Building scalable systems",
            hero_description=(
                "Python - Django - FastAPI - PostgreSQL - I design robust APIs, "
                "microservices, and cloud-native architectures that power modern applications."
            ),
            about_title="Backend Architect & Problem Solver",
            about_description=(
                "I'm Alex Morgan - backend developer with 6+ years of experience designing "
                "high-performance APIs and distributed systems."
            ),
            location="Austin, TX",
            availability="Remote worldwide",
            contact_email="alex.morgan@backend.dev",
            github_username="alexmorgan",
            years_experience=6,
            uptime_sla="99.9%",
            is_active=True,
        )
    social_links = list(SocialLink.objects.filter(is_active=True))
    if not social_links:
        social_links = [
            SocialLink(platform="GitHub", url="#", icon_class="fab fa-github", sort_order=1, is_active=True),
            SocialLink(platform="LinkedIn", url="#", icon_class="fab fa-linkedin-in", sort_order=2, is_active=True),
            SocialLink(platform="Twitter", url="#", icon_class="fab fa-twitter", sort_order=3, is_active=True),
            SocialLink(platform="Telegram", url="#", icon_class="fab fa-telegram", sort_order=4, is_active=True),
        ]
    return {
        "site_profile": profile,
        "site_social_links": social_links,
    }
