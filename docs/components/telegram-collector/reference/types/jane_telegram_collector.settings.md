# Модуль `jane_telegram_collector.settings`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/settings.py](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py). Не редагуйте вручну.

Settings and limits of the Telegram Collector. Every limit has a safe default documented in README.md.

Limit levels (``contracts/schemas/common/limits.schema.json``): service defaults -> platform (limits file, then ``JANE_TELEGRAM_COLLECTOR_LIMITS__*``) -> source (``rules.limits``) -> request (``CollectionRequest.limits`` or ``FetchRequest.limits``). ``hard_caps`` bound the result.

The layers are jane-kit's, with the same error checks as every other service (R20): the limits file is a shared ``PlatformLimits`` profile (contract groups the collector does not use - ``crawl``, ``sandbox``, ``llm``...
- are ignored and listed in ``ResolvedLimits.ignored``, a path unknown to the contract and to the model is an error); the environment layer takes model paths (``..._LIMITS__COLLECTOR__HISTORY_PAGE_SIZE``); source and request layers are contract-shaped ``Limits`` documents applied the same way as the profile (:func:`contract_layer`).

## Зміст

- [Клас `Settings`](#клас-settings)
- [Клас `Rate`](#клас-rate)
- [Клас `Timeouts`](#клас-timeouts)
- [Клас `Retries`](#клас-retries)
- [Клас `Queue`](#клас-queue)
- [Клас `Transfer`](#клас-transfer)
- [Клас `Telegram`](#клас-telegram)
- [Клас `Collector`](#клас-collector)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Функція `contract_layer`](#функція-contract_layer)
- [Функція `to_contract`](#функція-to_contract)
- [Функція `platform_layers`](#функція-platform_layers)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)

## Класи

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:45](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L45) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'telegram-collector'` | читання й запис |  |
| `port` | `int` | `8102` | читання й запис |  |
| `state_dir` | `Path` | `Path('.jane/telegram-collector')` | читання й запис | Own state store (SQLite ``state.db``): runs, channel cursors, seen revisions, buffer, jobs. |
| `client_backend` | `str` | `'recorded'` | читання й запис | Telegram client: ``recorded`` (JSON recordings, tests/demos), ``telethon`` (optional extra) or ``<module>:<factory>`` returning a :class:`~jane_telegram_collector.client.ClientFactory`. |
| `recordings_dir` | `Path \| None` | `None` | читання й запис | ``recorded`` backend: directory with ``<username or channel_id>.json`` recordings. |
| `default_account_connection_id` | `str \| None` | `None` | читання й запис | Connection (``kind=telegram_account``) used when rules name none (e.g. ``/v1/fetches`` without rules). |
| `transit_dir` | `Path \| None` | `None` | читання й запис | Transit blob store for large content and media (``file://`` ContentRef). Unset: inline only. |
| `rules_dir` | `Path \| None` | `None` | читання й запис | Local collector-rules packages for ``rules_ref`` without a registry (``<package_id>/<version>/``). |
| `registry_url` | `str \| None` | `None` | читання й запис | registry.v1 base URL for ``rules_ref``; checked after ``rules_dir``. |
| `registry_token_env` | `str \| None` | `None` | читання й запис | Name of the environment variable holding the bearer token for the registry (never the value). |
| `contracts_dir` | `Path \| None` | `None` | читання й запис | ``contracts/`` with the JSON Schemas; default: ``JANE_CONTRACTS_DIR`` or the checkout's contracts. |
| `secret_env_prefix` | `str` | `'JANE_SECRET_'` | читання й запис | ``env:`` secret references may name only variables with this prefix. |
| `secret_files_dir` | `Path \| None` | `Path('/run/secrets')` | читання й запис | ``file:`` secret references must point inside this directory (unset: ``file:`` disabled). |
| `telegram_host_allowlist` | `list[str]` | `Field(default_factory=list)` | читання й запис | Hosts allowed in host-like connection params (``server``, ``proxy_host``...); default: none. |
| `lease_seconds` | `int` | `Field(default=30, ge=2)` | читання й запис | A running collection is owned by one instance; after this long without a heartbeat another takes it. |
| `heartbeat_interval_ms` | `int` | `Field(default=5000, ge=50)` | читання й запис | How often the owner renews the lease and checks for cancellation requested through other instances. |
| `state_busy_timeout_ms` | `int` | `Field(default=10000, ge=1)` | читання й запис | How long a write waits for another process holding the SQLite lock. |
| `idempotency_lease_ms` | `int` | `Field(default=900000, ge=1000)` | читання й запис | An ``Idempotency-Key`` claim of a killed instance (not renewed for this long) can be claimed again; a live instance renews its claims in the resume loop (R17). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

#### Метод `Settings.connection_policy`

```python
def connection_policy(self) -> ConnectionPolicy: ...
```

Код: [settings.py:86](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L86).

### Клас `Rate`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:107](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L107) |

```python
class Rate(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `min_delay_ms_per_host` | `int` | `Field(default=200, ge=0)` | читання й запис | Minimum interval between two Telegram API calls of one run (the API is the only "host"). |

### Клас `Timeouts`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:112](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L112) |

```python
class Timeouts(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connect_timeout_ms` | `int` | `Field(default=15000, ge=1)` | читання й запис | Opening the Telegram client (connect + authorization check). |
| `request_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | One Telegram API call (history page, difference, message, media download). |

### Клас `Retries`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:119](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L119) |

```python
class Retries(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_attempts` | `int` | `Field(default=3, ge=1)` | читання й запис |  |
| `initial_backoff_ms` | `int` | `Field(default=1000, ge=0)` | читання й запис |  |
| `max_backoff_ms` | `int` | `Field(default=60000, ge=0)` | читання й запис |  |
| `backoff_multiplier` | `float` | `Field(default=2.0, ge=1)` | читання й запис |  |
| `jitter` | `bool` | `True` | читання й запис |  |

### Клас `Queue`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:127](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L127) |

```python
class Queue(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_unacked_materials` | `int` | `Field(default=500, ge=1)` | читання й запис |  |

### Клас `Transfer`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:131](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L131) |

```python
class Transfer(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `inline_max_bytes` | `int` | `Field(default=262144, ge=0)` | читання й запис |  |
| `transit_ttl_seconds` | `int` | `Field(default=604800, ge=60)` | читання й запис |  |

### Клас `Telegram`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:136](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L136) |

```python
class Telegram(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_messages_per_run` | `int` | `Field(default=10000, ge=1)` | читання й запис |  |
| `max_media_bytes` | `int` | `Field(default=20 * 1024 ** 2, ge=0)` | читання й запис |  |
| `max_flood_wait_seconds` | `int` | `Field(default=300, ge=0)` | читання й запис |  |

### Клас `Collector`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:142](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L142) |

```python
class Collector(Limits): ...
```

Service-specific limits (not in the contract; visible in the start-up log).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `history_page_size` | `int` | `Field(default=100, ge=1)` | читання й запис | Messages per history request (Telegram returns at most 100). |
| `changes_page_size` | `int` | `Field(default=100, ge=1)` | читання й запис | Updates per ``getChannelDifference`` request. |
| `max_wait_ms` | `int` | `Field(default=30000, ge=0)` | читання й запис | Upper bound of ``wait_ms`` long-poll on ``/materials``. |
| `long_poll_interval_ms` | `int` | `Field(default=100, ge=10)` | читання й запис | ``/materials?wait_ms=``: how often new materials are looked for while waiting. |
| `backpressure_poll_ms` | `int` | `Field(default=1000, ge=10)` | читання й запис | While paused by backpressure: how often the buffer is re-checked (acks may arrive via another instance). |
| `gc_interval_seconds` | `int` | `Field(default=3600, ge=1)` | читання й запис | How often expired collections and transit files are cleaned up. |

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:159](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L159) |

```python
class ServiceLimits(Limits): ...
```

Limits of the Telegram Collector; group and field names follow ``limits.schema.json``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `rate` | `Rate` | `contract_field('rate', Rate())` | читання й запис |  |
| `timeouts` | `Timeouts` | `contract_field('timeouts', Timeouts())` | читання й запис |  |
| `retries` | `Retries` | `contract_field('retries', Retries())` | читання й запис |  |
| `queue` | `Queue` | `contract_field('queue', Queue())` | читання й запис |  |
| `transfer` | `Transfer` | `contract_field('transfer', Transfer())` | читання й запис |  |
| `telegram` | `Telegram` | `contract_field('telegram', Telegram())` | читання й запис |  |
| `jobs` | `JobLimits` | `JobLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |
| `page` | `PageLimits` | `PageLimits()` | читання й запис |  |
| `collector` | `Collector` | `Collector()` | читання й запис |  |

## Функції

### Функція `contract_layer`

```python
def contract_layer(layer: LimitLayer) -> LimitLayer: ...
```

A contract-shaped ``Limits`` document (``rules.limits``, request ``limits``) as a jane-kit layer: contract paths go to the fields that declare them (``transfer.job_retention_seconds`` -> ``jobs.job_retention_seconds``), contract limits the collector does not have are ignored, anything else is a :class:`~jane_kit.config.LimitError` - exactly as for the platform profile.

Код: [settings.py:183](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L183).

### Функція `to_contract`

```python
def to_contract(limits: ServiceLimits) -> dict[str, Any]: ...
```

Model -> contract ``Limits`` document (only fields that exist in the contract), by jane-kit's mapping.

Код: [settings.py:191](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L191).

### Функція `platform_layers`

```python
def platform_layers(settings: Settings) -> list[LimitLayer]: ...
```

jane-kit's platform layers: the ``PlatformLimits`` file (shared profile) and the env overrides.

Код: [settings.py:199](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L199).

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- platform file (``..._LIMITS_FILE``) &lt;- ``JANE_TELEGRAM_COLLECTOR_LIMITS__*`` &lt;- ``extra`` (source/request layers, contract-shaped). Invalid limits raise :class:`~jane_kit.config.LimitError`.

Код: [settings.py:204](../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L204).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_TELEGRAM_COLLECTOR_'` |  |
| `LIMITS_ENV_PREFIX` | — | `f'{ENV_PREFIX}LIMITS__'` |  |
| `log` | — | `logging.getLogger(__name__)` |  |
