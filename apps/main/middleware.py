import hashlib

from django.conf import settings
from django.db.models import F
from django.utils import timezone


class IPBlockMiddleware:
    """Bloklangan IP'lardan kelgan so'rovlarni 403 bilan rad etadi."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = self._client_ip(request)
        if client_ip:
            from apps.main.models import BlockedIP

            if client_ip in BlockedIP.blocked_set():
                from django.http import HttpResponseForbidden

                return HttpResponseForbidden(
                    "<h1>403 Forbidden</h1><p>Sizning IP manzilingiz bloklangan.</p>"
                )
        return self.get_response(request)

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class VisitTrackingMiddleware:
    """Sahifa ko'rishlarini VisitorSession + PageVisit ga yozadi.

    Botlar ham yoziladi, lekin `is_bot` bayrog'i bilan belgilanadi - shunda
    ularni statistikadan filtrlash mumkin. 404 sahifalar ham kuzatiladi.
    Xatolik hech qachon sahifani buzmasligi kerak.
    """

    # Kuzatilmaydigan yo'llar (statik fayllar, boshqaruv paneli va h.k.)
    STATIC_PREFIXES = ("/static", "/media", "/favicon", "/robots.txt")
    # Kuzatiladigan javob kodlari (404 - "topilmadi" statistikasi uchun)
    TRACKED_STATUS = (200, 404)

    def __init__(self, get_response):
        self.get_response = get_response
        # Admin va panel manzillari env orqali o'zgarishi mumkin
        self.skip_prefixes = self.STATIC_PREFIXES + (
            f"/{settings.ADMIN_URL}".rstrip("/"),
            f"/{settings.PANEL_URL}".rstrip("/"),
        )

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record(request, response)
        except Exception:
            # Analytics hech qachon sahifani buzmasligi kerak.
            pass
        return response

    def _record(self, request, response):
        if request.method != "GET":
            return
        if response.status_code not in self.TRACKED_STATUS:
            return

        path = request.path
        if any(path.startswith(prefix) for prefix in self.skip_prefixes):
            return
        if "text/html" not in response.get("Content-Type", ""):
            return

        from apps.main.models import PageVisit, VisitorSession
        from apps.main.tracking import classify_referer, detect_bot, parse_user_agent

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        ip = self._client_ip(request)
        is_bot, bot_name = detect_bot(user_agent)
        session_key = self._session_key(request, is_bot, ip, user_agent)
        if not session_key:
            return

        referer = request.META.get("HTTP_REFERER", "")
        path = path[:255]

        session_obj, created = VisitorSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                "ip_address": ip,
                "user_agent": user_agent,
                "is_bot": is_bot,
                "bot_name": bot_name,
                "language": self._language(request),
                "referer": referer,
                "referer_source": classify_referer(referer, request.get_host()),
                "landing_page": path,
                "exit_page": path,
                **parse_user_agent(user_agent, is_bot=is_bot),
            },
        )

        # Sessiyani yangilaymiz: oxirgi sahifa, ko'rishlar soni, faollik vaqti.
        # F() ishlatamiz - parallel so'rovlarda hisob buzilmasligi uchun.
        VisitorSession.objects.filter(pk=session_obj.pk).update(
            exit_page=path,
            page_count=F("page_count") + 1,
            last_activity=timezone.now(),
        )

        PageVisit.objects.create(
            session=session_obj,
            path=path,
            ip_address=ip,
            session_key=session_key,
            user_agent=user_agent[:300],
            referrer=referer[:300],
            is_authenticated=request.user.is_authenticated,
            status_code=response.status_code,
            is_bot=is_bot,
        )

    @staticmethod
    def _session_key(request, is_bot, ip, user_agent):
        """Sessiya kalitini qaytaradi.

        Botlar cookie saqlamaydi - ular uchun har so'rovda yangi Django
        sessiyasi yaratilsa, baza shishadi. Shuning uchun botlarga IP + UA
        asosida barqaror sintetik kalit beriladi.
        """
        if is_bot:
            raw = f"bot:{ip}:{user_agent}".encode("utf-8", "ignore")
            return hashlib.sha1(raw).hexdigest()[:40]

        if not request.session.session_key:
            request.session.save()
        return request.session.session_key or ""

    @staticmethod
    def _language(request):
        """Accept-Language sarlavhasidan asosiy tilni oladi."""
        raw = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        if not raw:
            return ""
        return raw.split(",")[0].strip()[:20]

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class SiteLanguageMiddleware:
    SUPPORTED_LANGS = {"uz", "en"}
    DEFAULT_LANG = "uz"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get("lang", "").strip().lower()
        if lang in self.SUPPORTED_LANGS:
            request.session["site_lang"] = lang

        request.site_lang = request.session.get("site_lang", self.DEFAULT_LANG)
        if request.site_lang not in self.SUPPORTED_LANGS:
            request.site_lang = self.DEFAULT_LANG

        response = self.get_response(request)
        return response
