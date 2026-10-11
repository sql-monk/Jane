# Модуль `jane_assistant.settings`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/settings.py](../../../../../services/assistant/src/jane_assistant/settings.py). Не редагуйте вручну.

Settings and limits of the assistant. Every limit has a safe default documented in README.md.

Limits follow ``contracts/schemas/common/limits.schema.json`` where the limit exists there (``llm.*``, ``transfer.*``, ``timeouts.*``, ``retries``). Assistant-specific knobs (confidence threshold, batch size, sample text size, match thresholds...) live in the ``onboarding`` and ``improvement`` groups; they are internal because the contract schema is strict.

Resolution order: model defaults &lt;- platform file (``JANE_ASSISTANT_LIMITS_FILE``) &lt;- ``JANE_ASSISTANT_LIMITS__*`` &lt;- request ``limits`` (``OnboardingRequest.limits`` etc., contract ``limits.llm``), with platform ``hard_caps`` applied last (``min``).

## Зміст

- [Клас `Settings`](#клас-settings)
- [Клас `Budget`](#клас-budget)
- [Клас `LlmLimits`](#клас-llmlimits)
- [Клас `OnboardingLimits`](#клас-onboardinglimits)
- [Клас `MaterialLimits`](#клас-materiallimits)
- [Клас `ImprovementLimits`](#клас-improvementlimits)
- [Клас `UnknownLimits`](#клас-unknownlimits)
- [Клас `TransferLimits`](#клас-transferlimits)
- [Клас `ContentLimits`](#клас-contentlimits)
- [Клас `SearchLimits`](#клас-searchlimits)
- [Клас `LlmCallLimits`](#клас-llmcalllimits)
- [Клас `StateLimits`](#клас-statelimits)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)
- [Функція `request_layer`](#функція-request_layer)

## Класи

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_assistant.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:38](../../../../../services/assistant/src/jane_assistant/settings.py#L38) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'assistant'` | читання й запис |  |
| `state_dsn` | `SecretStr \| None` | `None` | читання й запис | PostgreSQL DSN of the service's own state (sessions, jobs, idempotency keys) shared by instances. Unset: in-memory state - only for a single standalone instance and tests (lost on restart). |
| `state_schema` | `str` | `Field(default='jane_assistant', pattern='^[a-z_][a-z0-9_]{0,62}$')` | читання й запис | Schema of the state tables (created if missing). |
| `llm_url` | `str \| None` | `None` | читання й запис |  |
| `registry_url` | `str \| None` | `None` | читання й запис |  |
| `collector_web_url` | `str \| None` | `None` | читання й запис |  |
| `collector_telegram_url` | `str \| None` | `None` | читання й запис |  |
| `handler_runtime_url` | `str \| None` | `None` | читання й запис |  |
| `orchestrator_url` | `str \| None` | `None` | читання й запис |  |
| `storage_url` | `str \| None` | `None` | читання й запис |  |
| `service_token_ref` | `str \| None` | `None` | читання й запис | Token for every neighbour that has no reference of its own below. |
| `llm_token_ref` | `str \| None` | `None` | читання й запис |  |
| `registry_token_ref` | `str \| None` | `None` | читання й запис |  |
| `collector_web_token_ref` | `str \| None` | `None` | читання й запис |  |
| `collector_telegram_token_ref` | `str \| None` | `None` | читання й запис |  |
| `handler_runtime_token_ref` | `str \| None` | `None` | читання й запис |  |
| `orchestrator_token_ref` | `str \| None` | `None` | читання й запис |  |
| `storage_token_ref` | `str \| None` | `None` | читання й запис |  |
| `service_token_env` | `str \| None` | `None` | читання й запис | Deprecated: name of an environment variable with the token for all neighbours; use ``service_token_ref=env:<name>``. |
| `search_provider` | `Literal['none', 'static', 'http_json']` | `'none'` | читання й запис |  |
| `search_static_file` | `Path \| None` | `None` | читання й запис | ``static``: JSON file ``[{"title", "url"?, "telegram_username"?, "description"?, "aliases"?}]``. |
| `search_url_template` | `str \| None` | `None` | читання й запис | ``http_json``: URL with ``{query}``, e.g. an internal search gateway. |
| `search_items_path` | `str` | `'results'` | читання й запис |  |
| `search_title_field` | `str` | `'title'` | читання й запис |  |
| `search_url_field` | `str` | `'url'` | читання й запис |  |
| `search_description_field` | `str` | `'description'` | читання й запис |  |
| `blob_roots` | `list[Path]` | `Field(default_factory=list)` | читання й запис | Directories from which ``file://`` material content may be read (JSON list). Empty (default): ``file://`` content is refused - a request must not read arbitrary files of this container. |
| `download_host_allowlist` | `list[str]` | `Field(default_factory=list)` | читання й запис | ``hostname`` (any port) or ``hostname:port`` a material ``download_url`` may point to (JSON list). Empty (default): downloads are refused. Redirects are never followed. |
| `contracts_dir` | `Path \| None` | `None` | читання й запис | Where ``contracts/schemas`` live (local validation of generated rules and manifests). Empty -> found upwards from the package (dev checkout) or ``/app/contracts`` (Docker). |
| `default_storage_package` | `str \| None` | `None` | читання й запис | ``package_id@version`` of a storage package added to task drafts (optional). |
| `default_storage_connection` | `str \| None` | `None` | читання й запис | ``connection_id`` for that storage stage. |
| `llm_model_cheap` | `str` | `'cheap'` | читання й запис | Model alias of the LLM gateway for classification (sampling, unknown materials). |
| `llm_model_strong` | `str` | `'strong'` | читання й запис | Model alias for analysis, proposals and code generation. |
| `llm_completion_mode` | `Literal['sync', 'async']` | `'sync'` | читання й запис | How the assistant waits for a model call (``llm.v1`` ``CompletionRequest.mode``): ``sync`` - one HTTP request with its own timeout ``limits.llm_call.request_timeout_ms``; ``async`` - 202 + job of the gateway, polled every ``clients.job_poll_interval_ms`` within ``clients.job_wait_timeout_ms`` (no long connection). |
| `generated_code_allowed_modules` | `list[str]` | `Field(default_factory=lambda: ['re', 'html', 'json', 'math', 'datetime', 'decima` | читання й запис | Policy (not a limit): modules generated extractor code may import. The runtime sandbox (WP-06) is the real barrier; this list rejects obviously unsuitable code early. |
| `onboarding_allow_activation` | `bool` | `True` | читання й запис | Allow ``acceptProposal`` with ``activate: true`` to create the source and task in the orchestrator (only when every extractor passed its tests). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

### Клас `Budget`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:139](../../../../../services/assistant/src/jane_assistant/settings.py#L139) |

```python
class Budget(Limits): ...
```

Contract ``limits.llm.budget`` (``Budget``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `amount` | `float` | `Field(default=2.0, ge=0)` | читання й запис |  |
| `currency` | `str` | `Field(default='USD', pattern='^[A-Z]{3}$')` | читання й запис |  |
| `period` | `Literal['run', 'day', 'week', 'month', 'total']` | `'run'` | читання й запис |  |

### Клас `LlmLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:147](../../../../../services/assistant/src/jane_assistant/settings.py#L147) |

```python
class LlmLimits(Limits): ...
```

Contract ``limits.llm``. ``budget`` follows the contract's ``Budget`` semantics: with ``period: run`` it is the limit of one assistant run (onboarding session, improvement or unknown-material job) - every call sends it with ``scope.run_id`` and the gateway counts the run; ``amount: 0`` allows no LLM call. The assistant also stops by itself once its run spent ``budget.amount``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_requests_per_minute` | `int` | `Field(default=30, ge=1)` | читання й запис |  |
| `max_input_tokens_per_request` | `int` | `Field(default=16000, ge=1)` | читання й запис | Data sent to the model is fitted to this limit as the gateway counts it (``llm_call.chars_per_token``). |
| `max_output_tokens_per_request` | `int` | `Field(default=8000, ge=1)` | читання й запис | Room for the model's answer. Code generation answers with a module, a schema and expectations; 4000 cut such answers on real pages (the gateway then reports invalid output). Keep the answer within the gateway's provider timeout (about 130 tokens/s of a strong model: 8000 tokens ~ 1 min). |
| `budget` | `Budget` | `Budget()` | читання й запис |  |
| `max_improvement_attempts` | `int` | `Field(default=3, ge=0)` | читання й запис |  |
| `max_onboarding_samples` | `int` | `Field(default=60, ge=1)` | читання й запис |  |
| `min_onboarding_confidence` | `float` | `Field(default=0.8, gt=0, le=1)` | читання й запис | Contract ``llm.min_onboarding_confidence`` (WP-15): sampling stops once the sample-coverage confidence reaches it; below it within the budget the session is ``insufficient_sample``. Before WP-15 it was the internal ``onboarding.min_confidence``. |

### Клас `OnboardingLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:169](../../../../../services/assistant/src/jane_assistant/settings.py#L169) |

```python
class OnboardingLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `min_distinct_types` | `int` | `Field(default=2, ge=1)` | читання й запис | Do not trust coverage of a single material type while collection is still running. |
| `sample_batch_size` | `int` | `Field(default=10, ge=1)` | читання й запис | Materials classified per LLM request during adaptive sampling. |
| `max_sample_chars` | `int` | `Field(default=6000, ge=200)` | читання й запис | Text of one material passed to the classifying model. A larger HTML page is shown as a digest of that size (see ``material``); a batch shrinks it further to fit ``llm.max_input_tokens_per_request``. |
| `max_example_chars` | `int` | `Field(default=12000, ge=200)` | читання й запис | Text of one example material in analysis and extractor generation (a digest for larger HTML; shrunk to fit ``llm.max_input_tokens_per_request`` with the other parts of the request). |
| `min_examples_per_type` | `int` | `Field(default=2, ge=1)` | читання й запис | A material type counts as distinguished after this many examples. |
| `max_examples_per_type` | `int` | `Field(default=3, ge=1)` | читання й запис | Examples of one type sent to analysis and code generation. |
| `max_negative_examples` | `int` | `Field(default=1, ge=1)` | читання й запис | Materials of other types used as ``empty`` cases when testing/generating an extractor. |
| `poll_page_factor` | `int` | `Field(default=3, ge=1)` | читання й запис | Materials pulled per poll of the sampling collection = ``sample_batch_size x poll_page_factor`` (the surplus is the pool the diversity selection picks from). |
| `max_candidates` | `int` | `Field(default=5, ge=1)` | читання й запис | Search results kept for disambiguation. |
| `auto_select_confidence` | `float` | `Field(default=0.8, gt=0, le=1)` | читання й запис |  |
| `auto_select_margin` | `float` | `Field(default=0.2, ge=0, le=1)` | читання й запис |  |
| `max_candidate_packages` | `int` | `Field(default=5, ge=1)` | читання й запис | Existing extractors tested per entity type. |
| `bind_threshold` | `float` | `Field(default=0.9, ge=0, le=1)` | читання й запис | Share of samples an existing extractor must pass to be bound as is. |
| `fork_threshold` | `float` | `Field(default=0.5, ge=0, le=1)` | читання й запис | Share of samples above which an existing extractor is forked and adapted. |
| `max_generation_attempts` | `int` | `Field(default=2, ge=1)` | читання й запис | LLM attempts to produce a new extractor that passes its tests. |
| `max_proposals` | `int` | `Field(default=4, ge=1)` | читання й запис |  |
| `fetch_ratio` | `int` | `Field(default=3, ge=1)` | читання й запис | The sampling collection may fetch up to ``max_onboarding_samples x fetch_ratio`` materials (``limits.crawl.max_pages_per_run`` / ``telegram.max_messages_per_run`` of that collection); only the most diverse ones are classified. |
| `collection_poll_wait_ms` | `int` | `Field(default=1000, ge=0)` | читання й запис | Long-poll of ``listCollectionMaterials`` while sampling. |
| `max_empty_polls` | `int` | `Field(default=30, ge=1)` | читання й запис | Consecutive empty polls of a running collection before sampling gives up. |
| `requests_overhead_ratio` | `float` | `Field(default=0.05, ge=0)` | читання й запис | Added to estimated materials for the ``requests_per_run_estimate`` of a proposal. |
| `max_link_patterns` | `int` | `Field(default=20, ge=0)` | читання й запис | In-page link patterns (and pagination URL templates) of sampled pages kept as evidence for analysis and proposals, most frequent first. |
| `link_pattern_examples` | `int` | `Field(default=2, ge=0)` | читання й запис | Example links kept per link pattern. |
| `max_pages_listed` | `int` | `Field(default=20, ge=1)` | читання й запис | Page numbers listed per pagination template (the largest seen is always given). |
| `max_evidence_examples` | `int` | `Field(default=5, ge=1)` | читання й запис | Examples kept of other evidence (pages declaring another canonical) and of URL shapes in messages. |
| `max_risk_url_chars` | `int` | `Field(default=200, ge=20)` | читання й запис | A page URL quoted in a proposal risk is cut to this many characters. |

### Клас `MaterialLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:225](../../../../../services/assistant/src/jane_assistant/settings.py#L225) |

```python
class MaterialLimits(Limits): ...
```

How a large HTML material is shown to the model and kept as a test fixture (``material.py``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_fixture_bytes` | `int` | `Field(default=131072, ge=1024)` | читання й запис | HTML content above this size is reduced once it is read (executable scripts, styles, SVG and comments removed, then data scripts other than JSON-LD, then the end of the body): the reduced page is what the model sees, what extractors are tested on and what a package keeps as its test fixture, so generated packages stay within ``transfer.inline_max_bytes``. JSON-LD is kept whole while it fits. |
| `head_share` | `float` | `Field(default=0.1, ge=0, le=1)` | читання й запис | Share of a digest's characters for head tags (title, meta, canonical / next / prev links). |
| `structured_share` | `float` | `Field(default=0.6, ge=0, le=1)` | читання й запис | Share of a digest's characters for structured data (JSON-LD, microdata). |
| `text_share` | `float` | `Field(default=0.15, ge=0, le=1)` | читання й запис | Share of a digest's characters for the visible text; the start of the body markup gets the rest (and whatever the other parts do not use). |
| `max_list_items` | `int` | `Field(default=3, ge=1)` | читання й запис | Items kept from every long list of structured data in a digest (the count of the rest is stated). |
| `max_string_chars` | `int` | `Field(default=1000, ge=20)` | читання й запис | Longer strings of structured data are shortened in a digest (marked with the number of cut characters). |
| `short_string_chars` | `int` | `Field(default=200, ge=20)` | читання й запис | Strings of structured data when even its first list items do not fit the structured share: lists then keep one item and strings this many characters. |
| `max_head_tags` | `int` | `Field(default=60, ge=0)` | читання й запис | Head tags (title, informative meta, canonical / next / prev links) in a digest. |
| `max_microdata_types` | `int` | `Field(default=20, ge=0)` | читання й запис |  |
| `max_microdata_props` | `int` | `Field(default=30, ge=0)` | читання й запис | Microdata item types and property names (most frequent first, with counts) in a digest. |

### Клас `ImprovementLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:260](../../../../../services/assistant/src/jane_assistant/settings.py#L260) |

```python
class ImprovementLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_sample_chars` | `int` | `Field(default=6000, ge=200)` | читання й запис |  |
| `max_problem_samples` | `int` | `Field(default=10, ge=1)` | читання й запис |  |
| `max_successful_examples` | `int` | `Field(default=5, ge=0)` | читання й запис |  |
| `max_file_chars` | `int` | `Field(default=20000, ge=200)` | читання й запис | Package source file passed to the model (longer files are cut). |
| `max_proposal_bytes` | `int` | `Field(default=1048576, ge=1024)` | читання й запис | ``proposal_only``: size of the whole ``ImprovementResult.proposal`` as compact UTF-8 JSON (whenever its required part fits): code and schema files, then the diff (cut with a marker), then test fixtures; files that do not fit are named in ``omitted_files``. |

### Клас `UnknownLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:272](../../../../../services/assistant/src/jane_assistant/settings.py#L272) |

```python
class UnknownLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_sample_chars` | `int` | `Field(default=6000, ge=200)` | читання й запис |  |
| `min_confidence` | `float` | `Field(default=0.6, ge=0, le=1)` | читання й запис | Below this, the suggestion for an unknown material is ``none``. |

### Клас `TransferLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:278](../../../../../services/assistant/src/jane_assistant/settings.py#L278) |

```python
class TransferLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `inline_max_bytes` | `int` | `contract_field('transfer.inline_max_bytes', 262144, ge=0)` | читання й запис | Package archives up to this size are sent to the runtime inline (base64). |

### Клас `ContentLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:283](../../../../../services/assistant/src/jane_assistant/settings.py#L283) |

```python
class ContentLimits(Limits): ...
```

Reading material content (``ContentRef``) under ``blob_roots`` / ``download_host_allowlist``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_material_bytes` | `int` | `Field(default=16777216, ge=1)` | читання й запис | Largest material content read (inline, file or download); larger is ``limit_exceeded``. |
| `fetch_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | The whole ``download_url`` download, connection included. |
| `connect_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис | Establishing the connection of a ``download_url`` download. |

### Клас `SearchLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:294](../../../../../services/assistant/src/jane_assistant/settings.py#L294) |

```python
class SearchLimits(Limits): ...
```

Calls of the ``http_json`` search provider.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `request_timeout_ms` | `int` | `Field(default=10000, ge=1)` | читання й запис |  |
| `connect_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис |  |

### Клас `LlmCallLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:301](../../../../../services/assistant/src/jane_assistant/settings.py#L301) |

```python
class LlmCallLimits(Limits): ...
```

Calls of the LLM gateway (internal). Other neighbours use ``clients.*`` - the platform's general ``timeouts.*`` / ``retries``, sized for short service calls; one model call can take minutes.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `request_timeout_ms` | `int` | `Field(default=900000, ge=1)` | читання й запис | Timeout of one synchronous ``createCompletion``. It must cover the gateway's worst case: (schema retries + 1) x provider attempts x provider timeout + backoff - with the llm defaults 2 x 2 x 120 s = 8 min, with a platform profile's 3 attempts 12 min; 15 min is also the gateway's ``reservation_ttl_seconds`` (a call older than that is treated as crashed). Connection and retries come from ``clients.*``. |
| `chars_per_token` | `float` | `Field(default=2.0, gt=0)` | читання й запис | Characters per token used to fit data into ``llm.max_input_tokens_per_request``. Keep it no larger than the gateway's own estimate (``gateway.chars_per_token_estimate``, 2.0 by default), otherwise the gateway refuses a full request with ``limit_exceeded``. |
| `prompt_overhead_chars` | `int` | `Field(default=2000, ge=0)` | читання й запис | Characters reserved for the gateway's preamble around the instructions (the instructions are counted). |
| `part_overhead_chars` | `int` | `Field(default=150, ge=0)` | читання й запис | Characters reserved for the delimiters of every data part (its name and media type are counted). |

#### Метод `LlmCallLimits.client_limits`

```python
def client_limits(self, clients: ClientLimits) -> ClientLimits: ...
```

Код: [settings.py:320](../../../../../services/assistant/src/jane_assistant/settings.py#L320).

### Клас `StateLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:324](../../../../../services/assistant/src/jane_assistant/settings.py#L324) |

```python
class StateLimits(Limits): ...
```

Shared PostgreSQL state (``state_dsn``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `pool_max_size` | `int` | `Field(default=10, ge=1)` | читання й запис |  |
| `connect_timeout_ms` | `int` | `Field(default=10000, ge=1)` | читання й запис |  |
| `in_progress_lease_ms` | `int` | `Field(default=900000, ge=1)` | читання й запис | An in-progress idempotency claim of a crashed instance can be taken over after this. |
| `job_lease_ms` | `int` | `Field(default=60000, ge=1)` | читання й запис | A running job whose instance did not renew the lease for this long is marked ``failed``. |
| `heartbeat_interval_ms` | `int` | `Field(default=15000, ge=1)` | читання й запис | How often an instance renews the leases of its running jobs (keep well below job_lease_ms). |
| `session_retention_seconds` | `int` | `Field(default=2592000, ge=60)` | читання й запис | Onboarding sessions not updated for this long are deleted (default 30 days). |

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:339](../../../../../services/assistant/src/jane_assistant/settings.py#L339) |

```python
class ServiceLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `state` | `StateLimits` | `StateLimits()` | читання й запис |  |
| `llm` | `LlmLimits` | `contract_field('llm', LlmLimits())` | читання й запис |  |
| `transfer` | `TransferLimits` | `TransferLimits()` | читання й запис |  |
| `onboarding` | `OnboardingLimits` | `OnboardingLimits()` | читання й запис |  |
| `material` | `MaterialLimits` | `MaterialLimits()` | читання й запис |  |
| `improvement` | `ImprovementLimits` | `ImprovementLimits()` | читання й запис |  |
| `unknown` | `UnknownLimits` | `UnknownLimits()` | читання й запис |  |
| `content` | `ContentLimits` | `ContentLimits()` | читання й запис |  |
| `search` | `SearchLimits` | `SearchLimits()` | читання й запис |  |
| `clients` | `ClientLimits` | `ClientLimits()` | читання й запис | Calls of the neighbours: contract ``timeouts.connect_timeout_ms`` / ``request_timeout_ms`` and ``retries`` (a platform profile sets them); the LLM gateway's request timeout is ``llm_call`` instead. |
| `llm_call` | `LlmCallLimits` | `LlmCallLimits()` | читання й запис |  |
| `pages` | `PageLimits` | `PageLimits()` | читання й запис | Cursor pages of ``listOnboardingSessions`` / ``listImprovementRuns``: default and largest ``limit``. |
| `jobs` | `JobLimits` | `JobLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |

## Функції

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- platform file (``..._LIMITS_FILE``) &lt;- ``JANE_ASSISTANT_LIMITS__*`` &lt;- ``extra``.

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits the assistant does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail.

Код: [settings.py:359](../../../../../services/assistant/src/jane_assistant/settings.py#L359).

### Функція `request_layer`

```python
def request_layer(llm_limits: dict[str, Any] | None) -> list[LimitLayer]: ...
```

Contract ``limits.llm`` from a request as a ``request`` layer (empty list if absent).

Код: [settings.py:367](../../../../../services/assistant/src/jane_assistant/settings.py#L367).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_ASSISTANT_'` |  |
