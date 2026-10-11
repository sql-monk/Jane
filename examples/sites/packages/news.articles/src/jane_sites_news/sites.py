"""Per-site extraction rules, keyed by domain (``www.`` and other subdomains match the shorter key).

Every rule is optional except ``body``; ``params.sites`` of the stage overrides or adds domains with the same
shape (``schemas/params.schema.json``):

* ``body`` - CSS selector(s) of the article text container; several matches are joined in document order;
* ``remove`` - CSS selectors removed inside the container (ads, "read also", embeds, photo captions);
* ``title`` / ``lead`` / ``author`` / ``section`` - CSS selectors; the page metadata is the fallback;
* ``tags`` - CSS selector of tag links; ``""`` disables tags (keywords that are really categories);
* ``drop`` / ``stop`` - regular expressions: a text block that matches ``drop`` is skipped, the first one that
  matches ``stop`` ends the text (a "more news" tail).
"""

from __future__ import annotations

from typing import Any

SiteRule = dict[str, Any]

# Blocks dropped on every site: navigation phrases between paragraphs, captions, ad labels.
DROP_ALWAYS: tuple[str, ...] = (
    r"^(читайте|дивіться|слухайте) (також|більше)\b",
    r"^(читайте|слідкуйте за|підписуйтеся на|підписуйтесь на|приєднуйтесь до|приєднуйтеся до) (нас|наш|наших|новин)",
    r"^(фото|відео|ілюстративне фото|ілюстрація|джерело фото)\b.{0,100}$",  # short captions and credits
    r"^(реклама|новини партнерів)\s*:?$",
    r"^новина (доповнюється|оновлюється)",
    r"^якщо ви (виявили|знайшли) помилку",
)
STOP_ALWAYS: tuple[str, ...] = (r"^вас також можуть зацікавити",)
# Removed inside every text container before the text is read.
REMOVE_ALWAYS: tuple[str, ...] = (
    "script",
    "style",
    "noscript",
    "template",
    "iframe",
    "object",
    "embed",
    "svg",
    "button",
    "form",
    "input",
    "select",
    "textarea",
    "figure",
    "figcaption",
    "picture",
    "img",
    "video",
    "audio",
    "aside",
    "nav",
    "ins",
)

SITES: dict[str, SiteRule] = {
    "pravda.com.ua": {
        "body": "div.post_news_text, div.post_text",
        "remove": [".advtext_mob", ".nts-ad", ".nts-video-wrapper", ".media_embed"],
        "title": "h1.post_news_title, h1.post_title",
        "author": ".post_news_author a, .post_author a",
        "tags": ".post_news_tags a, .post_tags a",
    },
    "ukrinform.ua": {
        "body": "article.news div.newsText",
        "remove": ["section.read", ".mobileBanner", ".afterNewItemMobileBanner"],
        "title": "article.news h1.newsTitle",
        "lead": "article.news div.newsHeading",
        "tags": "article.news aside.tags a.tag",
    },
    "suspilne.media": {
        "body": "article.post-body div.c-art-c__c",
        "remove": [".article-image", ".post-share-box", ".c-google-preferred-source-placement", ".read-m"],
        "title": "h1.c-article-headline__inner",
        # subscription calls at the end of the Crimean Tatar news of Suspilne Crimea
        "drop": [r"abune oluñız\.?$", r"Google Haberlerinde"],
    },
    "unian.ua": {
        "body": "div.article div.article-text",
        "remove": ["div.article-text > div", "ul.js-ul-anchor", ".photo_block"],
        "title": "div.article h1",
        "lead": "div.article p.article__like-h2",
        "tags": "div.article__tags a.article__tag",
    },
    "liga.net": {
        "body": "div.article-body",
        "remove": [
            ".readtoo-sp-area",
            ".b-blocks",
            ".tags",
            ".actual",
            ".article-footer__widget",
            ".banner",
            ".page-nav",
            ".page-nav__item",
        ],
        # the same intro paragraph opens every live chronicle
        "drop": [r"^Уранці 24 лютого 2022 року Росія завдала ракетних ударів"],
        "title": "h1.article-header__title",
        "lead": ".article-header__caption",
        "tags": "div.article__tags a",
    },
    "radiosvoboda.org": {
        "body": "#article-content > div.wsw",
        "remove": ["div.wsw > div", ".wsw__embed", ".clear"],
        "title": "h1.pg-title",
        "tags": "",
    },
    "zaxid.net": {
        "body": "#newsSummary",
        "remove": [
            ".wa-channel",
            ".google-source-block",
            ".mobile-branding-wrapper",
            ".video-adv-wrapper",
            ".adv-news-within",
            ".ideal-media",
        ],
        "title": "h1#newsName",
        "lead": "h2#newsShortName",
        "tags": ".tags_item_list a",
    },
    "nv.ua": {
        "body": "div[id^='article_content_replace_']",
        "remove": [
            ".media__also__news_link",
            ".media__also__news_links",
            "[data-read-also]",
            ".media__photo__container",
            ".nts-video-wrapper",
            ".media__embed",
            ".clearfix",
            ".ad_wrapper",
        ],
        "title": "header.article__content__head h1, div.article-content-body h1",
        "lead": "div.content_wrapper > div.subtitle",
        "tags": ".article__tags a",
    },
}
