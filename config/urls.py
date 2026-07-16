from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as media_serve

from apps.main.views import robots_txt

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("robots.txt", robots_txt, name="robots_txt"),
    path(settings.PANEL_URL, include("apps.panel.urls")),
    path("", include("apps.main.urls")),
    path("blog/", include("apps.blog.urls")),
]

# Foydalanuvchi yuklagan media fayllar (post rasmlari, profil rasmi).
# cPanel'da Apache alias sozlash qiyin bo'lgani uchun media'ni Django orqali
# xizmat qilamiz — DEBUG=False (production) bo'lganda ham ishlaydi.
urlpatterns += [
    re_path(
        r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
        media_serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
