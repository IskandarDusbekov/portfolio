import time

from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ContactMessageForm
from .models import Profile, Project, Skill


DEFAULT_SKILLS = [
    ("Python", "fab fa-python"),
    ("Django", "fas fa-database"),
    ("FastAPI", "fas fa-bolt"),
    ("PostgreSQL", "fas fa-database"),
    ("Docker", "fab fa-docker"),
    ("Git", "fab fa-git-alt"),
    ("AWS", "fas fa-cloud"),
    ("Redis", "fas fa-chart-line"),
    ("Kafka", "fas fa-stream"),
]

DEFAULT_PROJECTS = [
    {
        "title": "ScaleAPI Gateway",
        "desc": "High-performance API gateway with rate limiting, JWT auth, and real-time analytics. Handles 15k+ req/sec.",
        "icon": "fas fa-network-wired",
        "tags": ["Python", "FastAPI", "Redis", "Docker"],
    },
    {
        "title": "FlowCore Engine",
        "desc": "Workflow automation backend with Celery, PostgreSQL, and event-driven architecture.",
        "icon": "fas fa-diagram-project",
        "tags": ["Django", "Celery", "PostgreSQL", "RabbitMQ"],
    },
    {
        "title": "Nexus Data Platform",
        "desc": "Real-time analytics backend for IoT devices. TimescaleDB, async workers, and WebSocket streams.",
        "icon": "fas fa-chart-line",
        "tags": ["FastAPI", "TimescaleDB", "Redis", "WebSocket"],
    },
    {
        "title": "AuthService",
        "desc": "Centralized authentication microservice with OAuth2, SSO, and multi-factor authentication support.",
        "icon": "fas fa-shield-alt",
        "tags": ["Django", "JWT", "OAuth2", "PostgreSQL"],
    },
    {
        "title": "TaskFlow",
        "desc": "Distributed task scheduler with priority queues, retry logic, and real-time monitoring dashboard.",
        "icon": "fas fa-tasks",
        "tags": ["Python", "Celery", "Redis", "Django"],
    },
    {
        "title": "Ecom Backend Suite",
        "desc": "Scalable e-commerce backend handling inventory, payments, and order management.",
        "icon": "fas fa-cart-shopping",
        "tags": ["Django", "DRF", "Stripe API", "PostgreSQL"],
    },
]


def index(request):
    projects = list(Project.objects.filter(is_active=True))
    skills = list(Skill.objects.filter(is_active=True))

    profile = Profile.objects.filter(is_active=True).first()
    if not profile:
        profile = Profile(
            full_name="Alex Morgan",
            role="Backend Engineer",
            hero_title="Building scalable systems",
            hero_description=(
                "Python - Django - FastAPI - PostgreSQL - I design robust APIs, microservices, "
                "and cloud-native architectures that power modern applications."
            ),
            about_title="Backend Architect & Problem Solver",
            about_description=(
                "I'm Alex Morgan - backend developer with 6+ years of experience designing high-performance "
                "APIs and distributed systems. I focus on clean architecture, database optimization, and "
                "scalable cloud deployments."
            ),
            location="Austin, TX",
            availability="Remote worldwide",
            contact_email="alex.morgan@backend.dev",
            github_username="alexmorgan",
            years_experience=6,
            uptime_sla="99.9%",
            is_active=True,
        )

    if projects:
        projects_payload = [
            {
                "title": project.title,
                "desc": project.description,
                "icon": project.icon_class,
                "tags": project.tech_tags,
                "tags_text": ", ".join(project.tech_tags),
            }
            for project in projects
        ]
    else:
        projects_payload = [
            {
                **item,
                "tags_text": ", ".join(item["tags"]),
            }
            for item in DEFAULT_PROJECTS
        ]

    if skills:
        skills_payload = [{"name": item.name, "icon": item.icon_class} for item in skills]
    else:
        skills_payload = [{"name": name, "icon": icon} for name, icon in DEFAULT_SKILLS]

    context = {
        "profile": profile,
        "skills": skills_payload,
        "projects": projects_payload,
        "projects_count": len(projects_payload),
    }
    return render(request, "index.html", context)


@require_POST
def submit_contact(request):
    contact_redirect_url = f"{reverse('index')}#contact"
    honeypot_value = request.POST.get("website", "").strip()
    if honeypot_value:
        messages.error(request, "Invalid submission detected.")
        return redirect(contact_redirect_url)

    client_ip = request.META.get("REMOTE_ADDR", "unknown")
    cache_key = f"contact-last-submit:{client_ip}"
    last_submit_ts = cache.get(cache_key)
    now_ts = time.time()
    if last_submit_ts and (now_ts - last_submit_ts) < 30:
        payload = {"ok": False, "message": "Please wait 30 seconds before sending another message."}
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(payload, status=429)
        messages.warning(request, payload["message"])
        return redirect(contact_redirect_url)

    form = ContactMessageForm(request.POST)
    if form.is_valid():
        form.save()
        cache.set(cache_key, now_ts, timeout=30)
        success_message = "Xabaringiz yuborildi. Tez orada javob beraman."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": success_message})
        messages.success(request, success_message)
        return redirect(contact_redirect_url)

    error_message = "Formani tekshiring va qaytadan yuboring."
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "ok": False,
                "errors": form.errors,
                "message": error_message,
            },
            status=400,
        )
    messages.error(request, error_message)
    return redirect(contact_redirect_url)
