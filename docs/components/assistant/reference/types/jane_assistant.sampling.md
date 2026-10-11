# Модуль `jane_assistant.sampling`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/sampling.py](../../../../../services/assistant/src/jane_assistant/sampling.py). Не редагуйте вручну.

Adaptive sampling of a source (ТЗ §8: no fixed sample size; stop at sufficient confidence or report an insufficient sample within the budget).

The collector runs an ordinary, bounded collection: the strategies of the user's ``crawl_hints`` when given (they bound discovery to what the user asked for), otherwise sitemap + feeds + recursion from the entry point for the web and history for Telegram; ``limits.crawl.max_pages_per_run`` is ``max_onboarding_samples x fetch_ratio`` (or the user's smaller ``crawl_hints.limits.crawl`` value). The sampling collection does not treat ``rel=canonical`` as a duplicate signal (unless the hints set ``dedup``): the assistant observes pages as served and decides about canonical dedup for the proposals itself.

Materials are pulled in pages; each round the assistant picks the least represented URL shapes (diversity), classifies them with the cheap model and recomputes the confidence:

    coverage   = 1 - (materials of types seen fewer than min_examples_per_type times) / n
    confidence = (1 - estimated unseen-type share) x mean model confidence

``coverage`` is the Good-Turing sample-coverage estimate (with ``min_examples_per_type = 2`` it is exactly ``1 - singletons / n``): the probability that the next material belongs to a type already seen often enough. This estimate cannot detect a type that occurs later in a source ordered by URL or discovery strategy. After the first classification batch, the sampler probes the remaining bounded collector stream, classifies newly seen URL shapes, then samples more within known shapes if confidence is still low. Unclassified materials count toward a finite-population estimate of unseen types even when their URL shape is already known; this estimate also accounts for the observed rare types.

The population is the bounded stream. An unfinished stream cannot establish diversity: when the sample budget is reached with enough confidence before the stream ends, the rest of the stream is still read (without classification) - a URL shape that appears there and is not represented, or a stream that does not finish within the poll limits, makes the sample insufficient. A stream the collector stopped at its page budget (``fetched >= max_pages_per_run``: the crawl space is larger, as on every real shop with filter links) is a finished stream; the sample is then sufficient *for those pages* and its message says so.

Large HTML pages are reduced and shown to the model as digests (:mod:`jane_assistant.material`). Evidence for proposals is gathered from the full pages: declared ``rel=canonical``, in-page link patterns and pagination-like URL templates.

## Зміст

- [Клас `Evidence`](#клас-evidence)
- [Клас `Sample`](#клас-sample)
- [Клас `SampleResult`](#клас-sampleresult)
- [Функція `coverage`](#функція-coverage)
- [Функція `sample_source`](#функція-sample_source)
- [Функція `sampling_rules`](#функція-sampling_rules)

## Класи

### Клас `Evidence`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.sampling` |
| Код | [sampling.py:113](../../../../../services/assistant/src/jane_assistant/sampling.py#L113) |

```python
@dataclass
class Evidence: ...
```

What sampled pages say about discovery: canonical declarations, link patterns, pagination.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `hosts` | `list[str]` | — | читання й запис |  |
| `limits` | `OnboardingLimits` | — | читання й запис |  |
| `shas` | `dict[str, str]` | `field(default_factory=dict)` | читання й запис |  |
| `canonicals` | `list[tuple[str, str]]` | `field(default_factory=list)` | читання й запис |  |
| `patterns` | `Counter[str]` | `field(default_factory=Counter)` | читання й запис |  |
| `examples` | `dict[str, list[str]]` | `field(default_factory=dict)` | читання й запис |  |
| `pagination` | `dict[str, dict[str, Any]]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Evidence.observe`

```python
def observe(self, material: dict[str, Any], raw: bytes, text: str) -> None: ...
```

Код: [sampling.py:124](../../../../../services/assistant/src/jane_assistant/sampling.py#L124).

#### Метод `Evidence.canonical_wire`

```python
def canonical_wire(self) -> dict[str, Any]: ...
```

Код: [sampling.py:145](../../../../../services/assistant/src/jane_assistant/sampling.py#L145).

#### Метод `Evidence.wire`

```python
def wire(self) -> dict[str, Any]: ...
```

Код: [sampling.py:161](../../../../../services/assistant/src/jane_assistant/sampling.py#L161).

### Клас `Sample`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.sampling` |
| Код | [sampling.py:71](../../../../../services/assistant/src/jane_assistant/sampling.py#L71) |

```python
@dataclass
class Sample: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `material` | `dict[str, Any]` | — | читання й запис |  |
| `text` | `str` | — | читання й запис |  |
| `shape` | `str` | — | читання й запис |  |
| `material_type` | `str` | `'other'` | читання й запис |  |
| `confidence` | `float` | `0.0` | читання й запис |  |
| `reduced_from_bytes` | `int \| None` | `None` | читання й запис | Size of the page as served when ``material`` holds its reduced copy (``material.max_fixture_bytes``). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `SampleResult`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.sampling` |
| Код | [sampling.py:82](../../../../../services/assistant/src/jane_assistant/sampling.py#L82) |

```python
@dataclass
class SampleResult: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `samples` | `list[Sample]` | — | читання й запис |  |
| `confidence` | `float` | — | читання й запис |  |
| `sufficient` | `bool` | — | читання й запис |  |
| `message` | `str \| None` | — | читання й запис |  |
| `hints` | `dict[str, Any]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `SampleResult.counts`

```python
def counts(self) -> Counter[str]: ...
```

Код: [sampling.py:89](../../../../../services/assistant/src/jane_assistant/sampling.py#L89).

#### Метод `SampleResult.of_type`

```python
def of_type(self, material_type: str) -> list[Sample]: ...
```

Код: [sampling.py:92](../../../../../services/assistant/src/jane_assistant/sampling.py#L92).

#### Метод `SampleResult.wire`

```python
def wire(self) -> dict[str, Any]: ...
```

Код: [sampling.py:95](../../../../../services/assistant/src/jane_assistant/sampling.py#L95).

## Функції

### Функція `coverage`

```python
def coverage(counts: Counter[str], min_examples: int) -> float: ...
```

Код: [sampling.py:202](../../../../../services/assistant/src/jane_assistant/sampling.py#L202).

### Функція `sample_source`

```python
async def sample_source(
    *,
    collector: CollectorClient,
    llm: LlmSession,
    limits: ServiceLimits,
    job_key: str,
    source_id: str,
    source_kind: str,
    rules: dict[str, Any],
    model: str,
    progress: Progress,
    crawl_limits: dict[str, Any] | None = None,
) -> SampleResult: ...
```

``crawl_limits``: the user's ``crawl_hints.limits.crawl`` (validated by the caller); its ``max_pages_per_run`` can only lower the sampling bound.

Код: [sampling.py:322](../../../../../services/assistant/src/jane_assistant/sampling.py#L322).

### Функція `sampling_rules`

```python
def sampling_rules(
    source_kind: str,
    url: str | None,
    telegram_username: str | None,
    allowed: list[str],
    hints: dict[str, Any] | None,
) -> dict[str, Any]: ...
```

Код: [sampling.py:252](../../../../../services/assistant/src/jane_assistant/sampling.py#L252).
