# Модуль `jane_kit.auth`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/auth.py](../../../../../libs/jane-kit/src/jane_kit/auth.py). Не редагуйте вручну.

Authentication and scopes of Jane services (ADR-0005), one implementation for every service.

Modes (``auth_mode``, env ``<PREFIX>AUTH_MODE``):

* ``none`` - local tests only. Every caller is ``anonymous`` with every scope; a warning is logged at start, and a ``host`` other than loopback is refused unless ``auth_none_allow_remote=true``;
* ``api_key`` - static keys from configuration (``api_keys`` as JSON, ``api_keys_file`` as a JSON/YAML list): ``{"name", "scopes": [...], "sha256": "<hex of the key>"}`` or, instead of ``sha256``, ``"secret_ref": "env:VAR" | "file:/run/secrets/x"`` (ADR-0006) which is resolved once at start and kept only as its hash. Further fields of an entry (e.g. ``actor`` of the registry) become :attr:`Principal.attributes`;
* ``jwt`` - RS*/PS*/ES* tokens verified with the keys published at ``jwt_jwks_url`` (cached for ``jwt_jwks_cache_ttl_seconds``, fetched within ``jwt_jwks_timeout_ms``). The IdP is asked at most once per ``jwt_jwks_refresh_cooldown_seconds`` - for an expired cache, an unknown ``kid`` and after a failed fetch alike; meanwhile known keys keep working and, without any keys, requests get 503 at once. ``iss``/``aud``/ ``exp`` are required and ``nbf`` checked. Scopes come from the ``scope`` claim (space separated or a list). ``alg=none`` and HMAC algorithms are never accepted (a public key must not become an HMAC secret).

Incomplete configuration is an error at start (fail closed): ``api_key`` without keys, ``jwt`` without JWKS URL / issuer / audience, an unresolvable ``secret_ref``, a scope table that misses a route.

Paths: ``/v1/health`` needs no token, and ``/metrics`` neither unless ``metrics_public=false``. Every other path needs a valid token (401 ``unauthenticated``). Scopes (403 ``forbidden``) come either from the service's table ``"METHOD /path/template" -> scope`` (``create_app(..., auth_scopes=...)``; a tuple means "any of", an empty tuple "any valid token"; ``GET /v1/info`` and the OpenAPI pages are "any valid token"), or, when the service passes no table, from its handlers via :func:`principal_of` / :func:`require`.

## Зміст

- [Клас `ApiKeyConfig`](#клас-apikeyconfig)
- [Клас `AuthConfigError`](#клас-authconfigerror)
- [Клас `AuthSettings`](#клас-authsettings)
- [Клас `Authenticator`](#клас-authenticator)
- [Клас `JwksCache`](#клас-jwkscache)
- [Клас `Principal`](#клас-principal)
- [Клас `SecretRefError`](#клас-secretreferror)
- [Функція `authorize`](#функція-authorize)
- [Функція `bearer_header`](#функція-bearer_header)
- [Функція `check_scopes`](#функція-check_scopes)
- [Функція `install_auth`](#функція-install_auth)
- [Функція `principal_of`](#функція-principal_of)
- [Функція `require`](#функція-require)
- [Функція `resolve_secret_ref`](#функція-resolve_secret_ref)
- [Функція `sha256_hex`](#функція-sha256_hex)
- [Функція `unmapped_routes`](#функція-unmapped_routes)

## Класи

### Клас `ApiKeyConfig`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.auth` |
| Успадкування | `BaseModel` |
| Код | [auth.py:151](../../../../../libs/jane-kit/src/jane_kit/auth.py#L151) |

```python
class ApiKeyConfig(BaseModel): ...
```

One configured API key. Extra fields (e.g. ``actor``) are kept as :attr:`Principal.attributes`.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | `Field(min_length=1, max_length=128, pattern='^[A-Za-z0-9][A-Za-z0-9._@:-]*$')` | читання |  |
| `scopes` | `list[str]` | — | читання |  |
| `sha256` | `str \| None` | `Field(default=None, pattern='^[0-9a-fA-F]{64}$')` | читання |  |
| `secret_ref` | `str \| None` | `None` | читання |  |
| `attributes` | `dict[str, Any]` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='allow', frozen=True)` |  |

### Клас `AuthConfigError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.auth` |
| Успадкування | `ValueError` |
| Код | [auth.py:104](../../../../../libs/jane-kit/src/jane_kit/auth.py#L104) |

```python
class AuthConfigError(ValueError): ...
```

Authentication is configured incompletely or wrongly; the service must not start.

### Клас `AuthSettings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.auth` |
| Успадкування | `BaseModel` |
| Код | [auth.py:113](../../../../../libs/jane-kit/src/jane_kit/auth.py#L113) |

```python
class AuthSettings(BaseModel): ...
```

Authentication knobs; part of every service's settings (``JaneSettings``), env ``<PREFIX><NAME>``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `auth_mode` | `AuthMode` | `'none'` | читання й запис | ``none`` (local tests only), ``api_key`` (dev stack default) or ``jwt`` (production), ADR-0005. |
| `auth_none_allow_remote` | `bool` | `False` | читання й запис | ``auth_mode=none`` with a non-loopback ``host`` refuses to start unless this is true (isolated test networks only). |
| `api_keys` | `list[dict[str, Any]]` | `Field(default_factory=list)` | читання й запис | ``api_key``: ``[{"name", "scopes": [...], "sha256": "<hex>" \| "secret_ref": "env:VAR"\|"file:/path"}]``. |
| `api_keys_file` | `Path \| None` | `None` | читання й запис | ``api_key``: JSON or YAML file with the same list (added to ``api_keys``). |
| `jwt_jwks_url` | `str \| None` | `None` | читання й запис | ``jwt``: JWKS of the identity provider (HTTPS; plain HTTP only for a loopback host). |
| `jwt_issuer` | `str \| None` | `None` | читання й запис | ``jwt``: required ``iss``. |
| `jwt_audience` | `str \| None` | `None` | читання й запис | ``jwt``: required ``aud`` (this service's audience at the identity provider). |
| `jwt_algorithms` | `list[str]` | `Field(default_factory=lambda: ['RS256', 'ES256'])` | читання й запис | ``jwt``: accepted algorithms, a subset of :data:`JWT_ALGORITHMS`. |
| `jwt_scope_claim` | `str` | `'scope'` | читання й запис | ``jwt``: claim with the scopes (space separated string or list of strings). |
| `jwt_leeway_seconds` | `int` | `Field(default=30, ge=0, le=600)` | читання й запис | ``jwt``: allowed clock skew for ``exp``/``nbf``/``iat``. |
| `jwt_jwks_cache_ttl_seconds` | `int` | `Field(default=300, ge=1)` | читання й запис | ``jwt``: how long fetched keys are used before the JWKS is fetched again. |
| `jwt_jwks_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис | ``jwt``: time box of one JWKS request. |
| `jwt_jwks_refresh_cooldown_seconds` | `int` | `Field(default=10, ge=0)` | читання й запис | ``jwt``: minimum time between two fetches caused by an unknown ``kid`` (protects the IdP). |
| `jwt_jwks_max_bytes` | `int` | `Field(default=1048576, ge=1024)` | читання й запис | ``jwt``: largest accepted JWKS document. |
| `auth_max_token_bytes` | `int` | `Field(default=16384, ge=256)` | читання й запис | Longest accepted bearer token; longer ones are rejected with 401 before any parsing. |
| `metrics_public` | `bool` | `True` | читання й запис | ``/metrics`` without a token (Prometheus scraping inside the deployment); false - any valid token. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `Authenticator`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.auth` |
| Код | [auth.py:535](../../../../../libs/jane-kit/src/jane_kit/auth.py#L535) |

```python
class Authenticator: ...
```

Checks ``Authorization: Bearer <token>`` according to the mode; build it with :meth:`from_settings`.

#### Конструктор `Authenticator.__init__`

```python
def __init__(
    self,
    mode: AuthMode,
    *,
    api_keys: ApiKeyVerifier | None = None,
    jwt_verifier: JwtVerifier | None = None,
    max_token_bytes: int = 16384,
) -> None: ...
```

Винятки в коді методу: `AuthConfigError`.

Код: [auth.py:538](../../../../../libs/jane-kit/src/jane_kit/auth.py#L538).

#### Метод `Authenticator.from_settings`

```python
@classmethod
def from_settings(
    cls,
    settings: AuthSettings,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
    environ: Mapping[str, str] | None = None,
    clock: _Clock = time.monotonic,
) -> Authenticator: ...
```

Fail-closed construction: raises :class:`AuthConfigError` for an incomplete configuration.

Винятки в коді методу: `AuthConfigError`.

Код: [auth.py:556](../../../../../libs/jane-kit/src/jane_kit/auth.py#L556).

#### Метод `Authenticator.describe`

```python
def describe(self) -> dict[str, Any]: ...
```

For the start log: mode, key names or the JWT issuer (never key values).

Код: [auth.py:614](../../../../../libs/jane-kit/src/jane_kit/auth.py#L614).

#### Метод `Authenticator.authenticate`

```python
async def authenticate(self, authorization: str | None) -> Principal: ...
```

Principal of an ``Authorization`` header value; 401 ``unauthenticated`` when it is not valid.

Код: [auth.py:623](../../../../../libs/jane-kit/src/jane_kit/auth.py#L623).

### Клас `JwksCache`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.auth` |
| Код | [auth.py:335](../../../../../libs/jane-kit/src/jane_kit/auth.py#L335) |

```python
class JwksCache: ...
```

Signing keys of the identity provider, fetched on demand and cached for ``ttl_s``.

The IdP gets at most one request per ``cooldown_s``, whatever triggers it (empty or expired cache, a token with an unknown ``kid``) and whether the previous attempt succeeded or failed; concurrent requests wait for the one fetch in progress instead of starting their own. Between attempts:

* a token whose ``kid`` is in the cache is checked with that key, also while the cache is being refreshed or after a failed refresh (stale keys stay in use);
* an unknown ``kid`` is answered from the cache (-> 401) without contacting the IdP;
* without any keys every request fails at once with 503 ``service_unavailable`` (the IdP is unavailable, the token is not necessarily wrong) - one warning per failed attempt, not per request.

#### Конструктор `JwksCache.__init__`

```python
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
) -> None: ...
```

Код: [auth.py:349](../../../../../libs/jane-kit/src/jane_kit/auth.py#L349).

#### Метод `JwksCache.key`

```python
async def key(self, kid: str | None) -> dict[str, Any] | None: ...
```

The JWK for ``kid`` (``None`` - unknown key, 401); raises 503 when no keys are available.

Код: [auth.py:448](../../../../../libs/jane-kit/src/jane_kit/auth.py#L448).

### Клас `Principal`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.auth` |
| Код | [auth.py:229](../../../../../libs/jane-kit/src/jane_kit/auth.py#L229) |

```python
@dataclass(frozen=True)
class Principal: ...
```

The authenticated caller: key name / JWT subject, its scopes and extra attributes.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання |  |
| `scopes` | `frozenset[str]` | — | читання |  |
| `method` | `AuthMode` | — | читання |  |
| `attributes` | `Mapping[str, Any]` | `field(default_factory=dict)` | читання | ``api_key``: extra fields of the key entry; ``jwt``: the token's claims. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Principal.has`

```python
def has(self, scope: str) -> bool: ...
```

Код: [auth.py:238](../../../../../libs/jane-kit/src/jane_kit/auth.py#L238).

#### Метод `Principal.require`

```python
def require(self, *any_of: str) -> None: ...
```

403 ``forbidden`` unless the principal has one of ``any_of`` (no arguments - nothing required).

Винятки в коді методу: `Forbidden`.

Код: [auth.py:241](../../../../../libs/jane-kit/src/jane_kit/auth.py#L241).

### Клас `SecretRefError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.auth` |
| Успадкування | `AuthConfigError` |
| Код | [auth.py:108](../../../../../libs/jane-kit/src/jane_kit/auth.py#L108) |

```python
class SecretRefError(AuthConfigError): ...
```

A secret reference cannot be resolved. The message never contains a secret value.

## Функції

### Функція `authorize`

```python
async def authorize(request: Request) -> None: ...
```

Application-wide dependency of ``create_app``: the scope of the matched operation from the service's table (403 ``forbidden``). An operation missing from the table is denied (fail closed).

Винятки в коді функції: `Forbidden`.

Код: [auth.py:712](../../../../../libs/jane-kit/src/jane_kit/auth.py#L712).

### Функція `bearer_header`

```python
def bearer_header(token: str | None) -> dict[str, str]: ...
```

``{"Authorization": "Bearer <token>"}`` or ``{}`` - for clients of other Jane services.

Код: [auth.py:186](../../../../../libs/jane-kit/src/jane_kit/auth.py#L186).

### Функція `check_scopes`

```python
def check_scopes(app: FastAPI) -> None: ...
```

At start: every route of ``app`` must be in its scope table (fail closed); logs the auth mode.

Винятки в коді функції: `AuthConfigError`.

Код: [auth.py:763](../../../../../libs/jane-kit/src/jane_kit/auth.py#L763).

### Функція `install_auth`

```python
def install_auth(
    app: FastAPI,
    settings: AuthSettings,
    *,
    scopes: ScopeTable | None = None,
    authenticator: Authenticator | None = None,
) -> Authenticator: ...
```

Add authentication to ``app`` and remember its scope table; called by ``create_app``, which also registers :func:`authorize` as an application-wide dependency.

Raises :class:`AuthConfigError` for an incomplete configuration. ``scopes=None`` leaves the scope checks to the handlers (:func:`require`, :func:`principal_of`); with a table every route must be listed (checked at start: :func:`check_scopes`).

Винятки в коді функції: `AuthConfigError`.

Код: [auth.py:734](../../../../../libs/jane-kit/src/jane_kit/auth.py#L734).

### Функція `principal_of`

```python
def principal_of(request: Request) -> Principal: ...
```

The caller authenticated by the middleware; 401 if there is none (authentication not installed).

Код: [auth.py:780](../../../../../libs/jane-kit/src/jane_kit/auth.py#L780).

### Функція `require`

```python
def require(*any_of: str) -> Callable[[Request], Principal]: ...
```

FastAPI dependency: the caller must have one of ``any_of``; returns the :class:`Principal`.

Код: [auth.py:788](../../../../../libs/jane-kit/src/jane_kit/auth.py#L788).

### Функція `resolve_secret_ref`

```python
def resolve_secret_ref(ref: str, *, environ: Mapping[str, str] | None = None) -> str: ...
```

Value of ``env:VAR`` or ``file:/path`` (surrounding whitespace stripped). ``vault:`` is not supported by this build (ADR-0006: optional provider). Raises :class:`SecretRefError` without revealing values.

Винятки в коді функції: `SecretRefError`.

Код: [auth.py:191](../../../../../libs/jane-kit/src/jane_kit/auth.py#L191).

### Функція `sha256_hex`

```python
def sha256_hex(value: str) -> str: ...
```

Hex SHA-256 of a key, the form ``api_keys[].sha256`` stores.

Код: [auth.py:181](../../../../../libs/jane-kit/src/jane_kit/auth.py#L181).

### Функція `unmapped_routes`

```python
def unmapped_routes(
    app: FastAPI,
    table: ScopeTable,
    *,
    open_paths: Iterable[str] = OPEN_PATHS,
) -> list[str]: ...
```

``"METHOD /path"`` of routes that the scope table (plus :data:`BUILTIN_SCOPES`) does not cover.

Код: [auth.py:680](../../../../../libs/jane-kit/src/jane_kit/auth.py#L680).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `AUTHENTICATED` | `tuple[str, ...]` | `()` | Table value for operations that need a valid token but no particular scope. |
| `BUILTIN_SCOPES` | `dict[str, tuple[str, ...]]` | `{'GET /v1/info': AUTHENTICATED, 'GET /metrics': AUTHENTICATED, 'GET /openapi.jso` | Routes every service has (jane-kit, FastAPI); a service's table may override them. |
| `JWT_ALGORITHMS` | — | `frozenset({'RS256', 'RS384', 'RS512', 'PS256', 'PS384', 'PS512', 'ES256', 'ES384` | Asymmetric algorithms ``jwt_algorithms`` may list; ``none`` and ``HS*`` are rejected. |
| `ScopeTable` | — | `Mapping[str, str \| Sequence[str]]` | ``"METHOD /path/template"`` (as registered in FastAPI) -> scope, or any-of scopes (empty = any valid token). |
