import time

from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import F
from django.http import Http404
from django.shortcuts import render

from .models import BlogCategory, BlogPost


VIEW_DEBOUNCE_SECONDS = 90
VIEW_FLUSH_THRESHOLD = 10
VIEW_FLUSH_INTERVAL_SECONDS = 300
VIEW_BUFFER_TTL_SECONDS = 60 * 60 * 24

# Rasmi yo'q yoki tashqi rasm ochilmagan postlar uchun lokal zaxira rasm.
# Tashqi tarmoqqa bog'liq emas (data-URI SVG), barcha tirnoqlar %22 bilan
# kodlangani uchun HTML atributlari ichida xavfsiz ishlaydi.
BLOG_PLACEHOLDER = (
    "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20"
    "width%3D%22900%22%20height%3D%22550%22%3E%3Cdefs%3E%3ClinearGradient%20id"
    "%3D%22g%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E"
    "%3Cstop%20offset%3D%220%22%20stop-color%3D%22%232563eb%22/%3E%3Cstop%20"
    "offset%3D%221%22%20stop-color%3D%22%230ea5e9%22/%3E%3C/linearGradient%3E"
    "%3C/defs%3E%3Crect%20width%3D%22900%22%20height%3D%22550%22%20fill%3D%22"
    "url%28%23g%29%22/%3E%3Ctext%20x%3D%22450%22%20y%3D%22290%22%20fill%3D%22"
    "%23ffffff%22%20font-family%3D%22Arial%2CHelvetica%2Csans-serif%22%20font-"
    "size%3D%2252%22%20font-weight%3D%22bold%22%20text-anchor%3D%22middle%22%3E"
    "BackendDev%3C/text%3E%3C/svg%3E"
)


DEFAULT_BLOG_POSTS = [
    {
        "title": "Optimizing Django ORM for 10M+ Records: A Complete Guide",
        "slug": "optimizing-django-orm",
        "category": "Database",
        "date": "April 15, 2025",
        "readTime": "8 min read",
        "image": "https://picsum.photos/id/1/800/500",
        "shortDesc": "Advanced techniques to reduce query latency, use select_related, prefetch_related, and raw SQL when needed.",
        "fullDesc": "When working with millions of records in Django, the ORM can become a bottleneck if not used correctly.",
        "featured": True,
    },
    {
        "title": "Designing Idempotent REST APIs for Financial Systems",
        "slug": "idempotent-rest-apis",
        "category": "API Design",
        "date": "April 8, 2025",
        "readTime": "6 min read",
        "image": "https://picsum.photos/id/26/800/500",
        "shortDesc": "Learn how to make your APIs safe for retries and prevent duplicate processing in distributed systems.",
        "fullDesc": "Idempotency is crucial for reliable APIs, especially in financial transactions and critical operations.",
        "featured": False,
    },
    {
        "title": "Async Python with FastAPI: Best Practices for High Concurrency",
        "slug": "async-python-fastapi",
        "category": "Python",
        "date": "March 28, 2025",
        "readTime": "10 min read",
        "image": "https://picsum.photos/id/91/800/500",
        "shortDesc": "Leverage Python async/await to build high-concurrency APIs with FastAPI and async database drivers.",
        "fullDesc": "FastAPI has revolutionized Python backend development with async capabilities.",
        "featured": False,
    },
]


def blog(request):
    current_lang = getattr(request, "site_lang", "uz")
    categories = BlogCategory.objects.filter(is_active=True)
    selected_category_slug = request.GET.get("category", "").strip()

    posts_qs = BlogPost.objects.filter(is_published=True).select_related("category")
    selected_category = None
    if selected_category_slug:
        selected_category = BlogCategory.objects.filter(is_active=True, slug=selected_category_slug).first()
        if selected_category:
            posts_qs = posts_qs.filter(category=selected_category)

    featured_post = posts_qs.filter(is_featured=True).order_by("-published_at", "-id").first()
    if not featured_post:
        featured_post = posts_qs.order_by("-published_at", "-id").first()
    listing_qs = posts_qs.exclude(pk=featured_post.pk) if featured_post else posts_qs

    paginator = Paginator(listing_qs, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    if featured_post:
        featured_post.display_title = featured_post.get_title(current_lang)
        featured_post.display_excerpt = featured_post.get_excerpt(current_lang)
    for post in page_obj.object_list:
        post.display_title = post.get_title(current_lang)
        post.display_excerpt = post.get_excerpt(current_lang)

    context = {
        "categories": categories,
        "selected_category_slug": selected_category_slug,
        "featured_post": featured_post,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "current_lang": current_lang,
        "blog_placeholder": BLOG_PLACEHOLDER,
    }
    return render(request, "blog.html", context)


def _buffered_increment_post_view(request, post):
    now_ts = int(time.time())
    session_key = f"post_last_viewed_at:{post.pk}"
    last_viewed_ts = int(request.session.get(session_key, 0))
    if now_ts - last_viewed_ts < VIEW_DEBOUNCE_SECONDS:
        current_buffer = int(cache.get(f"post_views_buffer:{post.pk}", 0) or 0)
        return post.views_count + current_buffer

    request.session[session_key] = now_ts
    request.session.modified = True

    buffer_key = f"post_views_buffer:{post.pk}"
    last_flush_key = f"post_views_last_flush:{post.pk}"

    current_buffer = int(cache.get(buffer_key, 0) or 0) + 1
    cache.set(buffer_key, current_buffer, timeout=VIEW_BUFFER_TTL_SECONDS)

    last_flush_ts = int(cache.get(last_flush_key, 0) or 0)
    should_flush = (
        current_buffer >= VIEW_FLUSH_THRESHOLD
        or (now_ts - last_flush_ts) >= VIEW_FLUSH_INTERVAL_SECONDS
    )

    if should_flush:
        BlogPost.objects.filter(pk=post.pk).update(views_count=F("views_count") + current_buffer)
        post.views_count += current_buffer
        cache.set(buffer_key, 0, timeout=VIEW_BUFFER_TTL_SECONDS)
        cache.set(last_flush_key, now_ts, timeout=VIEW_BUFFER_TTL_SECONDS)
        return post.views_count

    return post.views_count + current_buffer


def view_post(request, slug):
    current_lang = getattr(request, "site_lang", "uz")
    post = BlogPost.objects.filter(is_published=True).select_related("category").filter(slug=slug).first()
    if post:
        displayed_views_count = _buffered_increment_post_view(request, post)
        related_posts = list(
            BlogPost.objects.filter(is_published=True, category=post.category)
            .exclude(pk=post.pk)
            .order_by("-published_at")[:3]
        )
        previous_post = (
            BlogPost.objects.filter(is_published=True, published_at__lt=post.published_at)
            .order_by("-published_at")
            .first()
        )
        next_post = (
            BlogPost.objects.filter(is_published=True, published_at__gt=post.published_at)
            .order_by("published_at")
            .first()
        )
        post.display_title = post.get_title(current_lang)
        post.display_content = post.get_content(current_lang)
        for item in related_posts:
            item.display_title = item.get_title(current_lang)
            item.display_excerpt = item.get_excerpt(current_lang)
        if previous_post:
            previous_post.display_title = previous_post.get_title(current_lang)
        if next_post:
            next_post.display_title = next_post.get_title(current_lang)
        context = {
            "post": post,
            "related_posts": related_posts,
            "previous_post": previous_post,
            "next_post": next_post,
            "displayed_views_count": displayed_views_count,
            "current_lang": current_lang,
            "blog_placeholder": BLOG_PLACEHOLDER,
        }
        return render(request, "view_post.html", context)

    fallback_post = next((item for item in DEFAULT_BLOG_POSTS if item["slug"] == slug), None)
    if fallback_post:
        context = {
            "fallback_post": fallback_post,
        }
        return render(request, "view_post.html", context)

    raise Http404("Post not found")
