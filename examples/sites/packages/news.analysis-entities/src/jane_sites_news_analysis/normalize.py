"""Deterministic normalisation of the ``news.analysis`` output: slugs, regions, dates and the event key.

The event key groups articles and posts of different sources about one event. The LLM describes the event
with a fixed vocabulary (type, date, region, actor, parties); this module turns that description into a key
that does not depend on wording:

``<date>:<class>:<anchor>``

* ``date`` - the event date (Kyiv) as given by the LLM if it lies within a few days before the publication,
  else the publication date in Kyiv;
* ``class`` - the event type for place events (strike, combat, incident, weather) and diplomacy, ``actor`` for
  all other types (statement, decision, sports... are confused by the LLM for the same actor);
* ``anchor`` - by type: the region for place events (strike, combat, incident, weather: ISO 3166-2 code of a
  Ukrainian oblast from the gazetteer below, else the country code), the sorted state codes for diplomacy,
  the sorted actor and counterpart for sports (and diplomacy without two states), otherwise the actor (alias
  table -> code; person -> transliterated surname; country -> ISO code).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from typing import Any

PLACE_TYPES = frozenset({"strike", "combat", "incident", "weather"})
PAIR_TYPES = frozenset({"diplomacy", "sports"})
EVENT_TYPES = frozenset(
    {
        "strike",
        "combat",
        "incident",
        "weather",
        "diplomacy",
        "statement",
        "decision",
        "crime_justice",
        "economy",
        "military_aid",
        "humanitarian",
        "sports",
        "culture_science",
        "memorial",
        "other",
    }
)

_TRANSLIT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "h",
    "ґ": "g",
    "д": "d",
    "е": "e",
    "є": "ie",
    "ж": "zh",
    "з": "z",
    "и": "y",
    "і": "i",
    "ї": "i",
    "й": "i",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ь": "",
    "ю": "iu",
    "я": "ia",
    "ы": "y",
    "э": "e",
    "ё": "e",
    "ъ": "",
}
_APOSTROPHES = re.compile(r"['’ʼ`´]")
_QUOTES = re.compile(r"[\"«»“”„]")

# Organisations by normalised name (lowercase, no quotes/apostrophes) -> stable code.
ALIASES: dict[str, str] = {}
_ALIAS_GROUPS: dict[str, tuple[str, ...]] = {
    "kmda": (
        "кмда",
        "кмва",
        "київська міська державна адміністрація",
        "київська міська військова адміністрація",
        "київська міська влада",
        "влада києва",
        "київська міська рада",
    ),
    "ukrenerho": ("укренерго", "нек укренерго"),
    "henshtab-zsu": (
        "генштаб",
        "генштаб зсу",
        "генеральний штаб",
        "генеральний штаб зсу",
        "генеральний штаб збройних сил україни",
    ),
    "zsu": ("зсу", "збройні сили україни", "сили оборони", "сили оборони україни"),
    "ps-zsu": ("повітряні сили", "повітряні сили зсу", "пс зсу"),
    "mzs-ua": ("мзс україни", "мзс", "міністерство закордонних справ україни"),
    "op": ("офіс президента", "офіс президента україни", "оп"),
    "kmu": ("кабмін", "кабінет міністрів", "кабінет міністрів україни", "уряд україни"),
    "vru": ("верховна рада", "верховна рада україни", "вр", "парламент україни"),
    "sbu": ("сбу", "служба безпеки україни"),
    "nabu": ("набу", "національне антикорупційне бюро україни", "національне антикорупційне бюро"),
    "sap": ("сап", "спеціалізована антикорупційна прокуратура"),
    "nbu": ("нбу", "національний банк україни", "нацбанк"),
    "dsns": ("дснс", "державна служба з надзвичайних ситуацій", "дснс україни"),
    "npu": ("нпу", "національна поліція", "національна поліція україни", "поліція"),
    "hur": ("гур", "гур мо", "гур мо україни", "головне управління розвідки"),
    "ogp": ("офіс генпрокурора", "офіс генерального прокурора", "генпрокуратура"),
    "kreml": ("кремль",),
    "bilyi-dim": ("білий дім",),
    "eu": ("єс", "євросоюз", "європейський союз"),
    "ec": ("єк", "єврокомісія", "європейська комісія"),
    "nato": ("нато",),
    "un": ("оон", "організація обʼєднаних націй"),
    "iaea": ("магате",),
    "upl": ("упл", "українська прем'єр-ліга", "українська премʼєр-ліга"),
}
COUNTRIES: dict[str, str] = {}
_COUNTRY_NAMES: dict[str, tuple[str, ...]] = {
    "ua": ("україна",),
    "ru": ("росія", "рф", "російська федерація"),
    "us": ("сша", "сполучені штати", "сполучені штати америки", "америка"),
    "gb": ("велика британія", "британія", "сполучене королівство"),
    "de": ("німеччина", "фрн"),
    "fr": ("франція",),
    "pl": ("польща",),
    "ee": ("естонія",),
    "lv": ("латвія",),
    "lt": ("литва",),
    "md": ("молдова", "республіка молдова"),
    "by": ("білорусь",),
    "cn": ("китай", "кнр"),
    "tr": ("туреччина",),
    "it": ("італія",),
    "es": ("іспанія",),
    "jp": ("японія",),
    "ca": ("канада",),
    "au": ("австралія",),
    "hu": ("угорщина",),
    "sk": ("словаччина",),
    "cz": ("чехія",),
    "ro": ("румунія",),
    "nl": ("нідерланди",),
    "be": ("бельгія",),
    "se": ("швеція",),
    "fi": ("фінляндія",),
    "no": ("норвегія",),
    "dk": ("данія",),
    "il": ("ізраїль",),
    "ir": ("іран",),
    "in": ("індія",),
    "pt": ("португалія",),
    "ge": ("грузія",),
    "kz": ("казахстан",),
    "kp": ("кндр", "північна корея"),
    "kr": ("південна корея",),
    "sa": ("саудівська аравія",),
    "qa": ("катар",),
    "ae": ("оае", "обʼєднані арабські емірати"),
    "eg": ("єгипет",),
    "sy": ("сирія",),
    "ch": ("швейцарія",),
    "at": ("австрія",),
    "bg": ("болгарія",),
    "gr": ("греція",),
    "hr": ("хорватія",),
    "rs": ("сербія",),
    "ie": ("ірландія",),
    "br": ("бразилія",),
    "mx": ("мексика",),
    "az": ("азербайджан",),
    "am": ("вірменія",),
    "ye": ("ємен",),
}

# Ukrainian oblasts (ISO 3166-2:UA): stems of the oblast name and of its main cities, matched as
# prefixes of words of a normalised region/settlement string. Order matters: Kyiv oblast before Kyiv city.
REGIONS: list[tuple[str, str, tuple[str, ...]]] = [
    ("UA-32", "Київська область", ("київськ", "київщин", "бровар", "бориспіл", "біла церкв", "ірпін", "буч")),
    ("UA-30", "Київ", ("київ",)),
    ("UA-05", "Вінницька область", ("вінниц", "вінничч")),
    ("UA-07", "Волинська область", ("волин", "луцьк", "ковел")),
    ("UA-09", "Луганська область", ("луган", "луганщ", "сєвєродонец", "лисичан", "сватов", "старобільс")),
    (
        "UA-12",
        "Дніпропетровська область",
        (
            "дніпропетров",
            "дніпр",
            "кривий ріг",
            "кривого рог",
            "криворіз",
            "нікопол",
            "кам'янськ",
            "павлоград",
        ),
    ),
    (
        "UA-14",
        "Донецька область",
        (
            "донец",
            "донеч",
            "краматорс",
            "слов'янс",
            "покровс",
            "костянтинівк",
            "бахмут",
            "маріупол",
            "часів яр",
        ),
    ),
    ("UA-18", "Житомирська область", ("житомир",)),
    ("UA-21", "Закарпатська область", ("закарпат", "ужгород", "мукачев")),
    ("UA-23", "Запорізька область", ("запоріз", "запоріж", "мелітопол", "енергодар", "гуляйпол", "оріхів")),
    ("UA-26", "Івано-Франківська область", ("івано-франків", "франківщ", "прикарпат", "калуш")),
    ("UA-35", "Кіровоградська область", ("кіровоград", "кропивниц", "олександрі")),
    ("UA-40", "Севастополь", ("севастопол",)),
    ("UA-43", "Автономна Республіка Крим", ("крим", "сімферопол", "керч", "феодосі", "джанкой")),
    ("UA-46", "Львівська область", ("львів", "львівщ", "дрогобич")),
    ("UA-48", "Миколаївська область", ("миколаїв", "миколаївщ", "очаків")),
    ("UA-51", "Одеська область", ("одес", "одещ", "ізмаїл", "чорноморс")),
    ("UA-53", "Полтавська область", ("полтав", "кременчу")),
    ("UA-56", "Рівненська область", ("рівн", "рівненщ")),
    ("UA-59", "Сумська область", ("сумськ", "суми", "сумах", "сумщ", "шостк", "охтирк")),
    ("UA-61", "Тернопільська область", ("тернопіл", "тернопільщ")),
    ("UA-63", "Харківська область", ("харків", "харківщ", "куп'янс", "ізюм", "чугуїв", "великий бурлук")),
    ("UA-65", "Херсонська область", ("херсон", "херсонщ", "нова каховк", "берислав")),
    ("UA-68", "Хмельницька область", ("хмельниц", "хмельниччин", "кам'янець-поділ")),
    ("UA-71", "Черкаська область", ("черкас", "черкащ", "умань")),
    ("UA-77", "Чернівецька область", ("чернівец", "чернівці", "буковин")),
    ("UA-74", "Чернігівська область", ("чернігів", "чернігівщ", "ніжин")),
]

for _code, _names in _ALIAS_GROUPS.items():
    for _name in _names:
        ALIASES[_APOSTROPHES.sub("'", _name)] = _code
for _code, _names in _COUNTRY_NAMES.items():
    for _name in _names:
        COUNTRIES[_name] = _code

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
_ISO2 = re.compile(r"^[A-Za-z]{2}$")


def norm_name(text: str) -> str:
    """Lowercase, no quotes, one kind of apostrophe, single spaces."""
    text = _QUOTES.sub("", text or "")
    text = _APOSTROPHES.sub("'", text).lower()
    return re.sub(r"\s+", " ", text).strip(" .,;:-")


def translit(text: str) -> str:
    """Ukrainian (and Russian) Cyrillic -> lowercase ASCII slug with ``-`` between words."""
    out = []
    for ch in norm_name(text).replace("'", ""):
        out.append(_TRANSLIT.get(ch, ch))
    return re.sub(r"[^a-z0-9]+", "-", "".join(out)).strip("-")


def country_code(name: str) -> str | None:
    n = norm_name(name)
    if _ISO2.match(n):
        return n
    return COUNTRIES.get(n)


def actor_slug(name: str, kind: str = "") -> str:
    """Stable anchor of an actor: alias code, ISO code of a country, surname of a person, else a slug."""
    n = norm_name(name)
    if not n:
        return ""
    if n in ALIASES:
        return ALIASES[n]
    code = country_code(n)
    if code:
        return code
    if kind == "person":
        words = [w for w in re.split(r"[\s-]+", n) if w]
        return translit(words[-1]) if words else ""
    words = translit(n).split("-")
    return "-".join(words[:4])


def region_code(*texts: str) -> tuple[str, str] | None:
    """``(ISO 3166-2 code, canonical name)`` of the first Ukrainian oblast matched by any of ``texts``."""
    for text in texts:
        n = norm_name(text)
        if not n:
            continue
        words = re.split(r"[\s,()]+", n)
        for code, canonical, stems in REGIONS:
            for stem in stems:
                if " " in stem:
                    if stem in n:
                        return code, canonical
                elif any(w.startswith(stem) for w in words):
                    return code, canonical
    return None


def parse_timestamp(value: str) -> datetime | None:
    if not isinstance(value, str) or not _TIMESTAMP.match(value.strip()):
        return None
    text = value.strip().replace(" ", "T").replace("Z", "+00:00")
    if re.search(r"[+-]\d{4}$", text):
        text = text[:-2] + ":" + text[-2:]
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else None


def _last_sunday(year: int, month: int) -> date:
    d = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
    return d - timedelta(days=(d.weekday() + 1) % 7)


def kyiv_date(moment: datetime) -> str:
    """Calendar date in Kyiv (EET/EEST with the EU switch at 01:00 UTC on the last Sundays of March/October)."""
    utc = moment.astimezone(UTC)
    start = datetime.combine(_last_sunday(utc.year, 3), datetime.min.time(), UTC) + timedelta(hours=1)
    end = datetime.combine(_last_sunday(utc.year, 10), datetime.min.time(), UTC) + timedelta(hours=1)
    offset = 3 if start <= utc < end else 2
    return (utc + timedelta(hours=offset)).date().isoformat()


def valid_date(value: str) -> str | None:
    if isinstance(value, str) and _DATE.match(value.strip()):
        try:
            return date.fromisoformat(value.strip()).isoformat()
        except ValueError:
            return None
    return None


def valid_id(value: object) -> str | None:
    return value if isinstance(value, str) and _ID.match(value) else None


def _party_slug(name: str, kind: str, kinds: Mapping[str, str]) -> str:
    return actor_slug(name, kind or kinds.get(norm_name(name), ""))


def event_anchor(event: Mapping[str, Any], kinds: Mapping[str, str] | None = None) -> str:
    """The anchor part of the event key (see the module docstring).

    ``kinds`` maps normalised canonical names of the item's mentions to their type (``person``…), so that a
    person named as ``counterpart`` is reduced to the surname just like an ``actor``."""
    kinds = kinds or {}
    etype = str(event.get("type") or "")
    country = country_code(str(event.get("country") or "")) or ""
    if etype in PLACE_TYPES:
        region = region_code(str(event.get("region") or ""), str(event.get("settlement") or ""))
        if region and country in ("", "ua"):
            return region[0].lower()
        return country or "xx"
    actor = _party_slug(str(event.get("actor") or ""), str(event.get("actor_type") or ""), kinds)
    counterpart = _party_slug(str(event.get("counterpart") or ""), "", kinds)
    if etype == "diplomacy":
        raw_parties = event.get("parties")
        codes = (country_code(str(p)) for p in (raw_parties if isinstance(raw_parties, list) else []))
        parties = sorted({c for c in codes if c})
        if len(parties) >= 2:
            return "+".join(parties)
    if etype in PAIR_TYPES and actor and counterpart and actor != counterpart:
        return "+".join(sorted((actor, counterpart)))
    if actor:
        return actor
    if counterpart:
        return counterpart
    region = region_code(str(event.get("region") or ""), str(event.get("settlement") or ""))
    if region:
        return region[0].lower()
    return country or "xx"


def event_date(event: Mapping[str, Any], published_date: str, max_lag_days: int = 3) -> str:
    """The event date of the LLM, kept only within ``[published - max_lag_days, published]`` (Kyiv dates):
    an event cannot follow its publication, and an old date (anniversaries, background) is not the news."""
    day = valid_date(str(event.get("date") or ""))
    if day is None:
        return published_date
    lag = (date.fromisoformat(published_date) - date.fromisoformat(day)).days
    return day if 0 <= lag <= max_lag_days else published_date


def key_class(etype: str) -> str:
    """The type part of the key: place types and diplomacy as they are, every actor-anchored type ``actor``
    (the LLM confuses statement / decision / sports for one actor, while the actor itself is stable)."""
    return etype if etype in PLACE_TYPES or etype == "diplomacy" else "actor"


def event_key(
    event: Mapping[str, Any],
    published_date: str,
    *,
    kinds: Mapping[str, str] | None = None,
    max_lag_days: int = 3,
) -> str | None:
    """``<date>:<class>:<anchor>``, or ``None`` when the material reports no event."""
    etype = str(event.get("type") or "")
    if etype not in EVENT_TYPES:
        return None
    day = event_date(event, published_date, max_lag_days)
    return f"{day}:{key_class(etype)}:{event_anchor(event, kinds)}"
