"""Trafik manbasini (referer) aniqlash.

Referer URL'idan tashrifchi qayerdan kelganini nomlaydi:
Google, Telegram, Instagram, GitHub, Direct va h.k.
"""

from urllib.parse import urlparse

SOURCE_DIRECT = "Direct"
SOURCE_INTERNAL = "Internal"

# (domen ichida qidiriladigan bo'lak, ko'rsatiladigan nom)
REFERER_SOURCES = (
    # Qidiruv tizimlari
    ("google.", "Google"),
    ("bing.", "Bing"),
    ("yandex.", "Yandex"),
    ("duckduckgo.", "DuckDuckGo"),
    ("yahoo.", "Yahoo"),
    ("baidu.", "Baidu"),
    ("ecosia.", "Ecosia"),
    ("brave.", "Brave Search"),
    # Ijtimoiy tarmoqlar / messenjerlar
    ("t.me", "Telegram"),
    ("telegram.", "Telegram"),
    ("instagram.", "Instagram"),
    ("facebook.", "Facebook"),
    ("fb.com", "Facebook"),
    ("fb.me", "Facebook"),
    ("twitter.", "Twitter/X"),
    ("x.com", "Twitter/X"),
    ("t.co", "Twitter/X"),
    ("linkedin.", "LinkedIn"),
    ("lnkd.in", "LinkedIn"),
    ("youtube.", "YouTube"),
    ("youtu.be", "YouTube"),
    ("tiktok.", "TikTok"),
    ("whatsapp.", "WhatsApp"),
    ("reddit.", "Reddit"),
    ("pinterest.", "Pinterest"),
    ("vk.com", "VK"),
    ("discord.", "Discord"),
    ("threads.", "Threads"),
    # Dasturchilar platformalari
    ("github.", "GitHub"),
    ("gitlab.", "GitLab"),
    ("stackoverflow.", "Stack Overflow"),
    ("dev.to", "DEV.to"),
    ("medium.", "Medium"),
    ("habr.", "Habr"),
    ("hashnode.", "Hashnode"),
    ("news.ycombinator.com", "Hacker News"),
    # AI
    ("chatgpt.", "ChatGPT"),
    ("chat.openai.com", "ChatGPT"),
    ("claude.ai", "Claude"),
    ("perplexity.", "Perplexity"),
    ("gemini.google", "Gemini"),
)


def classify_referer(referer, host=None):
    """Referer URL'idan trafik manbasini aniqlaydi.

    Args:
        referer: xom HTTP_REFERER qiymati.
        host: joriy sayt hosti (o'z-o'ziga havolani 'Internal' deb belgilash uchun).

    Returns:
        str: manba nomi ("Google", "Telegram", "Direct", "Internal" yoki domen).
    """
    if not referer:
        return SOURCE_DIRECT

    try:
        netloc = urlparse(referer).netloc.lower()
    except Exception:
        return SOURCE_DIRECT

    if not netloc:
        return SOURCE_DIRECT

    # Portni olib tashlaymiz (example.com:8000 -> example.com)
    domain = netloc.split(":")[0]

    if host:
        host_domain = host.split(":")[0].lower()
        if domain == host_domain or domain == f"www.{host_domain}":
            return SOURCE_INTERNAL

    for needle, name in REFERER_SOURCES:
        if needle in domain:
            return name

    # Noma'lum manba - domenning o'zini qaytaramiz (www. olib tashlanadi)
    return domain[4:][:40] if domain.startswith("www.") else domain[:40]
