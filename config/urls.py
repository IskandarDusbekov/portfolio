from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.main.views import robots_txt

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("robots.txt", robots_txt, name="robots_txt"),
    path(settings.PANEL_URL, include("apps.panel.urls")),
    path("", include("apps.main.urls")),
    path("blog/", include("apps.blog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
