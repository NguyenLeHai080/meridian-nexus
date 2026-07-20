from northstar.modules.storefront.content import DEFAULT_STOREFRONT_SITE, storefront_site


def test_storefront_content_falls_back_and_merges_partial_configuration() -> None:
    fallback = storefront_site({}, "en")
    configured = storefront_site(
        {"locales": {"en": {"announcement": "Configured", "brand": {"name": "Meridian"}}}},
        "en",
    )

    assert fallback == DEFAULT_STOREFRONT_SITE
    assert fallback is not DEFAULT_STOREFRONT_SITE
    assert configured["announcement"] == "Configured"
    assert configured["brand"] == {"name": "Meridian", "mark": "MN"}
    assert configured["navigation"] == DEFAULT_STOREFRONT_SITE["navigation"]


def test_storefront_content_rejects_malformed_navigation() -> None:
    site = storefront_site({"locales": {"en": {"navigation": {"bad": "shape"}}}}, "en")

    assert site["navigation"] == DEFAULT_STOREFRONT_SITE["navigation"]
