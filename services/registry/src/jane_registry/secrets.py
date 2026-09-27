"""Secret detection in package files (ADR-0002 §5, ADR-0006 §6): a finding rejects the publish with
422 ``secret_detected``.

Checks, in this order, for every file of the package (including ``jane-package.json``):

1. **file names** that hold credentials by convention (``.env``, ``*.pem``, ``id_rsa``, ``.netrc``...);
2. **known formats** in any text file: private key blocks, cloud/provider keys and tokens (AWS, GitHub,
   GitLab, Slack, Google, OpenAI/Anthropic-style ``sk-``, Stripe live keys, Telegram bot tokens), JWTs,
   credentials inside URLs (``scheme://user:password@host``);
3. **assignments** to secret-like names (``password = "..."``, ``"api_key": "..."``) of a non-placeholder
   value;
4. **high-entropy tokens** (quoted strings and assigned values) in code/config files only - not in test
   inputs such as HTML pages, where base64 images and hashes are normal.

Findings never contain the matched value (it would leak the secret into responses and logs).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from .settings import SecretScanLimits

__all__ = ["SecretFinding", "scan_files"]


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

_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "private_key",
        "a private key block",
        re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----"),
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
    ("google_api_key", "a Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}")),
    ("llm_api_key", "an LLM provider API key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("stripe_key", "a Stripe live key", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{20,}")),
    ("telegram_bot_token", "a Telegram bot token", re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b")),
    (
        "jwt",
        "a JSON Web Token",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ),
)
_URL_CREDENTIALS = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]{1,20}://([^\s:/?#@\"'<>]+):([^\s/?#@\"'<>]+)@")
_ASSIGNMENT = re.compile(
    r"(?i)[\"']?\b([a-z0-9_.-]*(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|"
    r"private[_-]?key|client[_-]?secret|auth))\b[\"']?\s*(?:=|:|:=)\s*[\"']([^\"'\s]{8,})[\"']"
)
_TOKEN = re.compile(r"(?:[\"'`]|=\s*|:\s*)([A-Za-z0-9+/=_-]{16,})")
_PLACEHOLDER = re.compile(
    r"(?i)^(?:\$\{.*\}|\$[A-Z_]+|<.*>|\{\{.*\}\}|%\(.*\)s|x+|\*+|\.+|changeme|example\S*|placeholder|"
    r"dummy\S*|test\S*|fake\S*|redacted|your[_-]?\S*|none|null|env:.*|file:.*|vault:.*)$"
)


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


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _high_entropy(token: str, limits: SecretScanLimits) -> bool:
    if len(token) < limits.min_entropy_token_length:
        return False
    if re.fullmatch(r"[0-9a-fA-F-]+", token):  # digests, UUIDs
        return False
    if not (re.search(r"[a-z]", token) and re.search(r"[A-Z]", token) and re.search(r"[0-9]", token)):
        return False
    return _entropy(token) >= limits.entropy_threshold


def _scan_text(path: str, text: str, limits: SecretScanLimits) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for code, what, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            line = _line_of(text, m.start())
            findings.append(SecretFinding(path, code, f"value looks like {what} (line {line})", line))
    for m in _URL_CREDENTIALS.finditer(text):
        password = m.group(2)
        if not _PLACEHOLDER.match(password):
            line = _line_of(text, m.start())
            findings.append(
                SecretFinding(path, "url_credentials", f"URL contains a password (line {line})", line)
            )
    for m in _ASSIGNMENT.finditer(text):
        value = m.group(2)
        if _PLACEHOLDER.match(value) or _entropy(value) < 3.0:
            continue
        line = _line_of(text, m.start())
        findings.append(
            SecretFinding(
                path, "secret_assignment", f"{m.group(1)!r} is assigned a literal value (line {line})", line
            )
        )
    if PurePosixPath(path).suffix.lower() in _ENTROPY_SUFFIXES:
        seen_lines = {f.line for f in findings}
        for m in _TOKEN.finditer(text):
            token = m.group(1)
            if not _high_entropy(token, limits):
                continue
            prefix = text[max(0, m.start(1) - 16) : m.start(1)].lower()
            if "base64," in prefix or re.search(r"sha(256|384|512)-$", prefix):
                continue
            line = _line_of(text, m.start(1))
            if line in seen_lines:
                continue
            seen_lines.add(line)
            findings.append(
                SecretFinding(path, "high_entropy_string", f"high-entropy string (line {line})", line)
            )
    return findings


def scan_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[SecretFinding]:
    """All findings, sorted by path and line."""
    findings: list[SecretFinding] = []
    for path in sorted(files):
        reason = _is_secret_name(path)
        if reason:
            findings.append(SecretFinding(path, "secret_file", reason))
        data = files[path][: limits.max_scan_bytes_per_file]
        if b"\0" in data[:8192]:
            continue  # binary file: names only
        text = data.decode("utf-8", errors="replace")
        findings.extend(_scan_text(path, text, limits))
    return sorted(findings, key=lambda f: (f.path, f.line or 0, f.code))
