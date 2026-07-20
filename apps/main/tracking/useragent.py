"""User-Agent tahlili: brauzer, operatsion tizim va qurilma.

`user_agents` kutubxonasi ustida ishlaydi. Kutubxona topilmasa yoki UA
tahlil qilinmasa, bo'sh qiymatlar qaytadi - kuzatuv hech qachon sahifani
buzmasligi kerak.
"""

try:
    from user_agents import parse as _ua_parse
except ImportError:  # pragma: no cover - kutubxona bo'lmasa ham ishlaydi
    _ua_parse = None


# Qurilma turlari
DEVICE_MOBILE = "mobile"
DEVICE_TABLET = "tablet"
DEVICE_DESKTOP = "desktop"
DEVICE_BOT = "bot"
DEVICE_OTHER = "other"

DEVICE_CHOICES = (
    (DEVICE_MOBILE, "Telefon"),
    (DEVICE_TABLET, "Planshet"),
    (DEVICE_DESKTOP, "Kompyuter"),
    (DEVICE_BOT, "Bot"),
    (DEVICE_OTHER, "Boshqa"),
)

_EMPTY = {
    "browser": "",
    "browser_version": "",
    "os": "",
    "os_version": "",
    "device_type": DEVICE_OTHER,
    "device_model": "",
}


def _clean(value):
    """user_agents 'Other' deb qaytargan qiymatlarni bo'shga aylantiradi."""
    if not value or value == "Other":
        return ""
    return str(value)[:60]


def parse_user_agent(user_agent, is_bot=False):
    """UA satrini tahlil qilib lug'at qaytaradi.

    Args:
        user_agent: xom User-Agent satri.
        is_bot: bot aniqlangan bo'lsa, qurilma turi 'bot' qilinadi.

    Returns:
        dict: browser, browser_version, os, os_version, device_type, device_model
    """
    result = dict(_EMPTY)

    if is_bot:
        result["device_type"] = DEVICE_BOT

    if not user_agent or _ua_parse is None:
        return result

    try:
        ua = _ua_parse(user_agent)
    except Exception:
        # Buzuq UA satri kuzatuvni to'xtatmasligi kerak
        return result

    result["browser"] = _clean(ua.browser.family)
    result["browser_version"] = _clean(ua.browser.version_string)[:30]
    result["os"] = _clean(ua.os.family)
    result["os_version"] = _clean(ua.os.version_string)[:30]
    result["device_model"] = _clean(ua.device.family)[:80]

    if is_bot or ua.is_bot:
        result["device_type"] = DEVICE_BOT
    elif ua.is_tablet:
        result["device_type"] = DEVICE_TABLET
    elif ua.is_mobile:
        result["device_type"] = DEVICE_MOBILE
    elif ua.is_pc:
        result["device_type"] = DEVICE_DESKTOP
    else:
        result["device_type"] = DEVICE_OTHER

    return result
