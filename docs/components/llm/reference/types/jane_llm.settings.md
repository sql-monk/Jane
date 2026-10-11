# Модуль `jane_llm.settings`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/settings.py](../../../../../services/llm/src/jane_llm/settings.py). Не редагуйте вручну.

Settings and limits of the LLM service. Every limit has a safe default documented in README.md.

## Зміст

- [Клас `Settings`](#клас-settings)
- [Клас `LlmBudget`](#клас-llmbudget)
- [Клас `LlmLimits`](#клас-llmlimits)
- [Клас `GatewayLimits`](#клас-gatewaylimits)
- [Клас `RegistryLimits`](#клас-registrylimits)
- [Клас `ProviderLimits`](#клас-providerlimits)
- [Клас `FakeProviderLimits`](#клас-fakeproviderlimits)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)

## Класи

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_llm.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:22](../../../../../services/llm/src/jane_llm/settings.py#L22) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'llm'` | читання й запис |  |
| `port` | `int` | `8110` | читання й запис |  |
| `store` | `Literal['postgres', 'memory']` | `'postgres'` | читання й запис | Where budgets, usage, providers, connections, idempotency keys and jobs live. ``postgres`` (default) is shared between instances; ``memory`` is for tests and single-process demos. |
| `database_url` | `str \| None` | `None` | читання й запис | PostgreSQL DSN (``postgresql://user:pass@host:5432/db``); required for ``store=postgres``. Give the password through the environment (for example ``PGPASSWORD``), not in files. |
| `db_schema` | `str` | `Field(default='llm', pattern='^[a-z_][a-z0-9_]{0,62}$')` | читання й запис | Own schema of the service in the database (the service never reads other services' tables). |
| `seed_file` | `Path \| None` | `None` | читання й запис | YAML/JSON with providers, model aliases, connections and budgets applied at startup (only entries that do not exist yet are created). See ``config/seed.example.yaml``. |
| `fake_provider_enabled` | `bool` | `True` | читання й запис | Register the deterministic ``fake`` provider and the ``default`` alias pointing to it. |
| `packages_dir` | `Path \| None` | `None` | читання й запис | Directory with unpacked LLM packages (``<dir>/<package_id>/jane-package.json``) usable without a registry. The built-in ``services/llm/packages`` is used when unset and present. |
| `registry_url` | `str \| None` | `None` | читання й запис | Base URL of the handler registry (``registry.v1``) for packages referenced by ``handler``. |
| `registry_token` | `SecretStr \| None` | `None` | читання й запис | The gateway's own bearer token for the registry (ADR-0005 §5; give it through the environment, never logged). |
| `db_pool_min_size` | `int` | `Field(default=1, ge=0)` | читання й запис | Minimum PostgreSQL connections per instance. |
| `db_pool_max_size` | `int` | `Field(default=10, ge=1)` | читання й запис | Maximum PostgreSQL connections per instance (size it with ``jobs.max_concurrent_jobs`` and traffic). |
| `secret_env_prefix` | `str` | `'JANE_SECRET_'` | читання й запис | ``env:`` secret references may only name variables with this prefix. |
| `secret_files_dir` | `Path \| None` | `Path('/run/secrets')` | читання й запис | ``file:`` secret references may only point inside this directory (unset: ``file:`` disabled). |
| `provider_api_base_allowlist` | `list[str]` | `Field(default_factory=lambda: ['https://api.anthropic.com'])` | читання й запис | Origins a connection's ``params.api_base`` may point to (JSON list in the environment). |
| `blob_roots` | `list[Path]` | `Field(default_factory=list)` | читання й запис | Directories from which ``file://`` content (materials, entities/data refs, package archives) may be read (JSON list). Empty (default): ``file://`` content is refused - a request must not read arbitrary files. |
| `download_host_allowlist` | `list[str]` | `Field(default_factory=list)` | читання й запис | ``hostname`` (any port) or ``hostname:port`` a ContentRef ``download_url`` may point to (JSON list). Empty (default): downloads are refused. Redirects are never followed. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

#### Метод `Settings.connection_policy`

```python
def connection_policy(self) -> ConnectionPolicy: ...
```

Код: [settings.py:73](../../../../../services/llm/src/jane_llm/settings.py#L73).

#### Метод `Settings.content_reader`

```python
def content_reader(self, limits: GatewayLimits) -> ContentReader: ...
```

Reader of request ContentRefs under ``blob_roots`` / ``download_host_allowlist`` and the gateway limits (``content_fetch_timeout_ms``; sizes are given per read).

Код: [settings.py:80](../../../../../services/llm/src/jane_llm/settings.py#L80).

### Клас `LlmBudget`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:91](../../../../../services/llm/src/jane_llm/settings.py#L91) |

```python
class LlmBudget(Limits): ...
```

Contract ``limits.llm.budget`` (``Budget``): the platform budget when no stored definition exists.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `amount` | `float` | `Field(default=10.0, ge=0)` | читання й запис |  |
| `currency` | `str` | `Field(default='USD', pattern='^[A-Z]{3}$')` | читання й запис |  |
| `period` | `Literal['run', 'day', 'week', 'month', 'total']` | `'day'` | читання й запис |  |

### Клас `LlmLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:99](../../../../../services/llm/src/jane_llm/settings.py#L99) |

```python
class LlmLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_requests_per_minute` | `int` | `contract_field('llm.max_requests_per_minute', 60, ge=1)` | читання й запис | Platform-wide provider calls per minute (all instances together). |
| `max_input_tokens_per_request` | `int` | `contract_field('llm.max_input_tokens_per_request', 100000, ge=1)` | читання й запис |  |
| `max_output_tokens_per_request` | `int` | `contract_field('llm.max_output_tokens_per_request', 4096, ge=1)` | читання й запис |  |
| `budget` | `LlmBudget` | `contract_field('llm.budget', LlmBudget())` | читання й запис |  |

### Клас `GatewayLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:107](../../../../../services/llm/src/jane_llm/settings.py#L107) |

```python
class GatewayLimits(Limits): ...
```

Service-specific knobs (not in ``limits.schema.json``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `default_max_output_tokens` | `int` | `Field(default=1024, ge=1)` | читання й запис | Used when neither the request nor the package gives ``max_output_tokens``. |
| `max_schema_retries` | `int` | `Field(default=1, ge=0)` | читання й запис | Default and upper bound of ``max_schema_retries`` (extra calls on output invalid for the schema). |
| `chars_per_token_estimate` | `float` | `Field(default=2.0, gt=0)` | читання й запис | Conservative input-token estimate (characters per token) used to reserve budget before a call. |
| `reservation_ttl_seconds` | `int` | `Field(default=900, ge=1)` | читання й запис | A reservation older than this (instance crashed mid-call) is charged at its estimate. |
| `max_data_part_bytes` | `int` | `Field(default=2000000, ge=1)` | читання й запис | Largest single data part (material content) accepted from inline or blob content. |
| `content_fetch_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | Timeout of downloading blob content (``download_url``) of materials and package archives (the whole download, connection included). |
| `max_package_bytes` | `int` | `Field(default=20000000, ge=1)` | читання й запис | Largest package archive (compressed, and total uncompressed size) from a request or the registry. |
| `max_package_files` | `int` | `Field(default=1000, ge=1)` | читання й запис | Most files in a package archive. |

### Клас `RegistryLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:129](../../../../../services/llm/src/jane_llm/settings.py#L129) |

```python
class RegistryLimits(Limits): ...
```

Calls to the handler registry (internal; the contract fields are used by ``provider``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connect_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис |  |
| `request_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис |  |
| `max_attempts` | `int` | `Field(default=3, ge=1)` | читання й запис |  |

#### Метод `RegistryLimits.client_limits`

```python
def client_limits(self) -> ClientLimits: ...
```

Код: [settings.py:136](../../../../../services/llm/src/jane_llm/settings.py#L136).

### Клас `ProviderLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:144](../../../../../services/llm/src/jane_llm/settings.py#L144) |

```python
class ProviderLimits(Limits): ...
```

Calls of LLM providers (``providers/anthropic.py``).

Connection establishment and the retry policy are the platform's general HTTP limits (contract ``timeouts.connect_timeout_ms``, ``retries``: a platform profile sets them). The time of one model call is the gateway's own limit: a generation of ``max_output_tokens_per_request`` takes minutes, while the contract's ``timeouts.request_timeout_ms`` is sized for web fetches and service calls (30 s in the profiles).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connect_timeout_ms` | `int` | `contract_field('timeouts.connect_timeout_ms', 5000, ge=1)` | читання й запис |  |
| `request_timeout_ms` | `int` | `Field(default=120000, ge=1)` | читання й запис | One provider HTTP call (waiting for the whole generation); not the contract's ``timeouts.request_timeout_ms``. |
| `retries` | `RetryPolicy` | `contract_field('retries', RetryPolicy(max_attempts=2, initial_backoff_ms=500))` | читання й запис |  |

### Клас `FakeProviderLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:158](../../../../../services/llm/src/jane_llm/settings.py#L158) |

```python
class FakeProviderLimits(Limits): ...
```

The deterministic test provider ``fake`` (internal, not in ``limits.schema.json``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_delay_ms` | `int` | `Field(default=30000, ge=0)` | читання й запис | Upper bound of the delay a ``fake`` connection asks for (``params.delay_ms``, ``params.responses[].delay_ms``); a longer delay is shortened to it, ``0`` turns delays off. |

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:166](../../../../../services/llm/src/jane_llm/settings.py#L166) |

```python
class ServiceLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `llm` | `LlmLimits` | `LlmLimits()` | читання й запис |  |
| `gateway` | `GatewayLimits` | `GatewayLimits()` | читання й запис |  |
| `fake` | `FakeProviderLimits` | `FakeProviderLimits()` | читання й запис |  |
| `provider` | `ProviderLimits` | `ProviderLimits()` | читання й запис | Calls to LLM providers: own ``request_timeout_ms``; contract ``timeouts.connect_timeout_ms`` and ``retries``. |
| `registry` | `RegistryLimits` | `RegistryLimits()` | читання й запис |  |
| `jobs` | `JobLimits` | `JobLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |
| `state` | `LeaseLimits` | `LeaseLimits()` | читання й запис | Leases of the shared PostgreSQL state (R17): ``Idempotency-Key`` claims, jobs, heartbeat interval. |

## Функції

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- platform file (``JANE_LLM_LIMITS_FILE``) &lt;- ``JANE_LLM_LIMITS__*`` &lt;- ``extra`` (request layer in autonomous mode).

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits this service does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail. Its ``timeouts.connect_timeout_ms`` and ``retries`` reach ``provider``; ``timeouts.request_timeout_ms`` does not (the model call timeout is ``provider.request_timeout_ms``, ``JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS``).

Код: [settings.py:179](../../../../../services/llm/src/jane_llm/settings.py#L179).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_LLM_'` |  |
