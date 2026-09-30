"""Secret detection in package files (ADR-0002 §5, ADR-0006 §6): a finding rejects the publish with
422 ``secret_detected``.

Checks for every file of the package (including ``jane-package.json``):

1. **file names** that hold credentials by convention (``.env``, ``*.pem``, ``id_rsa``, ``.netrc``...);
2. **known formats** in any file: private key blocks (also split or escaped), AWS, GitHub, GitLab, Slack,
   Google, SendGrid, Stripe, Hugging Face, OpenAI/Anthropic-style ``sk-`` keys, Azure storage account keys
   and SAS signatures, Telegram bot tokens, JWTs, credentials inside URLs (``scheme://user:password@host``);
3. **authorization values** - a token after ``Bearer``/``Basic``/``token`` (``Authorization: Bearer …``);
4. **assignments** to secret-like names: quoted (``password = "..."``, ``"api_key": "..."``) in any file,
   unquoted (``password: …`` in YAML, ``password = …`` in INI/.env/.properties) in configuration files,
   ``Password=…;`` / ``Pwd=…;`` in connection strings anywhere;
5. **high-entropy tokens** (quoted strings and assigned values) in code/config files only - not in test
   inputs such as HTML pages, where base64 images and hashes are normal.

Decoding: UTF-8 (with replacement); files with a UTF-16 BOM, or with NUL bytes, are also decoded as UTF-16
and as Latin-1 so that NUL-padded or UTF-16 text cannot hide a secret. A file larger than
``secrets.max_scan_bytes_per_file`` is not accepted unscanned: :func:`oversized_files` lists them and the
publish fails with ``limit_exceeded``.

Cost: every pattern is linear in the input (see the note at the patterns); a lower-case keyword pre-filter skips
patterns that cannot match; the whole scan has a time budget ``secrets.scan_time_budget_ms`` (exceeded ->
:class:`ScanBudgetExceeded` -> ``limit_exceeded``).

Findings never contain the matched value (it would leak the secret into responses and logs).
"""

from __future__ import annotations

import contextlib
import math
import re
import time
from collections import Counter
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from .settings import SecretScanLimits

__all__ = ["ScanBudgetExceeded", "SecretFinding", "oversized_files", "scan_files"]


@dataclass(frozen=True)
class SecretFinding:
    path: str
    code: str
    message: str
    line: int | None = None

    @property
    def pointer(self) -> str:
        return "/files/" + self.path.replace("~", "~0").replace("/", "~1")


class ScanBudgetExceeded(Exception):
    """Scanning took longer than ``secrets.scan_time_budget_ms`` (the publish is refused)."""

    def __init__(self, budget_ms: int, path: str) -> None:
        super().__init__(f"secret scan exceeded scan_time_budget_ms={budget_ms} (at {path})")
        self.budget_ms = budget_ms
        self.path = path


_SECRET_FILE_NAMES = frozenset(
    {
        ".env",
        ".netrc",
        "_netrc",
        ".pgpass",
        ".pypirc",
        ".npmrc",
        ".git-credentials",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "credentials",
    }
)
_SECRET_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".ppk", ".kdbx"})
_ENV_TEMPLATE_SUFFIXES = (".example", ".sample", ".template", ".dist")
_ENTROPY_SUFFIXES = frozenset(
    {".py", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".properties", ".txt", ".md", ".sh"}
)
_CONFIG_SUFFIXES = frozenset(
    {".yaml", ".yml", ".ini", ".cfg", ".conf", ".properties", ".toml", ".env", ".txt"}
)

# ------------------------------------------------------------------------------------------------ patterns
# Every pattern is linear in the input size (review 2, ReDoS):
# * no \s quantifiers that could run across lines - horizontal whitespace only, bounded ([ \t]{0,16});
# * a variable-length run followed by something that may fail is possessive (``{n,}+``, ``++``), and where the
#   run's own characters could start another attempt, a lookbehind makes attempts start only at a run boundary;
# * ``^`` (MULTILINE) is followed by ``[ \t]*`` only, never by ``\s*`` (which crosses lines: O(N^2)).
# ``tests/test_units.py::test_scanner_is_linear_on_adversarial_input`` checks this on adversarial inputs.
_WS = r"[ \t]{0,16}"
_NAME = (
    r"[a-z0-9_.-]{0,40}(?:password|passwd|pwd|secret|token|api[_.-]?key|access[_.-]?key|"
    r"private[_.-]?key|client[_.-]?secret|auth|session(?:[_-]?id)?|cookie)"
)
_NAME_KEYWORDS = ("password", "passwd", "pwd", "secret", "token", "key", "auth", "session", "cookie")


@dataclass(frozen=True)
class _Detector:
    code: str
    message: str
    pattern: re.Pattern[str]
    keywords: tuple[str, ...]
    """Lower-case substrings of which at least one must occur for the pattern to be tried (fast pre-filter)."""
    value_group: int | None = None
    """Group whose value must be a literal secret (not a placeholder); ``None`` - any match counts."""
    config_only: bool = False
    name_group: int | None = None
    anchor: str | None = None
    """``None`` - ``finditer`` over the text; ``name`` / ``line`` - the pattern is tried with ``match`` only at the
    start of the name run (``[a-z0-9_.-]``, at most 40 characters back) or at the start of the line around each
    keyword hit (:data:`_NAME_HIT`): same matches as ``finditer`` with the lookbehind, but without trying the
    40-character name prefix at every position of the text."""


def _d(code: str, message: str, pattern: str, keywords: tuple[str, ...], **kw: object) -> _Detector:
    return _Detector(code, message, re.compile(pattern), keywords, **kw)  # type: ignore[arg-type]


_DETECTORS: tuple[_Detector, ...] = (
    _d(
        "private_key",
        "value looks like a private key block",
        r"PRIVATE KEY(?: BLOCK)?-----",
        ("private key",),
    ),
    _d(
        "aws_access_key",
        "value looks like an AWS access key",
        r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{16}\b",
        ("akia", "asia", "agpa", "aida", "aroa"),
    ),
    _d(
        "aws_secret_key",
        "value looks like an AWS secret access key",
        rf"(?i)aws_?secret_?access_?key[\"']?{_WS}[=:]{_WS}[\"']?[A-Za-z0-9/+=]{{40}}",
        ("secret",),
    ),
    _d(
        "github_token",
        "value looks like a GitHub token",
        r"(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})",
        ("ghp_", "gho_", "ghu_", "ghs_", "ghr_", "github_pat_"),
    ),
    _d("gitlab_token", "value looks like a GitLab token", r"\bglpat-[A-Za-z0-9_-]{20,}", ("glpat-",)),
    _d("slack_token", "value looks like a Slack token", r"\bxox[abposr]-[A-Za-z0-9-]{10,}", ("xox",)),
    _d(
        "slack_webhook",
        "value looks like a Slack webhook URL",
        r"hooks\.slack\.com/services/T[A-Z0-9]++/B[A-Z0-9]++/[A-Za-z0-9]+",
        ("hooks.slack.com",),
    ),
    _d("google_api_key", "value looks like a Google API key", r"\bAIza[0-9A-Za-z_-]{35}", ("aiza",)),
    _d(
        "sendgrid_key",
        "value looks like a SendGrid API key",
        r"\bSG\.[A-Za-z0-9_-]{16,}+\.[A-Za-z0-9_-]{16,}",
        ("sg.",),
    ),
    _d("huggingface_token", "value looks like a Hugging Face token", r"\bhf_[A-Za-z0-9]{30,}", ("hf_",)),
    _d(
        "llm_api_key",
        "value looks like an LLM provider API key",
        r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}",
        ("sk-",),
    ),
    _d("stripe_key", "value looks like a Stripe live key", r"\b(?:sk|rk)_live_[0-9A-Za-z]{20,}", ("_live_",)),
    _d(
        "azure_storage_key",
        "value looks like an Azure storage account key",
        r"(?i)AccountKey=[A-Za-z0-9+/]{40,}={0,2}",
        ("accountkey=",),
    ),
    _d(
        "azure_sas",
        "value looks like an Azure shared access signature",
        r"(?i)(?:SharedAccessSignature=|[?&]sig=)[A-Za-z0-9%+/=]{20,}",
        ("sig=", "sharedaccesssignature="),
    ),
    _d(
        "telegram_bot_token",
        "value looks like a Telegram bot token",
        r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b",
        (":aa",),
    ),
    _d(
        "jwt",
        "value looks like a JSON Web Token",
        r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{8,}+\.eyJ[A-Za-z0-9_-]{8,}+\.[A-Za-z0-9_-]{8,}",
        ("eyj",),
    ),
    _d(
        "url_credentials",
        "URL contains a password",
        r"(?<![a-zA-Z0-9+.-])[a-zA-Z][a-zA-Z0-9+.-]{1,20}://([^\s:/?#@\"'<>]++):([^\s/?#@\"'<>]++)@",
        ("://",),
        value_group=2,
    ),
    _d(
        "authorization_value",
        "an authorization header value",
        r"(?i)(?<![a-z0-9])(?:bearer|basic|token)[ \t]{1,8}([A-Za-z0-9._~+/=-]{16,})",
        ("bearer", "basic", "token"),
        value_group=1,
    ),
    _d(
        "secret_assignment",
        "is assigned a literal value",
        rf"(?i)({_NAME})\b[\"']?{_WS}(?::=|=|:){_WS}[\"']([^\"'\s]{{6,}}+)[\"']",
        _NAME_KEYWORDS,
        value_group=2,
        name_group=1,
        anchor="name",
    ),
    _d(
        "secret_assignment",
        "is assigned a literal value",
        rf"(?im)^[ \t]*+(?:export[ \t]+)?({_NAME})[ \t]*[:=][ \t]*([^\s#;\"'(){{}}\[\]<>,]{{6,}}+)[ \t]*"
        r"(?:[#;][^\r\n]*)?\r?$",
        _NAME_KEYWORDS,
        value_group=2,
        name_group=1,
        config_only=True,
        anchor="line",
    ),
    _d(
        "connection_string_password",
        "connection string contains a password",
        r"(?im)(?:^|[;\"'\s])(password|pwd)[ \t]*=[ \t]*([^;\"'\s{}$]{4,}+)[ \t]*(?=[;\"']|\r?$)",
        ("password", "pwd"),
        value_group=2,
    ),
)
_NAME_HIT = re.compile(r"(?i)password|passwd|pwd|secret|token|key|auth|session|cookie")
_NAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-")
_NAME_PREFIX_MAX = 40
_NON_NAME = re.compile(r"[^A-Za-z0-9_.-]")
_TOKEN = re.compile(r"(?:[\"'`]|=[ \t]{0,16}|:[ \t]{0,16})([A-Za-z0-9+/=_-]{16,})")
_PLACEHOLDER = re.compile(
    r"(?i)^(?:\$\{.*\}|\$[A-Z_]+|<.*>|\{\{.*\}\}|\{.*\}|%\(.*\)s|x+|\*+|\.+|changeme|example\S*|placeholder|"
    r"dummy\S*|test\S*|fake\S*|redacted|your[_-]?\S*|none|null|true|false|env:.*|file:.*|vault:.*|secret_refs.*)$"
)
_HEX = re.compile(r"[0-9a-fA-F-]+")
_LOWER = re.compile(r"[a-z]")
_UPPER = re.compile(r"[A-Z]")
_DIGIT = re.compile(r"[0-9]")
_NON_ASCII = re.compile(r"[^\t\n\r\x20-\x7e]+")
_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
_WORDS = re.compile(r"^[a-z]+(?:[_.-][a-z]+)*$")
_SRI = re.compile(r"sha(?:256|384|512)-$")
_CHECK_EVERY = 256
"""Matches between two checks of the time budget inside one detector."""


def _entropy(token: str) -> float:
    counts = Counter(token)
    n = len(token)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def _is_secret_name(path: str) -> str | None:
    name = PurePosixPath(path).name
    lower = name.lower()
    if lower in _SECRET_FILE_NAMES:
        return f"file name {name!r} is used for credentials"
    if lower.startswith(".env.") and not lower.endswith(_ENV_TEMPLATE_SUFFIXES):
        return f"file name {name!r} is used for credentials"
    if PurePosixPath(lower).suffix in _SECRET_SUFFIXES:
        return f"file type {PurePosixPath(name).suffix!r} holds keys or certificates"
    return None


def _is_config(path: str) -> bool:
    name = PurePosixPath(path).name.lower()
    return PurePosixPath(name).suffix in _CONFIG_SUFFIXES or name.startswith(".env") or "." not in name


def _literal_secret(value: str) -> bool:
    """A value assigned to a secret-like name that is not a placeholder, env var name or plain words."""
    if _PLACEHOLDER.match(value) or _ENV_NAME.match(value):
        return False
    return not (_WORDS.match(value) and not any(c.isdigit() for c in value))


def _high_entropy(token: str, limits: SecretScanLimits) -> bool:
    if len(token) < limits.min_entropy_token_length:
        return False
    if _HEX.fullmatch(token):  # digests, UUIDs
        return False
    if not (_LOWER.search(token) and _UPPER.search(token) and _DIGIT.search(token)):
        return False
    return _entropy(token) >= limits.entropy_threshold


class _Lines:
    """Line numbers of offsets; counting continues from the previous offset (linear for increasing offsets)."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1

    def __call__(self, index: int) -> int:
        if index < self.pos:
            self.pos, self.line = 0, 1
        self.line += self.text.count("\n", self.pos, index)
        self.pos = index
        return self.line


class _Enough(Exception):
    pass


def _scan_text(
    path: str,
    text: str,
    limits: SecretScanLimits,
    *,
    entropy: bool,
    detectors: bool,
    check: Callable[[], None],
) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    with contextlib.suppress(_Enough):
        _scan_into(findings, path, text, limits, entropy=entropy, detectors=detectors, check=check)
    return findings


def _scan_into(
    findings: list[SecretFinding],
    path: str,
    text: str,
    limits: SecretScanLimits,
    *,
    entropy: bool,
    detectors: bool,
    check: Callable[[], None],
) -> None:
    line_of = _Lines(text)
    lower = text.lower()
    config = _is_config(path)
    has_assignment = "=" in text or ":" in text

    def add(code: str, message: str, index: int) -> None:
        line = line_of(index)
        findings.append(SecretFinding(path, code, f"{message} (line {line})", line))
        if len(findings) >= limits.max_findings_per_file:
            raise _Enough

    for det in _DETECTORS if detectors else ():
        check()
        if det.config_only and not config:
            continue
        if det.anchor and not has_assignment:
            continue
        if det.keywords and not any(k in lower for k in det.keywords):
            continue
        for i, m in enumerate(_matches(det, text)):
            if i % _CHECK_EVERY == _CHECK_EVERY - 1:
                check()
            if det.value_group is not None and not _literal_secret(m.group(det.value_group)):
                continue
            message = det.message
            if det.name_group is not None:
                message = f"{m.group(det.name_group)!r} {message}"
            add(det.code, message, m.start())
    if entropy and PurePosixPath(path).suffix.lower() in _ENTROPY_SUFFIXES:
        check()
        seen_lines = {f.line for f in findings}
        for i, m in enumerate(_TOKEN.finditer(text)):
            if i % _CHECK_EVERY == _CHECK_EVERY - 1:
                check()
            token = m.group(1)
            if not _high_entropy(token, limits):
                continue
            prefix = lower[max(0, m.start(1) - 16) : m.start(1)]
            if "base64," in prefix or _SRI.search(prefix):
                continue
            line = line_of(m.start(1))
            if line in seen_lines:
                continue
            seen_lines.add(line)
            add("high_entropy_string", "high-entropy string", m.start(1))


def _matches(det: _Detector, text: str) -> Iterator[re.Match[str]]:
    if det.anchor is None or det.anchor == "line":
        # The multiline anchor consumes horizontal whitespace only. Each line has one start position, and the
        # whitespace quantifier is possessive, so finditer cannot rescan a line from successive keywords.
        yield from det.pattern.finditer(text)
        return
    tried: set[int] = set()
    end = 0
    line_start, scanned = 0, 0  # start of the line of the last hit; text[:scanned] searched for newlines
    run_start: int | None = None  # start of the name run of the last hit (-1: longer than the prefix allows)
    for hit in _NAME_HIT.finditer(text):
        h = hit.start()
        if h < end:
            continue  # inside the previous match
        if det.anchor == "line":
            # hits come in increasing order: look for a newline only between the previous hit and this one
            # (``rfind`` from 0 would rescan a long line for every hit - O(N^2), review 2)
            nl = text.rfind("\n", scanned, h)
            if nl >= 0:
                line_start = nl + 1
            scanned = h
            start = line_start
        else:
            if run_start is None or _NON_NAME.search(text, scanned, h) is not None:
                # a new run of name characters: find its start once (at most _NAME_PREFIX_MAX steps back)
                start = h
                while start > 0 and h - start <= _NAME_PREFIX_MAX and text[start - 1] in _NAME_CHARS:
                    start -= 1
                run_start = start if start == 0 or text[start - 1] not in _NAME_CHARS else -1
            scanned = h
            if run_start < 0 or h - run_start > _NAME_PREFIX_MAX:
                continue  # the name run is longer than the prefix allows (as the lookbehind would reject it)
            start = run_start
        if start in tried:
            continue
        tried.add(start)
        m = det.pattern.match(text, start)
        if m is not None:
            end = m.end()
            yield m


def _decodings(data: bytes) -> list[tuple[str, bool, bool]]:
    """``(text, entropy, detectors)`` variants of a file.

    Text without NUL: the UTF-8 decoding gets every check. With a UTF-16 BOM: the UTF-16 decoding. With NUL bytes
    (binary, NUL-padded or UTF-16 without BOM): the detectors - which all look for ASCII - run on the printable
    ASCII runs of the Latin-1 (every ASCII byte of the file) and UTF-16 LE/BE decodings; the UTF-8 decoding, mostly
    replacement characters, keeps only the entropy check.
    """
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return [(data.decode("utf-16", errors="replace"), True, True)]
    primary = data.decode("utf-8", errors="replace")
    if b"\0" not in data:
        return [(primary, True, True)]
    variants = [(primary, True, False)]
    for codec in ("latin-1", "utf-16-le", "utf-16-be"):
        variants.append((_NON_ASCII.sub("\n", data.decode(codec, errors="ignore")), False, True))
    return variants


def oversized_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[str]:
    """Files the scanner would not read completely (the publish must be refused)."""
    return sorted(p for p, data in files.items() if len(data) > limits.max_scan_bytes_per_file)


def scan_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[SecretFinding]:
    """All findings, sorted by path and line. Callers reject :func:`oversized_files` first.

    Raises :class:`ScanBudgetExceeded` when the whole scan takes longer than ``secrets.scan_time_budget_ms``
    (checked between detectors and every few hundred matches - a safeguard on top of the linear patterns).
    """
    deadline = time.monotonic() + limits.scan_time_budget_ms / 1000
    findings: set[SecretFinding] = set()
    for path in sorted(files):

        def check(path: str = path) -> None:
            if time.monotonic() > deadline:
                raise ScanBudgetExceeded(limits.scan_time_budget_ms, path)

        reason = _is_secret_name(path)
        if reason:
            findings.add(SecretFinding(path, "secret_file", reason))
        data = files[path][: limits.max_scan_bytes_per_file]
        for text, entropy, detectors in _decodings(data):
            check()
            findings.update(_scan_text(path, text, limits, entropy=entropy, detectors=detectors, check=check))
    unique: dict[tuple[str, str, int | None], SecretFinding] = {}
    for f in findings:
        unique.setdefault((f.path, f.code, f.line), f)
    return sorted(unique.values(), key=lambda f: (f.path, f.line or 0, f.code))
