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

Findings never contain the matched value (it would leak the secret into responses and logs).
"""

from __future__ import annotations

import bisect
import contextlib
import math
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from .settings import SecretScanLimits

__all__ = ["SecretFinding", "oversized_files", "scan_files"]


@dataclass(frozen=True)
class SecretFinding:
    path: str
    code: str
    message: str
    line: int | None = None

    @property
    def pointer(self) -> str:
        return "/files/" + self.path.replace("~", "~0").replace("/", "~1")


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

_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "private_key",
        "a private key block",
        re.compile(
            r"(?:-----BEGIN (?:[A-Z0-9]{1,20} ){0,4}PRIVATE KEY(?: BLOCK)?-----|PRIVATE KEY(?: BLOCK)?-----)"
        ),
    ),
    ("aws_access_key", "an AWS access key", re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{16}\b")),
    (
        "aws_secret_key",
        "an AWS secret access key",
        re.compile(r"(?i)aws_?secret_?access_?key[\"']?\s*[=:]\s*[\"']?[A-Za-z0-9/+=]{40}"),
    ),
    (
        "github_token",
        "a GitHub token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})"),
    ),
    ("gitlab_token", "a GitLab token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}")),
    ("slack_token", "a Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    (
        "slack_webhook",
        "a Slack webhook URL",
        re.compile(r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"),
    ),
    ("google_api_key", "a Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}")),
    ("sendgrid_key", "a SendGrid API key", re.compile(r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}")),
    ("huggingface_token", "a Hugging Face token", re.compile(r"\bhf_[A-Za-z0-9]{30,}")),
    ("llm_api_key", "an LLM provider API key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("stripe_key", "a Stripe live key", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{20,}")),
    (
        "azure_storage_key",
        "an Azure storage account key",
        re.compile(r"(?i)AccountKey=[A-Za-z0-9+/]{40,}={0,2}"),
    ),
    (
        "azure_sas",
        "an Azure shared access signature",
        re.compile(r"(?i)(?:SharedAccessSignature=|[?&]sig=)[A-Za-z0-9%+/=]{20,}"),
    ),
    ("telegram_bot_token", "a Telegram bot token", re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b")),
    (
        "jwt",
        "a JSON Web Token",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ),
)
_URL_CREDENTIALS = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]{1,20}://([^\s:/?#@\"'<>]+):([^\s/?#@\"'<>]+)@")
_AUTH_VALUE = re.compile(r"(?i)\b(?:bearer|basic|token)\s+([A-Za-z0-9._~+/=-]{16,})")
_NAME = (
    r"[a-z0-9_.-]{0,40}(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|"
    r"private[_-]?key|client[_-]?secret|auth|session(?:[_-]?id)?|cookie)"
)
_ASSIGNMENT = re.compile(rf"(?i)[\"']?\b({_NAME})\b[\"']?\s*(?:=|:|:=)\s*[\"']([^\"'\s]{{6,}})[\"']")
_UNQUOTED_ASSIGNMENT = re.compile(
    rf"(?im)^\s*(?:export\s+)?({_NAME})\s*[:=]\s*([^\s#;\"'(){{}}\[\]<>,]{{6,}})\s*(?:[#;].*)?$"
)
_CONN_PASSWORD = re.compile(r"(?i)(?:^|[;\"'\s])(password|pwd)\s*=\s*([^;\"'\s{}$]{4,})\s*(?=;|\"|'|$)")
_TOKEN = re.compile(r"(?:[\"'`]|=\s*|:\s*)([A-Za-z0-9+/=_-]{16,})")
_PLACEHOLDER = re.compile(
    r"(?i)^(?:\$\{.*\}|\$[A-Z_]+|<.*>|\{\{.*\}\}|\{.*\}|%\(.*\)s|x+|\*+|\.+|changeme|example\S*|placeholder|"
    r"dummy\S*|test\S*|fake\S*|redacted|your[_-]?\S*|none|null|true|false|env:.*|file:.*|vault:.*|secret_refs.*)$"
)
_NON_ASCII = re.compile(r"[^\t\n\r\x20-\x7e]+")
_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
_WORDS = re.compile(r"^[a-z]+(?:[_.-][a-z]+)*$")


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
    if re.fullmatch(r"[0-9a-fA-F-]+", token):  # digests, UUIDs
        return False
    if not (re.search(r"[a-z]", token) and re.search(r"[A-Z]", token) and re.search(r"[0-9]", token)):
        return False
    return _entropy(token) >= limits.entropy_threshold


class _Enough(Exception):
    pass


def _scan_text(path: str, text: str, limits: SecretScanLimits, *, entropy: bool) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    with contextlib.suppress(_Enough):
        _scan_into(findings, path, text, limits, entropy=entropy)
    return findings


def _scan_into(
    findings: list[SecretFinding], path: str, text: str, limits: SecretScanLimits, *, entropy: bool
) -> None:
    newlines = [i for i, ch in enumerate(text) if ch == "\n"]

    def line_of(index: int) -> int:
        return bisect.bisect_left(newlines, index) + 1

    def add(code: str, message: str, index: int) -> None:
        line = line_of(index)
        findings.append(SecretFinding(path, code, f"{message} (line {line})", line))
        if len(findings) >= limits.max_findings_per_file:
            raise _Enough

    for code, what, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            add(code, f"value looks like {what}", m.start())
    for m in _URL_CREDENTIALS.finditer(text):
        if not _PLACEHOLDER.match(m.group(2)):
            add("url_credentials", "URL contains a password", m.start())
    for m in _AUTH_VALUE.finditer(text):
        if _literal_secret(m.group(1)):
            add("authorization_value", "an authorization header value", m.start())
    for m in _ASSIGNMENT.finditer(text):
        if _literal_secret(m.group(2)):
            add("secret_assignment", f"{m.group(1)!r} is assigned a literal value", m.start())
    if _is_config(path):
        for m in _UNQUOTED_ASSIGNMENT.finditer(text):
            if _literal_secret(m.group(2)):
                add("secret_assignment", f"{m.group(1)!r} is assigned a literal value", m.start())
    for m in _CONN_PASSWORD.finditer(text):
        if _literal_secret(m.group(2)):
            add("connection_string_password", "connection string contains a password", m.start())
    if entropy and PurePosixPath(path).suffix.lower() in _ENTROPY_SUFFIXES:
        seen_lines = {f.line for f in findings}
        for m in _TOKEN.finditer(text):
            token = m.group(1)
            if not _high_entropy(token, limits):
                continue
            prefix = text[max(0, m.start(1) - 16) : m.start(1)].lower()
            if "base64," in prefix or re.search(r"sha(256|384|512)-$", prefix):
                continue
            line = line_of(m.start(1))
            if line in seen_lines:
                continue
            seen_lines.add(line)
            findings.append(
                SecretFinding(path, "high_entropy_string", f"high-entropy string (line {line})", line)
            )


def _decodings(data: bytes) -> list[tuple[str, bool]]:
    """``(text, primary)`` variants of a file; ``primary`` gets the entropy check too."""
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return [(data.decode("utf-16", errors="replace"), True)]
    variants = [(data.decode("utf-8", errors="replace"), True)]
    if b"\0" in data:
        # every detector looks for ASCII: keep only printable ASCII runs of the alternative decodings
        for codec in ("latin-1", "utf-16-le", "utf-16-be"):
            text = _NON_ASCII.sub("\n", data.decode(codec, errors="ignore"))
            variants.append((text, False))
    return variants


def oversized_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[str]:
    """Files the scanner would not read completely (the publish must be refused)."""
    return sorted(p for p, data in files.items() if len(data) > limits.max_scan_bytes_per_file)


def scan_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[SecretFinding]:
    """All findings, sorted by path and line. Callers reject :func:`oversized_files` first."""
    findings: set[SecretFinding] = set()
    for path in sorted(files):
        reason = _is_secret_name(path)
        if reason:
            findings.add(SecretFinding(path, "secret_file", reason))
        data = files[path][: limits.max_scan_bytes_per_file]
        for text, primary in _decodings(data):
            findings.update(_scan_text(path, text, limits, entropy=primary))
    unique: dict[tuple[str, str, int | None], SecretFinding] = {}
    for f in findings:
        unique.setdefault((f.path, f.code, f.line), f)
    return sorted(unique.values(), key=lambda f: (f.path, f.line or 0, f.code))
