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
    """Records public page views into PageVisit for the panel analytics.

    Skips admin/panel/static assets, non-GET requests, non-HTML responses,
    and obvious bots. Failures never break the response.
    """

    SKIP_PREFIXES = ("/admin", "/panel", "/static", "/media", "/favicon")
    BOT_KEYWORDS = (
        "bot", "spider", "crawl", "slurp", "bing", "google", "yandex",
        "duckduck", "baidu", "semrush", "ahrefs", "facebookexternalhit",
        "python-requests", "curl", "wget", "headless",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record(request, response)
        except Exception:
            # Analytics must never break the page.
            pass
        return response

    def _record(self, request, response):
        if request.method != "GET" or response.status_code != 200:
            return

        path = request.path
        if any(path.startswith(prefix) for prefix in self.SKIP_PREFIXES):
            return

        if "text/html" not in response.get("Content-Type", ""):
            return

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        lowered = user_agent.lower()
        if not user_agent or any(keyword in lowered for keyword in self.BOT_KEYWORDS):
            return

        if not request.session.session_key:
            request.session.save()

        from apps.main.models import PageVisit

        PageVisit.objects.create(
            path=path[:255],
            ip_address=self._client_ip(request),
            session_key=request.session.session_key or "",
            user_agent=user_agent[:300],
            referrer=request.META.get("HTTP_REFERER", "")[:300],
            is_authenticated=request.user.is_authenticated,
        )

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
