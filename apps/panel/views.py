from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.blog.models import BlogCategory, BlogPost
from apps.main.models import (
    ContactMessage,
    PageVisit,
    Profile,
    Project,
    Skill,
    SocialLink,
)
from .forms import (
    BlogCategoryForm,
    BlogPostForm,
    ProfileForm,
    ProjectForm,
    SkillForm,
    SocialLinkForm,
)


def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url="panel:login")
    @user_passes_test(lambda u: u.is_staff, login_url="panel:login")
    def _wrapped(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return _wrapped


def _safe_next(request, next_url):
    """Faqat shu saytga tegishli ichki URL'ga ruxsat (open-redirect himoyasi)."""
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return "panel:dashboard"


def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("panel:dashboard")

    error = None
    next_url = request.GET.get("next", "") or request.POST.get("next", "")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        try:
            user = authenticate(request, username=username, password=password)
        except PermissionDenied:
            # django-axes ko'p xato urinishdan keyin bloklaganda
            user = None
            error = (
                "Juda ko'p xato urinish. Xavfsizlik uchun kirish vaqtincha "
                "bloklandi. Bir ozdan keyin qayta urinib ko'ring."
            )
        if error is None:
            if user is not None and user.is_staff:
                login(request, user)
                return redirect(_safe_next(request, next_url))
            if user is not None and not user.is_staff:
                error = "Bu hisobda panelga kirish huquqi yo'q."
            else:
                error = "Login yoki parol noto'g'ri."
    return render(request, "panel/login.html", {"error": error, "next": next_url})


@login_required(login_url="panel:login")
@require_POST
def panel_logout(request):
    logout(request)
    return redirect("panel:login")


def _visit_analytics():
    """Aggregate visitor stats used by the dashboard and analytics page."""
    today = timezone.localdate()
    window_start = today - timedelta(days=13)

    visits = PageVisit.objects.filter(is_authenticated=False)

    daily_counts = {
        row["day"]: row["count"]
        for row in (
            visits.filter(created_at__date__gte=window_start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
        )
    }
    daily_uniques = {
        row["day"]: row["uniques"]
        for row in (
            visits.filter(created_at__date__gte=window_start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(uniques=Count("session_key", distinct=True))
        )
    }

    series = []
    for offset in range(13, -1, -1):
        day = today - timedelta(days=offset)
        series.append(
            {
                "label": day.strftime("%m-%d"),
                "count": daily_counts.get(day, 0),
                "uniques": daily_uniques.get(day, 0),
            }
        )
    max_count = max((item["count"] for item in series), default=0) or 1
    for item in series:
        item["height"] = round(item["count"] / max_count * 100)

    def _range_count(days):
        return visits.filter(created_at__date__gte=today - timedelta(days=days - 1)).count()

    def _range_unique(days):
        return (
            visits.filter(created_at__date__gte=today - timedelta(days=days - 1))
            .values("session_key")
            .distinct()
            .count()
        )

    top_pages = list(
        visits.filter(created_at__date__gte=today - timedelta(days=29))
        .values("path")
        .annotate(count=Count("id"))
        .order_by("-count")[:8]
    )

    return {
        "visits_today": visits.filter(created_at__date=today).count(),
        "unique_today": visits.filter(created_at__date=today).values("session_key").distinct().count(),
        "visits_7d": _range_count(7),
        "unique_7d": _range_unique(7),
        "visits_30d": _range_count(30),
        "total_visits": visits.count(),
        "visit_series": series,
        "top_pages": top_pages,
        "recent_visits": visits.order_by("-created_at")[:10],
    }


@staff_required
def dashboard(request):
    context = {
        "posts_count": BlogPost.objects.count(),
        "published_posts_count": BlogPost.objects.filter(is_published=True).count(),
        "categories_count": BlogCategory.objects.count(),
        "projects_count": Project.objects.count(),
        "skills_count": Skill.objects.count(),
        "social_links_count": SocialLink.objects.count(),
        "profiles_count": Profile.objects.count(),
        "unread_messages_count": ContactMessage.objects.filter(is_read=False).count(),
        "recent_posts": BlogPost.objects.select_related("category").order_by("-updated_at")[:5],
        "recent_projects": Project.objects.order_by("-updated_at")[:5],
        "recent_messages": ContactMessage.objects.order_by("-created_at")[:5],
    }
    context.update(_visit_analytics())
    return render(request, "panel/dashboard.html", context)


@staff_required
def analytics(request):
    visits = PageVisit.objects.filter(is_authenticated=False).order_by("-created_at")
    paginator = Paginator(visits, 40)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_title": "Analytics",
        "page_obj": page_obj,
    }
    context.update(_visit_analytics())
    return render(request, "panel/analytics.html", context)


@staff_required
def post_list(request):
    query = request.GET.get("q", "").strip()
    posts = BlogPost.objects.select_related("category").order_by("-published_at")
    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(title_en__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(excerpt_en__icontains=query)
            | Q(category__name__icontains=query)
        )
    return render(request, "panel/post_list.html", {"posts": posts, "query": query})


@staff_required
def post_create(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Post created successfully.")
            return redirect("panel:post_list")
    else:
        form = BlogPostForm()
    return render(request, "panel/post_form.html", {"form": form, "page_title": "Create Blog Post"})


@staff_required
def post_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == "POST":
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect("panel:post_list")
    else:
        form = BlogPostForm(instance=post)
    return render(request, "panel/post_form.html", {"form": form, "page_title": "Edit Blog Post", "post": post})


@staff_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("panel:post_list")


@staff_required
def category_list(request):
    categories = BlogCategory.objects.order_by("sort_order", "name")
    return render(request, "panel/category_list.html", {"categories": categories})


@staff_required
def category_create(request):
    if request.method == "POST":
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("panel:category_list")
    else:
        form = BlogCategoryForm()
    return render(request, "panel/category_form.html", {"form": form, "page_title": "Create Category"})


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(BlogCategory, pk=pk)
    if request.method == "POST":
        form = BlogCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("panel:category_list")
    else:
        form = BlogCategoryForm(instance=category)
    return render(
        request,
        "panel/category_form.html",
        {"form": form, "page_title": "Edit Category", "category": category},
    )


@staff_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(BlogCategory, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect("panel:category_list")


@staff_required
def message_list(request):
    messages_qs = ContactMessage.objects.order_by("-created_at")
    return render(request, "panel/message_list.html", {"messages_list": messages_qs})


@staff_required
@require_POST
def message_mark_read(request, pk):
    message_item = get_object_or_404(ContactMessage, pk=pk)
    message_item.is_read = True
    message_item.save(update_fields=["is_read"])
    messages.success(request, "Message marked as read.")
    return redirect("panel:message_list")


@staff_required
def project_list(request):
    query = request.GET.get("q", "").strip()
    projects = Project.objects.order_by("sort_order", "title")
    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(tech_stack__icontains=query))
    return render(request, "panel/project_list.html", {"projects": projects, "query": query, "page_title": "Projects"})


@staff_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project created successfully.")
            return redirect("panel:project_list")
    else:
        form = ProjectForm()
    return render(request, "panel/project_form.html", {"form": form, "page_title": "Create Project"})


@staff_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect("panel:project_list")
    else:
        form = ProjectForm(instance=project)
    return render(request, "panel/project_form.html", {"form": form, "page_title": "Edit Project", "project": project})


@staff_required
@require_POST
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, "Project deleted.")
    return redirect("panel:project_list")


@staff_required
def skill_list(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.order_by("sort_order", "name")
    if query:
        skills = skills.filter(Q(name__icontains=query) | Q(icon_class__icontains=query))
    return render(request, "panel/skill_list.html", {"skills": skills, "query": query, "page_title": "Skills"})


@staff_required
def skill_create(request):
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Skill created successfully.")
            return redirect("panel:skill_list")
    else:
        form = SkillForm()
    return render(request, "panel/skill_form.html", {"form": form, "page_title": "Create Skill"})


@staff_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, "Skill updated successfully.")
            return redirect("panel:skill_list")
    else:
        form = SkillForm(instance=skill)
    return render(request, "panel/skill_form.html", {"form": form, "page_title": "Edit Skill", "skill": skill})


@staff_required
@require_POST
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    skill.delete()
    messages.success(request, "Skill deleted.")
    return redirect("panel:skill_list")


@staff_required
def social_link_list(request):
    query = request.GET.get("q", "").strip()
    links = SocialLink.objects.order_by("sort_order", "platform")
    if query:
        links = links.filter(Q(platform__icontains=query) | Q(url__icontains=query))
    return render(request, "panel/social_list.html", {"links": links, "query": query, "page_title": "Social Links"})


@staff_required
def social_link_create(request):
    if request.method == "POST":
        form = SocialLinkForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Social link created successfully.")
            return redirect("panel:social_list")
    else:
        form = SocialLinkForm()
    return render(request, "panel/social_form.html", {"form": form, "page_title": "Create Social Link"})


@staff_required
def social_link_edit(request, pk):
    link = get_object_or_404(SocialLink, pk=pk)
    if request.method == "POST":
        form = SocialLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, "Social link updated successfully.")
            return redirect("panel:social_list")
    else:
        form = SocialLinkForm(instance=link)
    return render(request, "panel/social_form.html", {"form": form, "page_title": "Edit Social Link", "link": link})


@staff_required
@require_POST
def social_link_delete(request, pk):
    link = get_object_or_404(SocialLink, pk=pk)
    link.delete()
    messages.success(request, "Social link deleted.")
    return redirect("panel:social_list")


@staff_required
def profile_list(request):
    profiles = Profile.objects.order_by("-is_active", "-updated_at")
    return render(request, "panel/profile_list.html", {"profiles": profiles, "page_title": "Profiles"})


@staff_required
def profile_create(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile created successfully.")
            return redirect("panel:profile_list")
    else:
        form = ProfileForm()
    return render(request, "panel/profile_form.html", {"form": form, "page_title": "Create Profile"})


@staff_required
def profile_edit(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("panel:profile_list")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "panel/profile_form.html", {"form": form, "page_title": "Edit Profile", "profile": profile})


@staff_required
@require_POST
def profile_delete(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    profile.delete()
    messages.success(request, "Profile deleted.")
    return redirect("panel:profile_list")
