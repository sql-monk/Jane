"""Verify quotations, preserve provenance, and give precise events a shared key."""

from __future__ import annotations

import base64
import copy
import hashlib
import html
import json
import re
import unicodedata
from collections.abc import Mapping
from datetime import date, datetime
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qsl, urljoin, urlsplit

_SKIP = {"script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form", "head"}
_VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class _Text(HTMLParser):
    def __init__(self, post: str | None = None) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.post = post
        self.stack: list[dict[str, Any]] = []
        self.primary: list[list[str]] = []
        self.headlines: list[str] = []
        self.canonicals: list[str] = []
        self.ld: list[list[str]] = []
        self.post_found = False
        self.published: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        parent = self.stack[-1] if self.stack else {}
        if (
            tag == "link"
            and "canonical" in str(values.get("rel", "")).casefold().split()
            and values.get("href")
        ):
            self.canonicals.append(str(values["href"]))
        if tag == "meta" and values.get("property") == "og:title" and values.get("content"):
            self.headlines.append(str(values["content"]))
        meta_key = str(
            values.get("property") or values.get("name") or values.get("itemprop") or ""
        ).casefold()
        if (
            tag == "meta"
            and meta_key in {"article:published_time", "datepublished", "date", "pubdate"}
            and values.get("content")
            and not self.post
            and (
                any(frame["tag"] == "head" for frame in self.stack)
                or (parent.get("primary") == 0 and not parent.get("skip"))
            )
        ):
            self.published.append(str(values["content"]))
        if (
            tag == "time"
            and values.get("datetime")
            and (
                (self.post and parent.get("post"))
                or (not self.post and parent.get("primary") == 0 and not parent.get("skip"))
            )
        ):
            self.published.append(str(values["datetime"]))
        if tag in _VOID:
            return
        frame = {
            "tag": tag,
            "skip": bool(parent.get("skip")) or tag in _SKIP,
            "primary": parent.get("primary"),
            "post": bool(parent.get("post")),
            "post_body": bool(parent.get("post_body")),
            "ld": parent.get("ld"),
            "h1": bool(parent.get("h1")) or tag == "h1",
        }
        if self.post and str(values.get("data-post") or "").casefold() == self.post.casefold():
            self.post_found = frame["post"] = True
        class_tokens = set(str(values.get("class") or "").split())
        if frame["post"] and "tgme_widget_message_text" in class_tokens:
            frame["post_body"] = True
        if class_tokens & {
            "tgme_widget_message_reply",
            "tgme_widget_message_link_preview",
            "tgme_widget_message_footer",
            "tgme_widget_message_author",
        }:
            frame["skip"] = True
        classes = str(values.get("class") or "") + " " + str(values.get("id") or "")
        if (
            not frame["skip"]
            and frame["primary"] is None
            and (
                tag == "article"
                or values.get("itemprop") == "articleBody"
                or re.search(
                    r"(?:article|story|news)[_-]?(?:body|text|content)|(?:entry|post)[_-]content",
                    classes,
                    re.I,
                )
            )
        ):
            frame["primary"] = len(self.primary)
            self.primary.append([])
        if tag == "script" and "ld+json" in str(values.get("type", "")):
            frame["ld"] = len(self.ld)
            self.ld.append([])
        self.stack.append(frame)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        frame = self.stack[-1] if self.stack else {}
        if frame.get("ld") is not None:
            self.ld[frame["ld"]].append(data)
        if frame.get("skip") or (self.post and not frame.get("post_body")):
            return
        self.parts.append(data)
        if frame.get("primary") is not None:
            self.primary[frame["primary"]].append(data)
        if frame.get("h1"):
            self.headlines.append(data)

    def visible(self, material: Mapping[str, Any] | None = None, article_url: str = "") -> str:
        if self.post:
            return " ".join(self.parts)
        bodies: list[str] = []
        headlines = list(self.headlines)
        for record in _primary_articles(self, material or {}, article_url):
            if record.get("articleBody"):
                bodies.append(str(record["articleBody"]))
                if record.get("headline"):
                    headlines.append(str(record["headline"]))
        if bodies:
            return " ".join([*headlines, max(bodies, key=len)])
        if self.primary:
            return " ".join([*headlines, *self.primary[0]])
        return " ".join(self.parts)


def _json_articles(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [record for child in value for record in _json_articles(child)]
    if not isinstance(value, dict):
        return []
    types = value.get("@type", [])
    types = [types] if isinstance(types, str) else types
    records = [value] if any(str(kind).endswith(("Article", "BlogPosting")) for kind in types) else []
    for key in ("@graph", "mainEntity"):
        if value.get(key):
            records.extend(_json_articles(value[key]))
    return records


def _primary_articles(
    parser: _Text, material: Mapping[str, Any], article_url: str = ""
) -> list[dict[str, Any]]:
    locator = material.get("locator") or {}
    urls = [str(locator[key]) for key in ("url", "final_url", "canonical_url") if locator.get(key)]
    if article_url:
        urls.append(article_url)
    base = urls[0] if urls else ""
    allowed_hosts = {urlsplit(url).hostname for url in urls}
    urls.extend(
        urljoin(base, value)
        for value in parser.canonicals
        if urlsplit(urljoin(base, value)).hostname in allowed_hosts
    )

    def identity(url: str) -> tuple[str, str, str]:
        parsed = urlsplit(urljoin(base, url))
        return str(parsed.hostname).casefold().removeprefix("www."), parsed.path.rstrip("/"), parsed.query

    identities = {identity(url) for url in urls}
    matched: list[dict[str, Any]] = []
    anonymous: list[dict[str, Any]] = []
    total = 0
    for raw in parser.ld:
        try:
            records = _json_articles(json.loads("".join(raw)))
        except ValueError:
            continue
        for record in records:
            total += 1
            links = []
            for field in ("url", "@id", "mainEntityOfPage"):
                value = record.get(field)
                if isinstance(value, dict):
                    value = value.get("@id") or value.get("url")
                if isinstance(value, str):
                    links.append(value)
            if links:
                if any(identity(link) in identities for link in links):
                    matched.append(record)
            else:
                anonymous.append(record)
    if matched:
        return matched
    if total == 1 and len(anonymous) == 1:
        record = anonymous[0]
        headline = _clean(str(record.get("headline", "")))
        if headline and (
            record.get("articleBody") or headline in {_clean(value) for value in parser.headlines}
        ):
            return [record]
    return []


def _inline_text(material: Mapping[str, Any], ctx: Any = None) -> str | None:
    content = material.get("content") or {}
    if content.get("kind") == "blob" and ctx is not None:
        try:
            payload = ctx.bytes()
        except RuntimeError:
            return None
        charset = content.get("charset") or (material.get("format") or {}).get("charset") or "utf-8"
        return str(payload.decode(charset))
    if content.get("kind") != "inline":
        return None
    value = str(content.get("data", ""))
    if content.get("encoding") == "base64":
        value = base64.b64decode(value, validate=True).decode(content.get("charset") or "utf-8")
    return value


def _clean(value: str) -> str:
    text = " ".join(unicodedata.normalize("NFKC", html.unescape(value)).split())
    return re.sub(r"\s+([,.;:!?])", r"\1", text)


def _source_text(
    material: Mapping[str, Any], article_url: str = "", raw_text: str | None = None
) -> str | None:
    value = raw_text if raw_text is not None else _inline_text(material)
    if value is None:
        return None
    media = (material.get("format") or {}).get("media_type", "")
    if media in {"text/html", "application/xhtml+xml"}:
        parsed_url = urlsplit(article_url)
        parts = parsed_url.path.strip("/").split("/")
        if parts and parts[0] == "s":
            parts = parts[1:]
        post = "/".join(parts) if parsed_url.hostname == "t.me" and len(parts) == 2 else None
        parser = _Text(post)
        parser.feed(value)
        value = parser.visible(material, article_url)
    elif media == "application/json":
        try:
            parsed = json.loads(value)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            value = (
                " ".join(
                    str(parsed[key]) for key in ("text", "message", "caption", "title") if parsed.get(key)
                )
                or value
            )
    return _clean(value)


def _canonical(value: str) -> str:
    return re.sub(r"[\W_]+", " ", _clean(value).casefold()).strip()


def _telegram_source(material: Mapping[str, Any]) -> bool:
    locator = material.get("locator") or {}
    return any(
        urlsplit(str(locator.get(key) or "")).hostname in {"t.me", "telegram.me"}
        for key in ("url", "final_url", "canonical_url")
    )


def _validate_url(
    url: str, material: Mapping[str, Any], source_kind: str, raw_text: str | None = None
) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("article URL must be an HTTP(S) source URL without credentials")
    locator = material.get("locator") or {}
    originals = [urlsplit(locator[key]) for key in ("url", "final_url", "canonical_url") if locator.get(key)]
    if not originals:
        return
    host = parsed.hostname.casefold().removeprefix("www.")
    if host not in {str(value.hostname).casefold().removeprefix("www.") for value in originals}:
        raise ValueError("article URL is outside the original source host")
    if _telegram_source(material):
        parts = parsed.path.strip("/").split("/")
        if parts and parts[0] == "s":
            parts = parts[1:]
        original_channels = set()
        for value in originals:
            path = value.path.strip("/").split("/")
            if path and path[0] == "s":
                path = path[1:]
            if path:
                original_channels.add(path[0].casefold())
        if len(parts) != 2 or not parts[1].isdigit() or parts[0].casefold() not in original_channels:
            raise ValueError("Telegram article URL must identify a post in the original channel")
        raw = raw_text if raw_text is not None else _inline_text(material)
        if raw is not None:
            parser = _Text("/".join(parts))
            parser.feed(raw)
            if not parser.post_found:
                raise ValueError("Telegram article URL must identify a post present in the original material")
        return
    raw = raw_text if raw_text is not None else _inline_text(material)
    if raw and (material.get("format") or {}).get("media_type") in {"text/html", "application/xhtml+xml"}:
        parser = _Text()
        parser.feed(raw)
        base = locator.get("final_url") or locator.get("url") or locator.get("canonical_url") or ""
        for href in parser.canonicals:
            candidate = urlsplit(urljoin(base, href))
            if str(candidate.hostname).casefold().removeprefix("www.") == host:
                originals.append(candidate)

    def identity(value: Any) -> tuple[str, tuple[tuple[str, str], ...]]:
        query = tuple(
            sorted(
                (key, item)
                for key, item in parse_qsl(value.query, keep_blank_values=True)
                if not key.casefold().startswith("utm_") and key.casefold() not in {"fbclid", "gclid"}
            )
        )
        return value.path.rstrip("/") or "/", query

    if identity(parsed) not in {identity(value) for value in originals}:
        raise ValueError("article URL is not the original or verified canonical article URL")


_GENERIC_OBJECT_WORDS = {
    "the",
    "a",
    "an",
    "military",
    "civilian",
    "industrial",
    "international",
    "national",
    "local",
    "airport",
    "airports",
    "warehouse",
    "warehouses",
    "building",
    "buildings",
    "facility",
    "facilities",
    "city",
    "cities",
    "country",
    "countries",
    "territory",
    "war",
    "politics",
    "conflict",
    "infrastructure",
    "people",
    "victims",
    "civilians",
    "soldiers",
    "aid",
    "event",
    "meeting",
    "attack",
    "strike",
}
_WEEKDAYS = (
    r"\bmonday\b|\bпонеділ\w*|\bпонедель\w*",
    r"\btuesday\b|\bвівтор\w*|\bвторник\w*",
    r"\bwednesday\b|\bсеред\w*|\bсред[ау]\w*",
    r"\bthursday\b|\bчетвер\w*",
    r"\bfriday\b|\bп[’'ʼ]?ятниц\w*|\bпятниц\w*",
    r"\bsaturday\b|\bсубот\w*|\bсуббот\w*",
    r"\bsunday\b|\bнеділ\w*|\bвоскресен\w*",
)
_MONTHS = (
    r"january|jan|січ\w*|январ\w*",
    r"february|feb|лют\w*|феврал\w*",
    r"march|mar|берез\w*|март\w*",
    r"april|apr|квіт\w*|апрел\w*",
    r"may|трав\w*|ма[йя]",
    r"june|jun|черв\w*|июн\w*",
    r"july|jul|лип\w*|июл\w*",
    r"august|aug|серп\w*|август\w*",
    r"september|sep|sept|верес\w*|сентябр\w*",
    r"october|oct|жовт\w*|октябр\w*",
    r"november|nov|листопад\w*|ноябр\w*",
    r"december|dec|груд\w*|декабр\w*",
)


def _publication_dates(material: Mapping[str, Any], raw_text: str | None, article_url: str = "") -> set[date]:
    timestamps = [str(material["published_at"])] if material.get("published_at") else []
    if raw_text and (material.get("format") or {}).get("media_type") in {
        "text/html",
        "application/xhtml+xml",
    }:
        parsed = urlsplit(article_url)
        parts = parsed.path.strip("/").split("/")
        post = (
            "/".join(parts) if parsed.hostname == "t.me" and len(parts) == 2 and parts[1].isdigit() else None
        )
        parser = _Text(post)
        parser.feed(raw_text)
        linked_published = [
            str(record["datePublished"])
            for record in _primary_articles(parser, material, article_url)
            if record.get("datePublished")
        ]
        timestamps.extend(linked_published or parser.published)
    dates = set()
    for timestamp in timestamps:
        try:
            dates.add(datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date())
        except ValueError:
            continue
    return dates


def _explicit_date_in_quote(value: date, quote: str) -> bool:
    if value.isoformat() in quote or f"{value.day:02d}.{value.month:02d}.{value.year}" in quote:
        return True
    month = _MONTHS[value.month - 1]
    return bool(
        re.search(
            rf"\b{value.day}\s+(?:{month})\s+{value.year}\b|\b(?:{month})\s+{value.day}(?:st|nd|rd|th)?[,]?\s+{value.year}\b",
            quote,
            re.I,
        )
    )


def _date_resolution(
    event: Mapping[str, Any],
    source_text: str,
    material: Mapping[str, Any],
    raw_text: str | None,
    article_url: str = "",
) -> str | None:
    """Incident dates require a checked date quote; publication alone never creates a date."""
    if event.get("identity_kind", "actor_action") != "incident":
        return None
    resolution = event.get("date_resolution") or {}
    original_quote = _clean(str(resolution.get("quote", "")))
    if not original_quote or original_quote not in source_text:
        return "unverified_event_date"
    quote = original_quote.casefold()
    try:
        value = date.fromisoformat((event.get("canonical") or {})["date"])
    except (ValueError, KeyError, TypeError):
        return "invalid_event_date"
    method = resolution.get("method")
    if method == "explicit":
        return None if _explicit_date_in_quote(value, quote) else "unverified_event_date"
    if method not in {"publication_weekday", "publication_today"}:
        return "unverified_event_date"
    publication_dates = _publication_dates(material, raw_text, article_url)
    if len(publication_dates) != 1 or value not in publication_dates:
        return "ambiguous_relative_event_date"
    reference = resolution.get("reference_published_at")
    try:
        reference_date = datetime.fromisoformat(str(reference).replace("Z", "+00:00")).date()
    except ValueError:
        return "unverified_publication_date"
    if reference_date != value:
        return "unverified_publication_date"
    if re.search(r"\b(?:last|previous|next)\b|минул\w*|прошл\w*|наступ\w*|следующ\w*", quote):
        return "ambiguous_relative_event_date"
    if method == "publication_today":
        return None if re.search(r"\btoday\b|\bсьогодн\w*|\bсегодня\b", quote) else "unverified_event_date"
    weekdays = {index for index, pattern in enumerate(_WEEKDAYS) if re.search(pattern, quote)}
    return None if weekdays == {value.weekday()} else "ambiguous_relative_event_date"


def _incident_time(event: Mapping[str, Any], source_text: str) -> str | None:
    canonical = event.get("canonical") or {}
    if event.get("identity_kind") != "incident":
        return None
    if not canonical.get("time"):
        quotes = [str(evidence.get("quote", "")) for evidence in event.get("evidence") or []]
        quotes.append(str((event.get("date_resolution") or {}).get("quote", "")))
        if any(
            re.search(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b|\b\d{1,2}\s*[ap]\.?\s*m\.?", quote, re.I)
            for quote in quotes
        ):
            return "missing_incident_time_discriminator"
        return None
    value = str(canonical["time"])
    if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value):
        return "invalid_incident_time"
    quote = _clean(str((event.get("time_evidence") or {}).get("quote", "")))
    if not quote or quote not in source_text:
        return "unverified_incident_time"
    hour, minute = value.split(":")
    clock = rf"\b0?{int(hour)}:{minute}\b"
    if minute == "00":
        display = int(hour) % 12 or 12
        suffix = r"a\.?\s*m\.?" if int(hour) < 12 else r"p\.?\s*m\.?"
        clock += rf"|\b{display}(?::00)?\s*{suffix}"
    return None if re.search(clock, quote, re.I) else "unverified_incident_time"


def event_identity(event: Mapping[str, Any], min_confidence: float) -> tuple[str | None, str]:
    """Exact identity is separate from broad topics and approximate candidate signatures."""
    canonical = event.get("canonical") or {}
    if float(event.get("identity_confidence", 0)) < min_confidence:
        return None, "low_identity_confidence"
    identity_kind = event.get("identity_kind", "actor_action")
    if identity_kind not in {"incident", "actor_action"}:
        return None, "unknown_identity_kind"
    fields = (
        ("date", "action", "object", "location", "country")
        if identity_kind == "incident"
        else ("date", "primary_actor", "action", "object", "location")
    )
    if any(not isinstance(canonical.get(key), str) or not canonical[key].strip() for key in fields):
        return None, "incomplete_event_identity"
    if any(
        _canonical(canonical[key]) in {"unknown", "unspecified", "none", "n a", "not applicable", "other"}
        for key in fields
    ):
        return None, "incomplete_event_identity"
    try:
        date.fromisoformat(canonical["date"])
    except ValueError:
        return None, "invalid_event_date"
    if event.get("identity_specificity") != "specific":
        return None, "broad_event_identity"
    if not event.get("evidence"):
        return None, "missing_event_evidence"
    if identity_kind == "incident" and set(_canonical(canonical["object"]).split()) <= _GENERIC_OBJECT_WORDS:
        return None, "generic_incident_object"
    values = {key: _canonical(canonical[key]) for key in fields}
    if identity_kind == "incident":
        values["identity_kind"] = identity_kind
        if canonical.get("time"):
            if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", str(canonical["time"])):
                return None, "invalid_incident_time"
            values["time"] = _canonical(canonical["time"])
    encoded = json.dumps(values, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "news-event-" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()[
        :32
    ], "exact_canonical_identity"


def _evidence(fields: Mapping[str, Any]) -> list[dict[str, Any]]:
    out = list((fields.get("sentiment") or {}).get("evidence") or [])
    out.extend((fields.get("event") or {}).get("evidence") or [])
    for entity in fields.get("entities") or []:
        out.extend(entity.get("evidence") or [])
    return out


def normalize(handler_input: dict[str, Any], params: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """The SDK passes the whole EntitiesInput to transforms; its Material is optional."""
    if handler_input.get("kind") != "entities":
        raise ValueError("news.article-normalize expects an entities input")
    incoming = handler_input.get("entities") or []
    if not incoming:
        return {"status": "empty", "entities": []}
    material = handler_input.get("material") or {}
    raw_text = _inline_text(material, ctx) if material else None
    strict = bool(params.get("require_verified_evidence", True))
    minimum = float(params.get("min_grouping_confidence", 0.9))
    out: list[dict[str, Any]] = []
    for original in incoming:
        if original.get("entity_type") != "news_article":
            continue
        record = copy.deepcopy(original)
        fields = record["fields"]
        source_text = _source_text(material, fields.get("url", ""), raw_text) if material else None
        if source_text is None and strict:
            raise ValueError(
                "quotation verification requires inline content or a runtime-loaded original blob"
            )
        material_id = material.get("material_id") or fields.get("material_id")
        if not material_id:
            raise ValueError("article is missing material_id")
        fields["material_id"] = material_id
        if material:
            source = material.get("source") or {}
            fields["source_id"] = (
                params.get("source_id")
                or source.get("source_id")
                or record.get("key", {}).get("scope", "local")
            )
            fields["source_name"] = (
                params.get("source_name")
                or fields.get("source_name")
                or source.get("name")
                or fields["source_id"]
            )
            fields["source_kind"] = (
                params.get("source_kind") or fields.get("source_kind") or source.get("kind", "web")
            )
            if _telegram_source(material):
                fields["source_kind"] = "telegram"
                fields["transport"] = "telegram_public_web"
            for key in ("region", "transport"):
                if params.get(key):
                    fields[key] = params[key]
            locator = material.get("locator") or {}
            url = (
                fields.get("url")
                or locator.get("canonical_url")
                or locator.get("final_url")
                or locator.get("url")
            )
            if url:
                fields["url"] = url
                _validate_url(url, material, fields["source_kind"], raw_text)
            for key in ("published_at", "fetched_at", "edited_at"):
                if material.get(key) and (key == "fetched_at" or not fields.get(key)):
                    fields[key] = material[key]
            digest = (material.get("revision") or {}).get("content_sha256")
            if digest:
                fields["content_sha256"] = digest
        if source_text is not None:
            for evidence in _evidence(fields):
                quote = _clean(str(evidence.get("quote", "")))
                if not quote or quote not in source_text:
                    raise ValueError("analysis evidence quotation is absent from the original material")
            for entity in fields.get("entities") or []:
                if entity.get("attitude") in {"positive", "negative"} and not any(
                    evidence.get("attribution") == "author" for evidence in entity.get("evidence") or []
                ):
                    raise ValueError("non-neutral entity attitude requires evidence of the author's framing")
            sentiment = fields.get("sentiment") or {}
            if sentiment.get("label") in {"positive", "negative"} and not any(
                evidence.get("attribution") == "author" for evidence in sentiment.get("evidence") or []
            ):
                raise ValueError("non-neutral overall sentiment requires evidence of the author's framing")
            fields["evidence_validation"] = "verified"
        else:
            fields["evidence_validation"] = "unavailable"
        fields["analysis_language"] = "uk"
        if not fields.get("url"):
            raise ValueError("article is missing its exact URL")
        record["key"] = {
            "scope": fields.get("source_id") or record.get("key", {}).get("scope", "local"),
            "natural": {"url": fields["url"]},
        }
        event = fields.get("event") or {}
        event_id, reason = event_identity(event, minimum)
        if source_text is not None and (
            date_reason := _date_resolution(event, source_text, material, raw_text, fields.get("url", ""))
        ):
            event_id, reason = None, date_reason
        if source_text is not None and (time_reason := _incident_time(event, source_text)):
            event_id, reason = None, time_reason
        if fields["evidence_validation"] != "verified":
            event_id, reason = None, "unverified_event_evidence"
        fields.pop("event_id", None)
        cleared = set(record.get("cleared") or [])
        if event_id:
            cleared.discard("event_id")
        else:
            cleared.add("event_id")
        if cleared:
            record["cleared"] = sorted(cleared)
        else:
            record.pop("cleared", None)
        fields["event_grouping"] = {
            "status": "grouped" if event_id else "ungrouped",
            "method": "exact_canonical_identity",
            "reason": reason,
        }
        if event_id:
            fields["event_id"] = event_id
            shared_canonical = copy.deepcopy(event["canonical"])
            if event.get("identity_kind") == "incident":
                shared_canonical.pop("primary_actor", None)
            shared = {
                "entity_type": "news_event",
                "key": {"scope": params.get("event_scope", "news-events"), "natural": {"event_id": event_id}},
                "fields": {
                    "event_id": event_id,
                    "summary": event["summary"],
                    "canonical": shared_canonical,
                    "identity_confidence": event["identity_confidence"],
                    "grouping_method": "exact_canonical_identity",
                    "identity_kind": event.get("identity_kind", "actor_action"),
                },
            }
            if record.get("observation"):
                shared["observation"] = copy.deepcopy(record["observation"])
            out.append(shared)
        out.append(record)
    return {"status": "success" if out else "empty", "entities": out}
