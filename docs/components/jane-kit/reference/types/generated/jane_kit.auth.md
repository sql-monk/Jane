# jane_kit.auth

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.auth.AUTHENTICATED](#jane_kitauthauthenticated)
- [jane_kit.auth.JWT_ALGORITHMS](#jane_kitauthjwt_algorithms)
- [jane_kit.auth.BUILTIN_SCOPES](#jane_kitauthbuiltin_scopes)
- [jane_kit.auth.ScopeTable](#jane_kitauthscopetable)
- [jane_kit.auth.AuthConfigError](#jane_kitauthauthconfigerror)
- [jane_kit.auth.SecretRefError](#jane_kitauthsecretreferror)
- [jane_kit.auth.AuthSettings](#jane_kitauthauthsettings)
- [jane_kit.auth.AuthSettings.auth_mode](#jane_kitauthauthsettingsauth_mode)
- [jane_kit.auth.AuthSettings.auth_none_allow_remote](#jane_kitauthauthsettingsauth_none_allow_remote)
- [jane_kit.auth.AuthSettings.api_keys](#jane_kitauthauthsettingsapi_keys)
- [jane_kit.auth.AuthSettings.api_keys_file](#jane_kitauthauthsettingsapi_keys_file)
- [jane_kit.auth.AuthSettings.jwt_jwks_url](#jane_kitauthauthsettingsjwt_jwks_url)
- [jane_kit.auth.AuthSettings.jwt_issuer](#jane_kitauthauthsettingsjwt_issuer)
- [jane_kit.auth.AuthSettings.jwt_audience](#jane_kitauthauthsettingsjwt_audience)
- [jane_kit.auth.AuthSettings.jwt_algorithms](#jane_kitauthauthsettingsjwt_algorithms)
- [jane_kit.auth.AuthSettings.jwt_scope_claim](#jane_kitauthauthsettingsjwt_scope_claim)
- [jane_kit.auth.AuthSettings.jwt_leeway_seconds](#jane_kitauthauthsettingsjwt_leeway_seconds)
- [jane_kit.auth.AuthSettings.jwt_jwks_cache_ttl_seconds](#jane_kitauthauthsettingsjwt_jwks_cache_ttl_seconds)
- [jane_kit.auth.AuthSettings.jwt_jwks_timeout_ms](#jane_kitauthauthsettingsjwt_jwks_timeout_ms)
- [jane_kit.auth.AuthSettings.jwt_jwks_refresh_cooldown_seconds](#jane_kitauthauthsettingsjwt_jwks_refresh_cooldown_seconds)
- [jane_kit.auth.AuthSettings.jwt_jwks_max_bytes](#jane_kitauthauthsettingsjwt_jwks_max_bytes)
- [jane_kit.auth.AuthSettings.auth_max_token_bytes](#jane_kitauthauthsettingsauth_max_token_bytes)
- [jane_kit.auth.AuthSettings.metrics_public](#jane_kitauthauthsettingsmetrics_public)
- [jane_kit.auth.ApiKeyConfig](#jane_kitauthapikeyconfig)
- [jane_kit.auth.ApiKeyConfig.model_config](#jane_kitauthapikeyconfigmodel_config)
- [jane_kit.auth.ApiKeyConfig.name](#jane_kitauthapikeyconfigname)
- [jane_kit.auth.ApiKeyConfig.scopes](#jane_kitauthapikeyconfigscopes)
- [jane_kit.auth.ApiKeyConfig.sha256](#jane_kitauthapikeyconfigsha256)
- [jane_kit.auth.ApiKeyConfig.secret_ref](#jane_kitauthapikeyconfigsecret_ref)
- [jane_kit.auth.ApiKeyConfig.attributes](#jane_kitauthapikeyconfigattributes)
- [jane_kit.auth.sha256_hex](#jane_kitauthsha256_hex)
- [jane_kit.auth.bearer_header](#jane_kitauthbearer_header)
- [jane_kit.auth.resolve_secret_ref](#jane_kitauthresolve_secret_ref)
- [jane_kit.auth.Principal](#jane_kitauthprincipal)
- [jane_kit.auth.Principal.__init__](#jane_kitauthprincipal__init__)
- [jane_kit.auth.Principal.name](#jane_kitauthprincipalname)
- [jane_kit.auth.Principal.scopes](#jane_kitauthprincipalscopes)
- [jane_kit.auth.Principal.method](#jane_kitauthprincipalmethod)
- [jane_kit.auth.Principal.attributes](#jane_kitauthprincipalattributes)
- [jane_kit.auth.Principal.has](#jane_kitauthprincipalhas)
- [jane_kit.auth.Principal.require](#jane_kitauthprincipalrequire)
- [jane_kit.auth.JwksCache](#jane_kitauthjwkscache)
- [jane_kit.auth.JwksCache.__init__](#jane_kitauthjwkscache__init__)
- [jane_kit.auth.JwksCache.url](#jane_kitauthjwkscacheurl)
- [jane_kit.auth.JwksCache.ttl_s](#jane_kitauthjwkscachettl_s)
- [jane_kit.auth.JwksCache.timeout_s](#jane_kitauthjwkscachetimeout_s)
- [jane_kit.auth.JwksCache.cooldown_s](#jane_kitauthjwkscachecooldown_s)
- [jane_kit.auth.JwksCache.max_bytes](#jane_kitauthjwkscachemax_bytes)
- [jane_kit.auth.JwksCache.fetches](#jane_kitauthjwkscachefetches)
- [jane_kit.auth.JwksCache.key](#jane_kitauthjwkscachekey)
- [jane_kit.auth.Authenticator](#jane_kitauthauthenticator)
- [jane_kit.auth.Authenticator.__init__](#jane_kitauthauthenticator__init__)
- [jane_kit.auth.Authenticator.mode](#jane_kitauthauthenticatormode)
- [jane_kit.auth.Authenticator.api_keys](#jane_kitauthauthenticatorapi_keys)
- [jane_kit.auth.Authenticator.jwt](#jane_kitauthauthenticatorjwt)
- [jane_kit.auth.Authenticator.max_token_bytes](#jane_kitauthauthenticatormax_token_bytes)
- [jane_kit.auth.Authenticator.from_settings](#jane_kitauthauthenticatorfrom_settings)
- [jane_kit.auth.Authenticator.describe](#jane_kitauthauthenticatordescribe)
- [jane_kit.auth.Authenticator.authenticate](#jane_kitauthauthenticatorauthenticate)
- [jane_kit.auth.unmapped_routes](#jane_kitauthunmapped_routes)
- [jane_kit.auth.authorize](#jane_kitauthauthorize)
- [jane_kit.auth.install_auth](#jane_kitauthinstall_auth)
- [jane_kit.auth.check_scopes](#jane_kitauthcheck_scopes)
- [jane_kit.auth.principal_of](#jane_kitauthprincipal_of)
- [jane_kit.auth.require](#jane_kitauthrequire)

## jane_kit.auth.AUTHENTICATED

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth.py:83](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L83).

```python
AUTHENTICATED: tuple[str, ...] = ()
```

### Опис із вихідного коду

```text
Table value for operations that need a valid token but no particular scope.
```

## jane_kit.auth.JWT_ALGORITHMS

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth.py:85](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L85).

```python
JWT_ALGORITHMS = frozenset({'RS256', 'RS384', 'RS512', 'PS256', 'PS384', 'PS512', 'ES256', 'ES384', 'ES512'})
```

### Опис із вихідного коду

```text
Asymmetric algorithms ``jwt_algorithms`` may list; ``none`` and ``HS*`` are rejected.
```

## jane_kit.auth.BUILTIN_SCOPES

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth.py:90](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L90).

```python
BUILTIN_SCOPES: dict[str, tuple[str, ...]] = {'GET /v1/info': AUTHENTICATED, 'GET /metrics': AUTHENTICATED, 'GET /openapi.json': AUTHENTICATED, 'GET /docs': AUTHENTICATED, 'GET /docs/oauth2-redirect': AUTHENTICATED, 'GET /redoc': AUTHENTICATED}
```

### Опис із вихідного коду

```text
Routes every service has (jane-kit, FastAPI); a service's table may override them.
```

## jane_kit.auth.ScopeTable

**Змінна.** Код: [libs/jane-kit/src/jane_kit/auth.py:100](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L100).

```python
ScopeTable = Mapping[str, str | Sequence[str]]
```

### Опис із вихідного коду

```text
``"METHOD /path/template"`` (as registered in FastAPI) -> scope, or any-of scopes (empty = any valid token).
```

## jane_kit.auth.AuthConfigError

**Клас.** Код: [libs/jane-kit/src/jane_kit/auth.py:104](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L104).

```python
class AuthConfigError(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Опис із вихідного коду

```text
Authentication is configured incompletely or wrongly; the service must not start.
```

## jane_kit.auth.SecretRefError

**Клас.** Код: [libs/jane-kit/src/jane_kit/auth.py:108](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L108).

```python
class SecretRefError(AuthConfigError):
```

Базові типи / інтерфейси: `AuthConfigError`.

### Опис із вихідного коду

```text
A secret reference cannot be resolved. The message never contains a secret value.
```

## jane_kit.auth.AuthSettings

**Клас.** Код: [libs/jane-kit/src/jane_kit/auth.py:113](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L113).

```python
class AuthSettings(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [auth_mode](jane_kit.auth.md#jane_kitauthauthsettingsauth_mode) | Поле | ні |
| [auth_none_allow_remote](jane_kit.auth.md#jane_kitauthauthsettingsauth_none_allow_remote) | Поле | ні |
| [api_keys](jane_kit.auth.md#jane_kitauthauthsettingsapi_keys) | Поле | ні |
| [api_keys_file](jane_kit.auth.md#jane_kitauthauthsettingsapi_keys_file) | Поле | ні |
| [jwt_jwks_url](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_url) | Поле | ні |
| [jwt_issuer](jane_kit.auth.md#jane_kitauthauthsettingsjwt_issuer) | Поле | ні |
| [jwt_audience](jane_kit.auth.md#jane_kitauthauthsettingsjwt_audience) | Поле | ні |
| [jwt_algorithms](jane_kit.auth.md#jane_kitauthauthsettingsjwt_algorithms) | Поле | ні |
| [jwt_scope_claim](jane_kit.auth.md#jane_kitauthauthsettingsjwt_scope_claim) | Поле | ні |
| [jwt_leeway_seconds](jane_kit.auth.md#jane_kitauthauthsettingsjwt_leeway_seconds) | Поле | ні |
| [jwt_jwks_cache_ttl_seconds](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_cache_ttl_seconds) | Поле | ні |
| [jwt_jwks_timeout_ms](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_timeout_ms) | Поле | ні |
| [jwt_jwks_refresh_cooldown_seconds](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_refresh_cooldown_seconds) | Поле | ні |
| [jwt_jwks_max_bytes](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_max_bytes) | Поле | ні |
| [auth_max_token_bytes](jane_kit.auth.md#jane_kitauthauthsettingsauth_max_token_bytes) | Поле | ні |
| [metrics_public](jane_kit.auth.md#jane_kitauthauthsettingsmetrics_public) | Поле | ні |

### Опис із вихідного коду

```text
Authentication knobs; part of every service's settings (``JaneSettings``), env ``<PREFIX><NAME>``.
```

## jane_kit.auth.AuthSettings.auth_mode

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:116](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L116).

```python
auth_mode: AuthMode = 'none'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``none`` (local tests only), ``api_key`` (dev stack default) or ``jwt`` (production), ADR-0005.
```

## jane_kit.auth.AuthSettings.auth_none_allow_remote

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:118](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L118).

```python
auth_none_allow_remote: bool = False
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``auth_mode=none`` with a non-loopback ``host`` refuses to start unless this is true (isolated test
    networks only).
```

## jane_kit.auth.AuthSettings.api_keys

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:121](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L121).

```python
api_keys: list[dict[str, Any]] = Field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

### Опис із вихідного коду

```text
``api_key``: ``[{"name", "scopes": [...], "sha256": "<hex>" | "secret_ref": "env:VAR"|"file:/path"}]``.
```

## jane_kit.auth.AuthSettings.api_keys_file

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:123](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L123).

```python
api_keys_file: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``api_key``: JSON or YAML file with the same list (added to ``api_keys``).
```

## jane_kit.auth.AuthSettings.jwt_jwks_url

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:125](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L125).

```python
jwt_jwks_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``jwt``: JWKS of the identity provider (HTTPS; plain HTTP only for a loopback host).
```

## jane_kit.auth.AuthSettings.jwt_issuer

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:127](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L127).

```python
jwt_issuer: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``jwt``: required ``iss``.
```

## jane_kit.auth.AuthSettings.jwt_audience

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:129](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L129).

```python
jwt_audience: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``jwt``: required ``aud`` (this service's audience at the identity provider).
```

## jane_kit.auth.AuthSettings.jwt_algorithms

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:131](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L131).

```python
jwt_algorithms: list[str] = Field(default_factory=lambda: ['RS256', 'ES256'])
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: ['RS256', 'ES256']"
}
```

### Опис із вихідного коду

```text
``jwt``: accepted algorithms, a subset of :data:`JWT_ALGORITHMS`.
```

## jane_kit.auth.AuthSettings.jwt_scope_claim

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:133](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L133).

```python
jwt_scope_claim: str = 'scope'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``jwt``: claim with the scopes (space separated string or list of strings).
```

## jane_kit.auth.AuthSettings.jwt_leeway_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:135](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L135).

```python
jwt_leeway_seconds: int = Field(default=30, ge=0, le=600)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30",
  "ge": "0",
  "le": "600"
}
```

### Опис із вихідного коду

```text
``jwt``: allowed clock skew for ``exp``/``nbf``/``iat``.
```

## jane_kit.auth.AuthSettings.jwt_jwks_cache_ttl_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:137](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L137).

```python
jwt_jwks_cache_ttl_seconds: int = Field(default=300, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "300",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
``jwt``: how long fetched keys are used before the JWKS is fetched again.
```

## jane_kit.auth.AuthSettings.jwt_jwks_timeout_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:139](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L139).

```python
jwt_jwks_timeout_ms: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
``jwt``: time box of one JWKS request.
```

## jane_kit.auth.AuthSettings.jwt_jwks_refresh_cooldown_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:141](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L141).

```python
jwt_jwks_refresh_cooldown_seconds: int = Field(default=10, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
``jwt``: minimum time between two fetches caused by an unknown ``kid`` (protects the IdP).
```

## jane_kit.auth.AuthSettings.jwt_jwks_max_bytes

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:143](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L143).

```python
jwt_jwks_max_bytes: int = Field(default=1048576, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1048576",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
``jwt``: largest accepted JWKS document.
```

## jane_kit.auth.AuthSettings.auth_max_token_bytes

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:145](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L145).

```python
auth_max_token_bytes: int = Field(default=16384, ge=256)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "16384",
  "ge": "256"
}
```

### Опис із вихідного коду

```text
Longest accepted bearer token; longer ones are rejected with 401 before any parsing.
```

## jane_kit.auth.AuthSettings.metrics_public

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:147](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L147).

```python
metrics_public: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``/metrics`` without a token (Prometheus scraping inside the deployment); false - any valid token.
```

## jane_kit.auth.ApiKeyConfig

**Клас.** Код: [libs/jane-kit/src/jane_kit/auth.py:151](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L151).

```python
class ApiKeyConfig(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_kit.auth.md#jane_kitauthapikeyconfigmodel_config) | Поле | ні |
| [name](jane_kit.auth.md#jane_kitauthapikeyconfigname) | Поле | ні |
| [scopes](jane_kit.auth.md#jane_kitauthapikeyconfigscopes) | Поле | ні |
| [sha256](jane_kit.auth.md#jane_kitauthapikeyconfigsha256) | Поле | ні |
| [secret_ref](jane_kit.auth.md#jane_kitauthapikeyconfigsecret_ref) | Поле | ні |
| [attributes](jane_kit.auth.md#jane_kitauthapikeyconfigattributes) | Властивість | ні |

### Опис із вихідного коду

```text
One configured API key. Extra fields (e.g. ``actor``) are kept as :attr:`Principal.attributes`.
```

## jane_kit.auth.ApiKeyConfig.model_config

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:154](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L154).

```python
model_config = ConfigDict(extra='allow', frozen=True)
```

Доступ: читання — так; запис — так.

## jane_kit.auth.ApiKeyConfig.name

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:156](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L156).

```python
name: str = Field(min_length=1, max_length=128, pattern='^[A-Za-z0-9][A-Za-z0-9._@:-]*$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "max_length": "128",
  "min_length": "1",
  "pattern": "'^[A-Za-z0-9][A-Za-z0-9._@:-]*$'"
}
```

## jane_kit.auth.ApiKeyConfig.scopes

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:157](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L157).

```python
scopes: list[str]
```

Доступ: читання — так; запис — так.

## jane_kit.auth.ApiKeyConfig.sha256

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:158](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L158).

```python
sha256: str | None = Field(default=None, pattern='^[0-9a-fA-F]{64}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "pattern": "'^[0-9a-fA-F]{64}$'"
}
```

## jane_kit.auth.ApiKeyConfig.secret_ref

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:159](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L159).

```python
secret_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.auth.ApiKeyConfig.attributes

**Властивість.** Код: [libs/jane-kit/src/jane_kit/auth.py:176](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L176).

```python
def attributes(self) -> dict[str, Any]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Доступ: читання — так; запис — ні.

## jane_kit.auth.sha256_hex

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:181](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L181).

```python
def sha256_hex(value: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Hex SHA-256 of a key, the form ``api_keys[].sha256`` stores.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:51](../../../../../../libs/jane-kit/tests/test_auth.py#L51).

```python
return [
        {"name": "reader", "sha256": sha256_hex("key-reader"), "scopes": ["storage:read"]},
        {"name": "writer", "sha256": sha256_hex("key-writer"), "scopes": ["storage:read", "storage:write"]},
        {"name": "bare", "sha256": sha256_hex("key-bare"), "scopes": [], "actor": "llm"},
    ]
```

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:142](../../../../../../libs/jane-kit/tests/test_auth.py#L142).

```python
keys_file.write_text(
        "- name: yaml\n  sha256: " + sha256_hex("key-yaml") + "\n  scopes: [storage:read]\n", encoding="utf-8"
    )
```

## jane_kit.auth.bearer_header

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:186](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L186).

```python
def bearer_header(token: str | None) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `token` | `str \| None` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

### Опис із вихідного коду

```text
``{"Authorization": "Bearer <token>"}`` or ``{}`` - for clients of other Jane services.
```

## jane_kit.auth.resolve_secret_ref

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:191](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L191).

```python
def resolve_secret_ref(ref: str, *, environ: Mapping[str, str] | None=None) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `ref` | `str` | `—` | positional-or-keyword |
| `environ` | `Mapping[str, str] \| None` | `None` | keyword-only |

Результат: `str`.

Явні `raise` у тілі: `SecretRefError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Value of ``env:VAR`` or ``file:/path`` (surrounding whitespace stripped). ``vault:`` is not supported
by this build (ADR-0006: optional provider). Raises :class:`SecretRefError` without revealing values.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:149](../../../../../../libs/jane-kit/tests/test_auth.py#L149).

```python
assert resolve_secret_ref("env:JANE_TEST_KEY_ENV") == "key-from-env"
```

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:151](../../../../../../libs/jane-kit/tests/test_auth.py#L151).

```python
resolve_secret_ref("vault:kv/jane#key")
```

## jane_kit.auth.Principal

**Клас.** Код: [libs/jane-kit/src/jane_kit/auth.py:229](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L229).

```python
class Principal:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_kit.auth.md#jane_kitauthprincipalname) | Поле | ні |
| [scopes](jane_kit.auth.md#jane_kitauthprincipalscopes) | Поле | ні |
| [method](jane_kit.auth.md#jane_kitauthprincipalmethod) | Поле | ні |
| [attributes](jane_kit.auth.md#jane_kitauthprincipalattributes) | Поле | ні |
| [has](jane_kit.auth.md#jane_kitauthprincipalhas) | Метод | ні |
| [require](jane_kit.auth.md#jane_kitauthprincipalrequire) | Метод | ні |
| [__init__](jane_kit.auth.md#jane_kitauthprincipal__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
The authenticated caller: key name / JWT subject, its scopes and extra attributes.
```

## jane_kit.auth.Principal.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/auth.py:229](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L229).

```python
def __init__(self, name: str, scopes: frozenset[str], method: AuthMode, attributes: Mapping[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `scopes` | `frozenset[str]` | `—` | positional-or-keyword |
| `method` | `AuthMode` | `—` | positional-or-keyword |
| `attributes` | `Mapping[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_kit.auth.Principal.name

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:232](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L232).

```python
name: str
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:235](../../../../../../libs/jane-kit/tests/test_auth.py#L235).

```python
return {"name": p.name, "actor": p.attributes.get("actor")}
```

## jane_kit.auth.Principal.scopes

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:233](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L233).

```python
scopes: frozenset[str]
```

Доступ: читання — так; запис — ні.

## jane_kit.auth.Principal.method

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:234](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L234).

```python
method: AuthMode
```

Доступ: читання — так; запис — ні.

## jane_kit.auth.Principal.attributes

**Поле.** Код: [libs/jane-kit/src/jane_kit/auth.py:235](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L235).

```python
attributes: Mapping[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Опис із вихідного коду

```text
``api_key``: extra fields of the key entry; ``jwt``: the token's claims.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:235](../../../../../../libs/jane-kit/tests/test_auth.py#L235).

```python
return {"name": p.name, "actor": p.attributes.get("actor")}
```

## jane_kit.auth.Principal.has

**Метод.** Код: [libs/jane-kit/src/jane_kit/auth.py:238](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L238).

```python
def has(self, scope: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `scope` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_kit.auth.Principal.require

**Метод.** Код: [libs/jane-kit/src/jane_kit/auth.py:241](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L241).

```python
def require(self, *any_of: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `any_of` | `str` | `—` | var-positional |

Результат: `None`.

Явні `raise` у тілі: `Forbidden`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
403 ``forbidden`` unless the principal has one of ``any_of`` (no arguments - nothing required).
```

## jane_kit.auth.JwksCache

**Клас.** Код: [libs/jane-kit/src/jane_kit/auth.py:335](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L335).

```python
class JwksCache:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.auth.md#jane_kitauthjwkscache__init__) | Конструктор | ні |
| [url](jane_kit.auth.md#jane_kitauthjwkscacheurl) | Поле екземпляра | ні |
| [ttl_s](jane_kit.auth.md#jane_kitauthjwkscachettl_s) | Поле екземпляра | ні |
| [timeout_s](jane_kit.auth.md#jane_kitauthjwkscachetimeout_s) | Поле екземпляра | ні |
| [cooldown_s](jane_kit.auth.md#jane_kitauthjwkscachecooldown_s) | Поле екземпляра | ні |
| [max_bytes](jane_kit.auth.md#jane_kitauthjwkscachemax_bytes) | Поле екземпляра | ні |
| [fetches](jane_kit.auth.md#jane_kitauthjwkscachefetches) | Поле екземпляра | ні |
| [key](jane_kit.auth.md#jane_kitauthjwkscachekey) | Метод | ні |

### Опис із вихідного коду

```text
Signing keys of the identity provider, fetched on demand and cached for ``ttl_s``.

The IdP gets at most one request per ``cooldown_s``, whatever triggers it (empty or expired cache, a token
with an unknown ``kid``) and whether the previous attempt succeeded or failed; concurrent requests wait for
the one fetch in progress instead of starting their own. Between attempts:

* a token whose ``kid`` is in the cache is checked with that key, also while the cache is being refreshed
  or after a failed refresh (stale keys stay in use);
* an unknown ``kid`` is answered from the cache (-> 401) without contacting the IdP;
* without any keys every request fails at once with 503 ``service_unavailable`` (the IdP is unavailable,
  the token is not necessarily wrong) - one warning per failed attempt, not per request.
```

## jane_kit.auth.JwksCache.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/auth.py:349](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L349).

```python
def __init__(self, url: str, *, ttl_s: float, timeout_s: float, cooldown_s: float, max_bytes: int, transport: httpx.AsyncBaseTransport | None=None, clock: _Clock=time.monotonic) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `ttl_s` | `float` | `—` | keyword-only |
| `timeout_s` | `float` | `—` | keyword-only |
| `cooldown_s` | `float` | `—` | keyword-only |
| `max_bytes` | `int` | `—` | keyword-only |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |
| `clock` | `_Clock` | `time.monotonic` | keyword-only |

Результат: `None`.

## jane_kit.auth.JwksCache.url

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:360](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L360).

```python
self.url = url
```

## jane_kit.auth.JwksCache.ttl_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:361](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L361).

```python
self.ttl_s = ttl_s
```

## jane_kit.auth.JwksCache.timeout_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:362](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L362).

```python
self.timeout_s = timeout_s
```

## jane_kit.auth.JwksCache.cooldown_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:363](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L363).

```python
self.cooldown_s = cooldown_s
```

## jane_kit.auth.JwksCache.max_bytes

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:364](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L364).

```python
self.max_bytes = max_bytes
```

## jane_kit.auth.JwksCache.fetches

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:374](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L374).

```python
self.fetches = 0
```

## jane_kit.auth.JwksCache.key

**Метод.** Код: [libs/jane-kit/src/jane_kit/auth.py:448](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L448).

```python
async def key(self, kid: str | None) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kid` | `str \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

Явні `raise` у тілі: `self._unavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
The JWK for ``kid`` (``None`` - unknown key, 401); raises 503 when no keys are available.
```

## jane_kit.auth.Authenticator

**Клас.** Код: [libs/jane-kit/src/jane_kit/auth.py:535](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L535).

```python
class Authenticator:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.auth.md#jane_kitauthauthenticator__init__) | Конструктор | ні |
| [mode](jane_kit.auth.md#jane_kitauthauthenticatormode) | Поле екземпляра | ні |
| [api_keys](jane_kit.auth.md#jane_kitauthauthenticatorapi_keys) | Поле екземпляра | ні |
| [jwt](jane_kit.auth.md#jane_kitauthauthenticatorjwt) | Поле екземпляра | ні |
| [max_token_bytes](jane_kit.auth.md#jane_kitauthauthenticatormax_token_bytes) | Поле екземпляра | ні |
| [from_settings](jane_kit.auth.md#jane_kitauthauthenticatorfrom_settings) | Метод | ні |
| [describe](jane_kit.auth.md#jane_kitauthauthenticatordescribe) | Метод | ні |
| [authenticate](jane_kit.auth.md#jane_kitauthauthenticatorauthenticate) | Метод | ні |

### Опис із вихідного коду

```text
Checks ``Authorization: Bearer <token>`` according to the mode; build it with :meth:`from_settings`.
```

## jane_kit.auth.Authenticator.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/auth.py:538](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L538).

```python
def __init__(self, mode: AuthMode, *, api_keys: ApiKeyVerifier | None=None, jwt_verifier: JwtVerifier | None=None, max_token_bytes: int=16384) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `mode` | `AuthMode` | `—` | positional-or-keyword |
| `api_keys` | `ApiKeyVerifier \| None` | `None` | keyword-only |
| `jwt_verifier` | `JwtVerifier \| None` | `None` | keyword-only |
| `max_token_bytes` | `int` | `16384` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `AuthConfigError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_kit.auth.Authenticator.mode

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:550](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L550).

```python
self.mode = mode
```

## jane_kit.auth.Authenticator.api_keys

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:551](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L551).

```python
self.api_keys = api_keys
```

## jane_kit.auth.Authenticator.jwt

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:552](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L552).

```python
self.jwt = jwt_verifier
```

## jane_kit.auth.Authenticator.max_token_bytes

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/auth.py:553](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L553).

```python
self.max_token_bytes = max_token_bytes
```

## jane_kit.auth.Authenticator.from_settings

**Метод.** Код: [libs/jane-kit/src/jane_kit/auth.py:556](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L556).

```python
def from_settings(cls, settings: AuthSettings, *, transport: httpx.AsyncBaseTransport | None=None, environ: Mapping[str, str] | None=None, clock: _Clock=time.monotonic) -> Authenticator:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `AuthSettings` | `—` | positional-or-keyword |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |
| `environ` | `Mapping[str, str] \| None` | `None` | keyword-only |
| `clock` | `_Clock` | `time.monotonic` | keyword-only |

Результат: `Authenticator`.

Явні `raise` у тілі: `AuthConfigError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Fail-closed construction: raises :class:`AuthConfigError` for an incomplete configuration.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:309](../../../../../../libs/jane-kit/tests/test_auth.py#L309).

```python
auth = Authenticator.from_settings(s, transport=idp.transport())
```

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:327](../../../../../../libs/jane-kit/tests/test_auth.py#L327).

```python
auth = Authenticator.from_settings(as_list, transport=idp.transport())
```

## jane_kit.auth.Authenticator.describe

**Метод.** Код: [libs/jane-kit/src/jane_kit/auth.py:614](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L614).

```python
def describe(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
For the start log: mode, key names or the JWT issuer (never key values).
```

## jane_kit.auth.Authenticator.authenticate

**Метод.** Код: [libs/jane-kit/src/jane_kit/auth.py:623](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L623).

```python
async def authenticate(self, authorization: str | None) -> Principal:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `authorization` | `str \| None` | `—` | positional-or-keyword |

Результат: `Principal`.

Явні `raise` у тілі: `_unauthenticated`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Principal of an ``Authorization`` header value; 401 ``unauthenticated`` when it is not valid.
```

## jane_kit.auth.unmapped_routes

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:680](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L680).

```python
def unmapped_routes(app: FastAPI, table: ScopeTable, *, open_paths: Iterable[str]=OPEN_PATHS) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `app` | `FastAPI` | `—` | positional-or-keyword |
| `table` | `ScopeTable` | `—` | positional-or-keyword |
| `open_paths` | `Iterable[str]` | `OPEN_PATHS` | keyword-only |

Результат: `list[str]`.

### Опис із вихідного коду

```text
``"METHOD /path"`` of routes that the scope table (plus :data:`BUILTIN_SCOPES`) does not cover.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:519](../../../../../../libs/jane-kit/tests/test_auth.py#L519).

```python
assert unmapped_routes(partial, SCOPES) == ["GET /v1/jobs/{job_id}", "POST /v1/jobs/{job_id}/cancel"]
```

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:219](../../../../../../libs/jane-kit/tests/test_auth.py#L219).

```python
assert sorted(unmapped_routes(app, {"GET /v1/things": "storage:read"})) == [
        "GET /v1/open-to-any",
        "POST /v1/things",
    ]
```

## jane_kit.auth.authorize

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:712](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L712).

```python
async def authorize(request: Request) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `request` | `Request` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `Forbidden`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Application-wide dependency of ``create_app``: the scope of the matched operation from the service's
table (403 ``forbidden``). An operation missing from the table is denied (fail closed).
```

## jane_kit.auth.install_auth

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:734](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L734).

```python
def install_auth(app: FastAPI, settings: AuthSettings, *, scopes: ScopeTable | None=None, authenticator: Authenticator | None=None) -> Authenticator:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `app` | `FastAPI` | `—` | positional-or-keyword |
| `settings` | `AuthSettings` | `—` | positional-or-keyword |
| `scopes` | `ScopeTable \| None` | `None` | keyword-only |
| `authenticator` | `Authenticator \| None` | `None` | keyword-only |

Результат: `Authenticator`.

Явні `raise` у тілі: `AuthConfigError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Add authentication to ``app`` and remember its scope table; called by ``create_app``, which also
registers :func:`authorize` as an application-wide dependency.

Raises :class:`AuthConfigError` for an incomplete configuration. ``scopes=None`` leaves the scope checks
to the handlers (:func:`require`, :func:`principal_of`); with a table every route must be listed
(checked at start: :func:`check_scopes`).
```

## jane_kit.auth.check_scopes

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:763](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L763).

```python
def check_scopes(app: FastAPI) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `app` | `FastAPI` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `AuthConfigError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
At start: every route of ``app`` must be in its scope table (fail closed); logs the auth mode.
```

## jane_kit.auth.principal_of

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:780](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L780).

```python
def principal_of(request: Request) -> Principal:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `request` | `Request` | `—` | positional-or-keyword |

Результат: `Principal`.

Явні `raise` у тілі: `_unauthenticated`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
The caller authenticated by the middleware; 401 if there is none (authentication not installed).
```

## jane_kit.auth.require

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth.py:788](../../../../../../libs/jane-kit/src/jane_kit/auth.py#L788).

```python
def require(*any_of: str) -> Callable[[Request], Principal]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `any_of` | `str` | `—` | var-positional |

Результат: `Callable[[Request], Principal]`.

### Опис із вихідного коду

```text
FastAPI dependency: the caller must have one of ``any_of``; returns the :class:`Principal`.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:234](../../../../../../libs/jane-kit/tests/test_auth.py#L234).

```python
require("storage:write")
```
