from copy import deepcopy

DEFAULT_STOREFRONT_SITE: dict[str, object] = {
    "brand": {"name": "Meridian Nexus", "mark": "MN"},
    "announcement": "Web Development · Automation · AI Creative Solutions",
    "navigation": [
        {"path": "/", "label": "Home"},
        {"path": "/products", "label": "Products"},
        {"path": "/journal", "label": "Journal"},
        {"path": "/about", "label": "About"},
    ],
    "contact": {"email": "hello@meridian-nexus.com"},
    "footer": {
        "tagline": "Websites, automation and AI solutions built for real growth.",
        "newsletter_title": "Digital Insights",
        "newsletter_text": "Practical notes about web development, automation and AI.",
        "legal": "All rights reserved.",
        "note": "Built for modern digital businesses.",
    },
    "home_hero": {
        "eyebrow": "Northstar collection",
        "title": "Objects for",
        "accent": "everyday rituals.",
        "description": "Useful forms, honest materials, and details made to last.",
        "image": "/favicon.svg",
        "image_alt": "Northstar mark",
        "cta_label": "Explore the collection",
        "cta_path": "/products",
    },
}


def storefront_site(settings: object, locale: str) -> dict[str, object]:
    site = deepcopy(DEFAULT_STOREFRONT_SITE)
    if not isinstance(settings, dict):
        return site
    locales = settings.get("locales")
    if not isinstance(locales, dict):
        return site
    configured = locales.get(locale) or locales.get("en")
    if not isinstance(configured, dict):
        return site
    return _merge(site, configured)


def _merge(defaults: dict[str, object], configured: dict[str, object]) -> dict[str, object]:
    merged = deepcopy(defaults)
    for key, value in configured.items():
        default = merged.get(key)
        if isinstance(default, dict) and isinstance(value, dict):
            merged[key] = _merge(default, value)
        elif key == "navigation":
            if _valid_navigation(value):
                merged[key] = value
        elif value is not None:
            merged[key] = value
    return merged


def _valid_navigation(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return all(
        isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and isinstance(item.get("label"), str)
        for item in value
    )
