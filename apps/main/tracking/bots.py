"""Bot / crawler aniqlash.

User-Agent satridan ma'lum crawlerlarni nomi bilan aniqlaydi. Ro'yxatda
bo'lmagan, lekin "bot"/"crawler"/"spider" so'zi bor UA'lar umumiy bot deb
belgilanadi.
"""

# (UA ichida qidiriladigan kichik harfli bo'lak, ko'rsatiladigan nom)
# Tartib muhim: aniqroq mos keluvchilar yuqorida turadi.
BOT_SIGNATURES = (
    # Qidiruv tizimlari
    ("googlebot", "Googlebot"),
    ("google-inspectiontool", "Googlebot"),
    ("adsbot-google", "Googlebot"),
    ("mediapartners-google", "Googlebot"),
    ("bingbot", "Bingbot"),
    ("adidxbot", "Bingbot"),
    ("yandexbot", "YandexBot"),
    ("yandexaccessibilitybot", "YandexBot"),
    ("duckduckbot", "DuckDuckBot"),
    ("baiduspider", "Baiduspider"),
    ("slurp", "Yahoo Slurp"),
    ("applebot", "Applebot"),
    ("petalbot", "PetalBot"),
    ("seznambot", "SeznamBot"),
    # AI / LLM crawlerlar
    ("gptbot", "GPTBot"),
    ("oai-searchbot", "OpenAI SearchBot"),
    ("chatgpt-user", "ChatGPT-User"),
    ("claudebot", "ClaudeBot"),
    ("claude-web", "ClaudeBot"),
    ("anthropic-ai", "ClaudeBot"),
    ("perplexitybot", "PerplexityBot"),
    ("ccbot", "CCBot"),
    ("bytespider", "Bytespider"),
    ("google-extended", "Google-Extended"),
    ("amazonbot", "AmazonBot"),
    ("meta-externalagent", "Meta AI"),
    # SEO / marketing
    ("ahrefsbot", "AhrefsBot"),
    ("semrushbot", "SemrushBot"),
    ("mj12bot", "MJ12bot"),
    ("dotbot", "DotBot"),
    ("rogerbot", "Rogerbot"),
    ("screaming frog", "Screaming Frog"),
    ("dataforseobot", "DataForSeoBot"),
    # Ijtimoiy tarmoq preview botlari
    ("facebookexternalhit", "FacebookBot"),
    ("facebookcatalog", "FacebookBot"),
    ("facebot", "FacebookBot"),
    ("twitterbot", "Twitterbot"),
    ("linkedinbot", "LinkedInBot"),
    ("telegrambot", "TelegramBot"),
    ("whatsapp", "WhatsApp"),
    ("discordbot", "Discordbot"),
    ("slackbot", "Slackbot"),
    ("pinterest", "Pinterestbot"),
    ("redditbot", "Redditbot"),
    # Skanerlar / xavfsizlik tadqiqotchilari
    ("shodan", "Shodan"),
    ("censys", "Censys"),
    ("masscan", "Masscan"),
    ("nmap", "Nmap"),
    ("zgrab", "ZGrab"),
    ("nikto", "Nikto"),
    ("sqlmap", "sqlmap"),
    ("nuclei", "Nuclei"),
    ("wpscan", "WPScan"),
    ("dirbuster", "DirBuster"),
    ("gobuster", "Gobuster"),
    # Monitoring
    ("uptimerobot", "UptimeRobot"),
    ("pingdom", "Pingdom"),
    ("statuscake", "StatusCake"),
    ("betteruptime", "BetterUptime"),
    # Skript / kutubxona klientlari
    ("python-requests", "python-requests"),
    ("python-urllib", "urllib"),
    ("aiohttp", "aiohttp"),
    ("httpx", "httpx"),
    ("scrapy", "Scrapy"),
    ("go-http-client", "Go HTTP client"),
    ("java/", "Java client"),
    ("okhttp", "OkHttp"),
    ("curl/", "curl"),
    ("wget", "Wget"),
    ("libwww-perl", "libwww-perl"),
    ("headlesschrome", "Headless Chrome"),
    ("phantomjs", "PhantomJS"),
    ("puppeteer", "Puppeteer"),
    ("playwright", "Playwright"),
)

# Ro'yxatda yo'q, lekin bot ekanini bildiruvchi umumiy so'zlar
GENERIC_BOT_HINTS = ("bot", "crawler", "spider", "scraper", "crawl")


def detect_bot(user_agent):
    """User-Agent satridan botni aniqlaydi.

    Returns:
        (is_bot: bool, bot_name: str) - bot bo'lmasa (False, "").
    """
    if not user_agent:
        # UA umuman yo'q - deyarli har doim skript/bot
        return True, "Unknown (no UA)"

    lowered = user_agent.lower()

    for needle, name in BOT_SIGNATURES:
        if needle in lowered:
            return True, name

    for hint in GENERIC_BOT_HINTS:
        if hint in lowered:
            return True, "Other bot"

    return False, ""
