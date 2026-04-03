from .models import Profile, SocialLink


TRANSLATIONS = {
    "uz": {
        "nav_home": "Bosh sahifa",
        "nav_projects": "Loyihalar",
        "nav_about": "Men haqimda",
        "nav_contact": "Aloqa",
        "nav_blog": "Blog",
        "blog_title": "Backend Maqolalar",
        "blog_subtitle": "Arxitektura, API dizayni va amaliy backend tajribalari.",
        "blog_all_posts": "Barcha Postlar",
        "blog_featured": "Asosiy Post",
        "blog_recent": "So'nggi Maqolalar",
        "blog_read_full": "To'liq o'qish",
        "blog_no_posts": "Bu kategoriya uchun postlar hozircha yo'q.",
        "blog_back": "Blogga qaytish",
        "blog_prev": "Oldingi",
        "blog_next": "Keyingi",
        "blog_related": "O'xshash Postlar",
        "views": "ko'rish",
        "min_read": "daq o'qish",
    },
    "en": {
        "nav_home": "Home",
        "nav_projects": "Projects",
        "nav_about": "About",
        "nav_contact": "Contact",
        "nav_blog": "Blog",
        "blog_title": "Backend Insights",
        "blog_subtitle": "Architecture, API design, scalability, and practical backend case studies.",
        "blog_all_posts": "All Posts",
        "blog_featured": "Featured",
        "blog_recent": "Recent Articles",
        "blog_read_full": "Read full article",
        "blog_no_posts": "No posts found for this category yet.",
        "blog_back": "Back to blog",
        "blog_prev": "Previous",
        "blog_next": "Next",
        "blog_related": "Related Posts",
        "views": "views",
        "min_read": "min read",
    },
}


def site_identity(request):
    profile = Profile.objects.filter(is_active=True).order_by("-updated_at", "-id").first()
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

    current_lang = getattr(request, "site_lang", request.session.get("site_lang", "uz"))
    if current_lang not in {"uz", "en"}:
        current_lang = "uz"

    return {
        "site_profile": profile,
        "site_social_links": social_links,
        "current_lang": current_lang,
        "t": TRANSLATIONS[current_lang],
    }
