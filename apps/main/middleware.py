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
