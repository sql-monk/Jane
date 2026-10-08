"""Authentication and scopes of Jane services (ADR-0005), one implementation for every service.

Modes (``auth_mode``, env ``<PREFIX>AUTH_MODE``):

* ``none`` - local tests only. Every caller is ``anonymous`` with every scope; a warning is logged at start,
  and a ``host`` other than loopback is refused unless ``auth_none_allow_remote=true``;
* ``api_key`` - static keys from configuration (``api_keys`` as JSON, ``api_keys_file`` as a JSON/YAML list):
  ``{"name", "scopes": [...], "sha256": "<hex of the key>"}`` or, instead of ``sha256``, ``"secret_ref":
  "env:VAR" | "file:/run/secrets/x"`` (ADR-0006) which is resolved once at start and kept only as its hash.
  Further fields of an entry (e.g. ``actor`` of the registry) become :attr:`Principal.attributes`;
* ``jwt`` - RS*/PS*/ES* tokens verified with the keys published at ``jwt_jwks_url`` (cached for
  ``jwt_jwks_cache_ttl_seconds``, fetched within ``jwt_jwks_timeout_ms``). The IdP is asked at most once per
  ``jwt_jwks_refresh_cooldown_seconds`` - for an expired cache, an unknown ``kid`` and after a failed fetch
  alike; meanwhile known keys keep working and, without any keys, requests get 503 at once. ``iss``/``aud``/
  ``exp`` are required and ``nbf`` checked. Scopes come from the ``scope`` claim (space separated or a list).
  ``alg=none`` and HMAC algorithms are never accepted (a public key must not become an HMAC secret).

Incomplete configuration is an error at start (fail closed): ``api_key`` without keys, ``jwt`` without
JWKS URL / issuer / audience, an unresolvable ``secret_ref``, a scope table that misses a route.

Paths: ``/v1/health`` needs no token, and ``/metrics`` neither unless ``metrics_public=false``. Every other
path needs a valid token (401 ``unauthenticated``). Scopes (403 ``forbidden``) come either from the
service's table ``"METHOD /path/template" -> scope`` (``create_app(..., auth_scopes=...)``; a tuple means
"any of", an empty tuple "any valid token"; ``GET /v1/info`` and the OpenAPI pages are "any valid token"),
or, when the service passes no table, from its handlers via :func:`principal_of` / :func:`require`.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import ipaddress
import json
import logging
import math
import os
import re
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol
from urllib.parse import urlsplit

import httpx
import jwt
import yaml
from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from starlette.types import ASGIApp, Receive, Scope, Send

from jane_kit.errors import Forbidden, JaneError, ServiceUnavailable, Unauthenticated, problem_response

__all__ = [
    "AUTHENTICATED",
    "BUILTIN_SCOPES",
    "JWT_ALGORITHMS",
    "ApiKeyConfig",
    "AuthConfigError",
    "AuthSettings",
    "Authenticator",
    "JwksCache",
    "Principal",
    "ScopeTable",
    "SecretRefError",
    "authorize",
    "bearer_header",
    "check_scopes",
    "install_auth",
    "principal_of",
    "require",
    "resolve_secret_ref",
    "sha256_hex",
    "unmapped_routes",
]

log = logging.getLogger("jane.auth")

AuthMode = Literal["none", "api_key", "jwt"]
WILDCARD = "*"
"""Scope of the anonymous principal of ``auth_mode=none``: has every scope."""
AUTHENTICATED: tuple[str, ...] = ()
"""Table value for operations that need a valid token but no particular scope."""
JWT_ALGORITHMS = frozenset({"RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512"})
"""Asymmetric algorithms ``jwt_algorithms`` may list; ``none`` and ``HS*`` are rejected."""
SCOPE_RE = re.compile(r"^[a-z][a-z0-9-]*:[a-z][a-z0-9_-]*$")
ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
OPEN_PATHS = frozenset({"/v1/health"})
BUILTIN_SCOPES: dict[str, tuple[str, ...]] = {
    "GET /v1/info": AUTHENTICATED,  # common.yaml Info: bearerAuth, 401 - any valid token
    "GET /metrics": AUTHENTICATED,  # only when metrics_public=false
    "GET /openapi.json": AUTHENTICATED,
    "GET /docs": AUTHENTICATED,
    "GET /docs/oauth2-redirect": AUTHENTICATED,
    "GET /redoc": AUTHENTICATED,
}
"""Routes every service has (jane-kit, FastAPI); a service's table may override them."""

ScopeTable = Mapping[str, str | Sequence[str]]
"""``"METHOD /path/template"`` (as registered in FastAPI) -> scope, or any-of scopes (empty = any valid token)."""


class AuthConfigError(ValueError):
    """Authentication is configured incompletely or wrongly; the service must not start."""


class SecretRefError(AuthConfigError):
    """A secret reference cannot be resolved. The message never contains a secret value."""


# ----------------------------------------------------------------------------- settings
class AuthSettings(BaseModel):
    """Authentication knobs; part of every service's settings (``JaneSettings``), env ``<PREFIX><NAME>``."""

    auth_mode: AuthMode = "none"
    """``none`` (local tests only), ``api_key`` (dev stack default) or ``jwt`` (production), ADR-0005."""
    auth_none_allow_remote: bool = False
    """``auth_mode=none`` with a non-loopback ``host`` refuses to start unless this is true (isolated test
    networks only)."""
    api_keys: list[dict[str, Any]] = Field(default_factory=list)
    """``api_key``: ``[{"name", "scopes": [...], "sha256": "<hex>" | "secret_ref": "env:VAR"|"file:/path"}]``."""
    api_keys_file: Path | None = None
    """``api_key``: JSON or YAML file with the same list (added to ``api_keys``)."""
    jwt_jwks_url: str | None = None
    """``jwt``: JWKS of the identity provider (HTTPS; plain HTTP only for a loopback host)."""
    jwt_issuer: str | None = None
    """``jwt``: required ``iss``."""
    jwt_audience: str | None = None
    """``jwt``: required ``aud`` (this service's audience at the identity provider)."""
    jwt_algorithms: list[str] = Field(default_factory=lambda: ["RS256", "ES256"])
    """``jwt``: accepted algorithms, a subset of :data:`JWT_ALGORITHMS`."""
    jwt_scope_claim: str = "scope"
    """``jwt``: claim with the scopes (space separated string or list of strings)."""
    jwt_leeway_seconds: int = Field(default=30, ge=0, le=600)
    """``jwt``: allowed clock skew for ``exp``/``nbf``/``iat``."""
    jwt_jwks_cache_ttl_seconds: int = Field(default=300, ge=1)
    """``jwt``: how long fetched keys are used before the JWKS is fetched again."""
    jwt_jwks_timeout_ms: int = Field(default=5_000, ge=1)
    """``jwt``: time box of one JWKS request."""
    jwt_jwks_refresh_cooldown_seconds: int = Field(default=10, ge=0)
    """``jwt``: minimum time between two fetches caused by an unknown ``kid`` (protects the IdP)."""
    jwt_jwks_max_bytes: int = Field(default=1_048_576, ge=1_024)
    """``jwt``: largest accepted JWKS document."""
    auth_max_token_bytes: int = Field(default=16_384, ge=256)
    """Longest accepted bearer token; longer ones are rejected with 401 before any parsing."""
    metrics_public: bool = True
    """``/metrics`` without a token (Prometheus scraping inside the deployment); false - any valid token."""


class ApiKeyConfig(BaseModel):
    """One configured API key. Extra fields (e.g. ``actor``) are kept as :attr:`Principal.attributes`."""

    model_config = ConfigDict(extra="allow", frozen=True)

    name: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._@:-]*$")
    scopes: list[str]
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-fA-F]{64}$")
    secret_ref: str | None = None

    @field_validator("scopes")
    @classmethod
    def _scopes(cls, value: list[str]) -> list[str]:
        bad = [s for s in value if not SCOPE_RE.match(s)]
        if bad:
            raise ValueError(f"scopes must look like 'service:action', got {bad}")
        return value

    @model_validator(mode="after")
    def _one_source(self) -> ApiKeyConfig:
        if (self.sha256 is None) == (self.secret_ref is None):
            raise ValueError("give exactly one of sha256 (hex digest of the key) or secret_ref (env:/file:)")
        return self

    @property
    def attributes(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


# ----------------------------------------------------------------------------- helpers
def sha256_hex(value: str) -> str:
    """Hex SHA-256 of a key, the form ``api_keys[].sha256`` stores."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def bearer_header(token: str | None) -> dict[str, str]:
    """``{"Authorization": "Bearer <token>"}`` or ``{}`` - for clients of other Jane services."""
    return {"Authorization": f"Bearer {token}"} if token else {}


def resolve_secret_ref(ref: str, *, environ: Mapping[str, str] | None = None) -> str:
    """Value of ``env:VAR`` or ``file:/path`` (surrounding whitespace stripped). ``vault:`` is not supported
    by this build (ADR-0006: optional provider). Raises :class:`SecretRefError` without revealing values."""
    kind, sep, target = ref.partition(":")
    if not sep or not target:
        raise SecretRefError("secret reference must be env:VAR or file:/path")
    if kind == "env":
        if not ENV_NAME_RE.match(target):
            raise SecretRefError(f"env reference has an invalid variable name: {target!r}")
        value = (os.environ if environ is None else environ).get(target, "").strip()
        if not value:
            raise SecretRefError(f"environment variable {target} is not set or empty")
        return value
    if kind == "file":
        try:
            value = Path(target).read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError) as exc:
            raise SecretRefError(f"secret file {target} cannot be read: {type(exc).__name__}") from None
        if not value:
            raise SecretRefError(f"secret file {target} is empty")
        return value
    if kind == "vault":
        raise SecretRefError("vault: references are not supported by this build; use env: or file:")
    raise SecretRefError(f"unknown secret reference kind {kind!r}; use env: or file:")


def _is_loopback(host: str) -> bool:
    host = host.strip("[]")
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


# ----------------------------------------------------------------------------- principal
@dataclass(frozen=True)
class Principal:
    """The authenticated caller: key name / JWT subject, its scopes and extra attributes."""

    name: str
    scopes: frozenset[str]
    method: AuthMode
    attributes: Mapping[str, Any] = field(default_factory=dict)
    """``api_key``: extra fields of the key entry; ``jwt``: the token's claims."""

    def has(self, scope: str) -> bool:
        return WILDCARD in self.scopes or scope in self.scopes

    def require(self, *any_of: str) -> None:
        """403 ``forbidden`` unless the principal has one of ``any_of`` (no arguments - nothing required)."""
        if any_of and not any(self.has(s) for s in any_of):
            raise Forbidden(
                f"scope {' or '.join(any_of)} required", details={"required_scopes": list(any_of)}
            )


ANONYMOUS = Principal("anonymous", frozenset({WILDCARD}), "none")


def _challenge(error: str | None = None) -> dict[str, str]:
    return {"WWW-Authenticate": f'Bearer error="{error}"' if error else "Bearer"}


def _unauthenticated(detail: str, error: str | None = "invalid_token") -> Unauthenticated:
    return Unauthenticated(detail, headers=_challenge(error))


# ----------------------------------------------------------------------------- api keys
@dataclass(frozen=True)
class _Key:
    digest: bytes
    principal: Principal


class ApiKeyVerifier:
    """Keys as SHA-256 digests; a presented token is hashed and compared in constant time."""

    def __init__(self, keys: Sequence[ApiKeyConfig], *, environ: Mapping[str, str] | None = None) -> None:
        if not keys:
            raise AuthConfigError("auth_mode=api_key needs at least one key (api_keys or api_keys_file)")
        self._keys: list[_Key] = []
        names: set[str] = set()
        for key in keys:
            if key.name in names:
                raise AuthConfigError(f"api key name {key.name!r} is configured twice")
            names.add(key.name)
            if key.sha256 is not None:
                digest = bytes.fromhex(key.sha256)
            else:
                try:
                    digest = hashlib.sha256(
                        resolve_secret_ref(str(key.secret_ref), environ=environ).encode("utf-8")
                    ).digest()
                except SecretRefError as exc:
                    raise SecretRefError(f"api key {key.name!r}: {exc}") from None
            if any(hmac.compare_digest(digest, k.digest) for k in self._keys):
                raise AuthConfigError(f"api key {key.name!r} has the same value as another key")
            principal = Principal(key.name, frozenset(key.scopes), "api_key", key.attributes)
            self._keys.append(_Key(digest, principal))

    @property
    def names(self) -> list[str]:
        return [k.principal.name for k in self._keys]

    def verify(self, token: str) -> Principal | None:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        found: Principal | None = None
        for key in self._keys:  # every key is compared: no early exit
            if hmac.compare_digest(digest, key.digest):
                found = key.principal
        return found


def load_api_keys(settings: AuthSettings) -> list[ApiKeyConfig]:
    """Entries of ``api_keys`` and ``api_keys_file`` (validated; errors name the entry, never a value)."""
    raw: list[Any] = list(settings.api_keys)
    if settings.api_keys_file is not None:
        path = settings.api_keys_file
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AuthConfigError(f"api_keys_file {path} cannot be read: {type(exc).__name__}") from None
        doc = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
        if not isinstance(doc, list):
            raise AuthConfigError(f"api_keys_file {path} must contain a list of keys")
        raw += doc
    out: list[ApiKeyConfig] = []
    for i, entry in enumerate(raw):
        try:
            out.append(ApiKeyConfig.model_validate(entry))
        except ValidationError as exc:
            name = entry.get("name") if isinstance(entry, dict) else None
            problems = "; ".join(f"{'.'.join(map(str, e['loc'])) or '-'}: {e['msg']}" for e in exc.errors())
            raise AuthConfigError(f"api key #{i} ({name!r}) is invalid: {problems}") from None
    return out


# ----------------------------------------------------------------------------- jwt
class _Clock(Protocol):
    def __call__(self) -> float: ...


class JwksCache:
    """Signing keys of the identity provider, fetched on demand and cached for ``ttl_s``.

    The IdP gets at most one request per ``cooldown_s``, whatever triggers it (empty or expired cache, a token
    with an unknown ``kid``) and whether the previous attempt succeeded or failed; concurrent requests wait for
    the one fetch in progress instead of starting their own. Between attempts:

    * a token whose ``kid`` is in the cache is checked with that key, also while the cache is being refreshed
      or after a failed refresh (stale keys stay in use);
    * an unknown ``kid`` is answered from the cache (-> 401) without contacting the IdP;
    * without any keys every request fails at once with 503 ``service_unavailable`` (the IdP is unavailable,
      the token is not necessarily wrong) - one warning per failed attempt, not per request.
    """

    def __init__(
        self,
        url: str,
        *,
        ttl_s: float,
        timeout_s: float,
        cooldown_s: float,
        max_bytes: int,
        transport: httpx.AsyncBaseTransport | None = None,
        clock: _Clock = time.monotonic,
    ) -> None:
        self.url = url
        self.ttl_s = ttl_s
        self.timeout_s = timeout_s
        self.cooldown_s = cooldown_s
        self.max_bytes = max_bytes
        self._transport = transport
        self._clock = clock
        self._keys: list[dict[str, Any]] = []
        self._fetched_at: float | None = None
        """Time of the last successful fetch (age of the cached keys)."""
        self._attempted_at: float | None = None
        """Time of the last fetch attempt, successful or not (the cooldown counts from it)."""
        self._attempts = 0
        self._lock = asyncio.Lock()
        self.fetches = 0
        """Number of JWKS requests made (diagnostics and tests)."""

    async def _download(self) -> list[dict[str, Any]]:
        self.fetches += 1
        async with (
            httpx.AsyncClient(
                timeout=self.timeout_s, transport=self._transport, follow_redirects=False
            ) as client,
            client.stream("GET", self.url, headers={"Accept": "application/json"}) as response,
        ):
            if response.status_code != 200:
                raise ValueError(f"JWKS answered HTTP {response.status_code}")
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body += chunk
                if len(body) > self.max_bytes:
                    raise ValueError(f"JWKS is larger than {self.max_bytes} bytes")
        doc = json.loads(bytes(body))
        keys = doc.get("keys") if isinstance(doc, dict) else None
        if not isinstance(keys, list):
            raise ValueError("JWKS has no 'keys' list")
        usable = [
            k
            for k in keys
            if isinstance(k, dict) and k.get("kty") in {"RSA", "EC"} and k.get("use") in (None, "sig")
        ]
        if not usable:
            raise ValueError("JWKS has no RSA/EC signing keys")
        return usable

    def _may_attempt(self, now: float) -> bool:
        return self._attempted_at is None or now - self._attempted_at >= self.cooldown_s

    def _expired(self, now: float) -> bool:
        return self._fetched_at is None or now - self._fetched_at >= self.ttl_s

    def _unavailable(self) -> ServiceUnavailable:
        return ServiceUnavailable(
            "signing keys of the identity provider are unavailable",
            retry_after_seconds=max(1, math.ceil(self.cooldown_s)),
        )

    async def _refresh(self) -> None:
        """One fetch for all waiting requests: a request that waited while another one fetched does not fetch
        again, and nobody fetches before the cooldown since the last attempt has passed."""
        seen = self._attempts
        async with self._lock:
            now = self._clock()
            if self._attempts != seen or not self._may_attempt(now):
                return
            self._attempts += 1
            self._attempted_at = now
            try:
                keys = await self._download()
            except (httpx.HTTPError, httpx.InvalidURL, ValueError, TypeError) as exc:
                log.warning(
                    "JWKS fetch failed; cached keys stay in use, next attempt after the cooldown",
                    extra={
                        "jwks_url": self.url,
                        "cooldown_s": self.cooldown_s,
                        "cached_keys": len(self._keys),
                        "error": f"{type(exc).__name__}: {exc}"[:500],
                    },
                )
                return
            self._keys = keys
            self._fetched_at = now

    def _find(self, kid: str | None) -> dict[str, Any] | None:
        if kid is None:
            return self._keys[0] if len(self._keys) == 1 else None
        return next((k for k in self._keys if k.get("kid") == kid), None)

    async def key(self, kid: str | None) -> dict[str, Any] | None:
        """The JWK for ``kid`` (``None`` - unknown key, 401); raises 503 when no keys are available."""
        now = self._clock()
        found = self._find(kid)
        if found is not None and (
            not self._expired(now) or self._lock.locked() or not self._may_attempt(now)
        ):
            return found  # fresh; or a refresh is running / was just tried - the cached key stays valid
        if not self._may_attempt(now):
            if not self._keys:
                raise self._unavailable()
            return None  # unknown kid within the cooldown: no request to the IdP
        await self._refresh()
        if not self._keys:
            raise self._unavailable()
        return self._find(kid)


class JwtVerifier:
    def __init__(
        self,
        jwks: JwksCache,
        *,
        issuer: str,
        audience: str,
        algorithms: Sequence[str],
        scope_claim: str = "scope",
        leeway_s: float = 30,
    ) -> None:
        self.jwks = jwks
        self.issuer = issuer
        self.audience = audience
        self.algorithms = tuple(algorithms)
        self.scope_claim = scope_claim
        self.leeway_s = leeway_s

    async def verify(self, token: str) -> Principal:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError:
            raise _unauthenticated("token is not a valid JWT") from None
        alg = header.get("alg")
        if alg not in self.algorithms:
            raise _unauthenticated(f"token algorithm {alg!r} is not accepted")
        kid = header.get("kid")
        if kid is not None and not isinstance(kid, str):
            raise _unauthenticated("token kid is not a string")
        jwk = await self.jwks.key(kid)
        if jwk is None:
            raise _unauthenticated("token is signed with an unknown key")
        if jwk.get("alg") not in (None, alg):
            raise _unauthenticated("token algorithm does not match its key")
        try:
            key = jwt.PyJWK(jwk, algorithm=alg)
            claims: dict[str, Any] = jwt.decode(
                token,
                key=key,
                algorithms=[alg],
                audience=self.audience,
                issuer=self.issuer,
                leeway=self.leeway_s,
                options={"require": ["exp", "iss", "aud"], "enforce_minimum_key_length": True},
            )
        except jwt.ExpiredSignatureError:
            raise _unauthenticated("token has expired") from None
        except jwt.ImmatureSignatureError:
            raise _unauthenticated("token is not valid yet") from None
        except jwt.InvalidAudienceError:
            raise _unauthenticated("token audience is not accepted") from None
        except jwt.InvalidIssuerError:
            raise _unauthenticated("token issuer is not accepted") from None
        except jwt.MissingRequiredClaimError as exc:
            raise _unauthenticated(f"token has no {exc.claim} claim") from None
        except (jwt.PyJWTError, jwt.PyJWKError, ValueError, TypeError):
            raise _unauthenticated("token signature is not valid") from None
        raw = claims.get(self.scope_claim, "")
        if isinstance(raw, str):
            scopes = frozenset(raw.split())
        elif isinstance(raw, list) and all(isinstance(s, str) for s in raw):
            scopes = frozenset(raw)
        else:
            raise _unauthenticated(f"claim {self.scope_claim} must be a string or a list of strings")
        name = next((str(claims[c]) for c in ("sub", "client_id", "azp") if claims.get(c)), "jwt")
        return Principal(name, scopes - {WILDCARD}, "jwt", claims)


# ----------------------------------------------------------------------------- authenticator
class Authenticator:
    """Checks ``Authorization: Bearer <token>`` according to the mode; build it with :meth:`from_settings`."""

    def __init__(
        self,
        mode: AuthMode,
        *,
        api_keys: ApiKeyVerifier | None = None,
        jwt_verifier: JwtVerifier | None = None,
        max_token_bytes: int = 16_384,
    ) -> None:
        if mode == "api_key" and api_keys is None:
            raise AuthConfigError("auth_mode=api_key needs API keys")
        if mode == "jwt" and jwt_verifier is None:
            raise AuthConfigError("auth_mode=jwt needs a JWT verifier")
        self.mode = mode
        self.api_keys = api_keys
        self.jwt = jwt_verifier
        self.max_token_bytes = max_token_bytes

    @classmethod
    def from_settings(
        cls,
        settings: AuthSettings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        environ: Mapping[str, str] | None = None,
        clock: _Clock = time.monotonic,
    ) -> Authenticator:
        """Fail-closed construction: raises :class:`AuthConfigError` for an incomplete configuration."""
        mode = settings.auth_mode
        if mode == "none":
            return cls("none", max_token_bytes=settings.auth_max_token_bytes)
        if mode == "api_key":
            return cls(
                "api_key",
                api_keys=ApiKeyVerifier(load_api_keys(settings), environ=environ),
                max_token_bytes=settings.auth_max_token_bytes,
            )
        missing = [
            f"jwt_{n}"
            for n, v in (
                ("jwks_url", settings.jwt_jwks_url),
                ("issuer", settings.jwt_issuer),
                ("audience", settings.jwt_audience),
            )
            if not v
        ]
        if missing:
            raise AuthConfigError(f"auth_mode=jwt needs {', '.join(missing)}")
        algorithms = list(settings.jwt_algorithms)
        bad = [a for a in algorithms if a not in JWT_ALGORITHMS]
        if bad or not algorithms:
            raise AuthConfigError(
                f"jwt_algorithms may only list {sorted(JWT_ALGORITHMS)} (never none/HS*), got {algorithms}"
            )
        url = str(settings.jwt_jwks_url)
        parts = urlsplit(url)
        if parts.scheme != "https" and not (parts.scheme == "http" and _is_loopback(parts.hostname or "")):
            raise AuthConfigError("jwt_jwks_url must be https:// (http:// only for a loopback host)")
        jwks = JwksCache(
            url,
            ttl_s=settings.jwt_jwks_cache_ttl_seconds,
            timeout_s=settings.jwt_jwks_timeout_ms / 1000,
            cooldown_s=settings.jwt_jwks_refresh_cooldown_seconds,
            max_bytes=settings.jwt_jwks_max_bytes,
            transport=transport,
            clock=clock,
        )
        verifier = JwtVerifier(
            jwks,
            issuer=str(settings.jwt_issuer),
            audience=str(settings.jwt_audience),
            algorithms=algorithms,
            scope_claim=settings.jwt_scope_claim,
            leeway_s=settings.jwt_leeway_seconds,
        )
        return cls("jwt", jwt_verifier=verifier, max_token_bytes=settings.auth_max_token_bytes)

    def describe(self) -> dict[str, Any]:
        """For the start log: mode, key names or the JWT issuer (never key values)."""
        out: dict[str, Any] = {"auth_mode": self.mode}
        if self.api_keys is not None:
            out["api_keys"] = self.api_keys.names
        if self.jwt is not None:
            out.update(jwt_issuer=self.jwt.issuer, jwt_audience=self.jwt.audience, jwks_url=self.jwt.jwks.url)
        return out

    async def authenticate(self, authorization: str | None) -> Principal:
        """Principal of an ``Authorization`` header value; 401 ``unauthenticated`` when it is not valid."""
        if self.mode == "none":
            return ANONYMOUS
        if not authorization:
            raise _unauthenticated("bearer token required", None)
        if len(authorization) > self.max_token_bytes:
            raise _unauthenticated("bearer token is too long")
        scheme, _, token = authorization.strip().partition(" ")
        token = token.strip()
        if scheme.lower() != "bearer" or not token or " " in token:
            raise _unauthenticated("Authorization must be 'Bearer <token>'", "invalid_request")
        if self.api_keys is not None:
            principal = self.api_keys.verify(token)
            if principal is None:
                raise _unauthenticated("invalid API key")
            return principal
        assert self.jwt is not None
        return await self.jwt.verify(token)


# ----------------------------------------------------------------------------- FastAPI wiring
def _normalize(table: ScopeTable) -> dict[str, tuple[str, ...]]:
    out: dict[str, tuple[str, ...]] = {}
    for key, value in table.items():
        method, _, path = key.partition(" ")
        if not method.isupper() or not path.startswith("/"):
            raise AuthConfigError(f"scope table key must be 'METHOD /path', got {key!r}")
        scopes = (value,) if isinstance(value, str) else tuple(value)
        bad = [s for s in scopes if not SCOPE_RE.match(s)]
        if bad:
            raise AuthConfigError(f"{key}: invalid scope(s) {bad}")
        out[key] = scopes
    return out


_HTTP_METHODS = ("get", "put", "post", "delete", "patch")


def _routes(app: FastAPI) -> set[tuple[str, str]]:
    """``(METHOD, path template)`` of every operation: the routes of the application (also those hidden from
    the schema) and, for routers included with a prefix, the operations of its OpenAPI document."""
    out: set[tuple[str, str]] = set()
    for route in app.router.routes:
        path = getattr(route, "path", None)
        if isinstance(path, str):
            out |= {(m, path) for m in getattr(route, "methods", None) or () if m not in {"HEAD", "OPTIONS"}}
    try:
        paths = app.openapi().get("paths", {})
    except Exception:  # a schema problem must not hide routes from the check: those found above stay
        log.warning("OpenAPI document of the service cannot be built; scope check uses the top-level routes")
        paths = {}
    for path, item in paths.items():
        out |= {(m.upper(), path) for m in _HTTP_METHODS if m in item}
    return out


def unmapped_routes(app: FastAPI, table: ScopeTable, *, open_paths: Iterable[str] = OPEN_PATHS) -> list[str]:
    """``"METHOD /path"`` of routes that the scope table (plus :data:`BUILTIN_SCOPES`) does not cover."""
    known = {**BUILTIN_SCOPES, **_normalize(table)}
    skip = set(open_paths)
    return sorted(f"{m} {p}" for m, p in _routes(app) if p not in skip and f"{m} {p}" not in known)


class AuthMiddleware:
    """ASGI middleware: authenticates every request except the open paths (401 ``unauthenticated``)."""

    def __init__(self, app: ASGIApp, *, authenticator: Authenticator, open_paths: frozenset[str]) -> None:
        self.app = app
        self.auth = authenticator
        self.open_paths = open_paths

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in self.open_paths:
            await self.app(scope, receive, send)
            return
        values = [v for k, v in scope["headers"] if k == b"authorization"]
        try:
            if len(values) > 1:
                raise _unauthenticated("only one Authorization header is allowed", "invalid_request")
            header = values[0].decode("latin-1") if values else None
            scope.setdefault("state", {})["principal"] = await self.auth.authenticate(header)
        except JaneError as exc:
            response = problem_response(exc.to_problem(instance=scope["path"]), exc.headers or None)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


async def authorize(request: Request) -> None:
    """Application-wide dependency of ``create_app``: the scope of the matched operation from the service's
    table (403 ``forbidden``). An operation missing from the table is denied (fail closed)."""
    table: dict[str, tuple[str, ...]] | None = getattr(request.app.state, "auth_scopes", None)
    if table is None or request.scope["path"] in request.app.state.auth_open_paths:
        return
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    method = request.method
    key = f"{method} {path}"
    if key not in table and method == "HEAD":
        key = f"GET {path}"
    required = table.get(key)
    if required is None:
        log.error(
            "operation has no scope in the service's table - denied",
            extra={"method": method, "path": request.scope["path"], "route": path},
        )
        raise Forbidden("operation is not mapped to a scope")
    principal_of(request).require(*required)


def install_auth(
    app: FastAPI,
    settings: AuthSettings,
    *,
    scopes: ScopeTable | None = None,
    authenticator: Authenticator | None = None,
) -> Authenticator:
    """Add authentication to ``app`` and remember its scope table; called by ``create_app``, which also
    registers :func:`authorize` as an application-wide dependency.

    Raises :class:`AuthConfigError` for an incomplete configuration. ``scopes=None`` leaves the scope checks
    to the handlers (:func:`require`, :func:`principal_of`); with a table every route must be listed
    (checked at start: :func:`check_scopes`).
    """
    auth = authenticator or Authenticator.from_settings(settings)
    host = str(getattr(settings, "host", "127.0.0.1"))
    if auth.mode == "none" and not _is_loopback(host) and not settings.auth_none_allow_remote:
        raise AuthConfigError(
            f"auth_mode=none is for local tests and listens on loopback only, but host={host}; "
            "use api_key or jwt (or set auth_none_allow_remote=true in an isolated test network)"
        )
    open_paths = frozenset(OPEN_PATHS | ({"/metrics"} if settings.metrics_public else set()))
    app.state.auth = auth
    app.state.auth_scopes = None if scopes is None else {**BUILTIN_SCOPES, **_normalize(scopes)}
    app.state.auth_open_paths = open_paths
    app.add_middleware(AuthMiddleware, authenticator=auth, open_paths=open_paths)
    return auth


def check_scopes(app: FastAPI) -> None:
    """At start: every route of ``app`` must be in its scope table (fail closed); logs the auth mode."""
    auth: Authenticator | None = getattr(app.state, "auth", None)
    if auth is None:
        return
    if auth.mode == "none":
        log.warning("auth_mode=none: every caller has every scope - for local tests only")
    else:
        log.info("authentication enabled", extra=auth.describe())
    table = getattr(app.state, "auth_scopes", None)
    if table is None:
        return
    missing = unmapped_routes(app, table, open_paths=app.state.auth_open_paths)
    if missing:
        raise AuthConfigError(f"routes without a scope in the service's auth table: {missing}")


def principal_of(request: Request) -> Principal:
    """The caller authenticated by the middleware; 401 if there is none (authentication not installed)."""
    principal = getattr(request.state, "principal", None)
    if not isinstance(principal, Principal):
        raise _unauthenticated("request is not authenticated", None)
    return principal


def require(*any_of: str) -> Callable[[Request], Principal]:
    """FastAPI dependency: the caller must have one of ``any_of``; returns the :class:`Principal`."""

    def dependency(request: Request) -> Principal:
        principal = principal_of(request)
        principal.require(*any_of)
        return principal

    return dependency
