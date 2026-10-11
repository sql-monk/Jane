# jane_assistant.sampling

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.sampling.Sample](#jane_assistantsamplingsample)
- [jane_assistant.sampling.Sample.__init__](#jane_assistantsamplingsample__init__)
- [jane_assistant.sampling.Sample.material](#jane_assistantsamplingsamplematerial)
- [jane_assistant.sampling.Sample.text](#jane_assistantsamplingsampletext)
- [jane_assistant.sampling.Sample.shape](#jane_assistantsamplingsampleshape)
- [jane_assistant.sampling.Sample.material_type](#jane_assistantsamplingsamplematerial_type)
- [jane_assistant.sampling.Sample.confidence](#jane_assistantsamplingsampleconfidence)
- [jane_assistant.sampling.Sample.reduced_from_bytes](#jane_assistantsamplingsamplereduced_from_bytes)
- [jane_assistant.sampling.SampleResult](#jane_assistantsamplingsampleresult)
- [jane_assistant.sampling.SampleResult.__init__](#jane_assistantsamplingsampleresult__init__)
- [jane_assistant.sampling.SampleResult.samples](#jane_assistantsamplingsampleresultsamples)
- [jane_assistant.sampling.SampleResult.confidence](#jane_assistantsamplingsampleresultconfidence)
- [jane_assistant.sampling.SampleResult.sufficient](#jane_assistantsamplingsampleresultsufficient)
- [jane_assistant.sampling.SampleResult.message](#jane_assistantsamplingsampleresultmessage)
- [jane_assistant.sampling.SampleResult.hints](#jane_assistantsamplingsampleresulthints)
- [jane_assistant.sampling.SampleResult.counts](#jane_assistantsamplingsampleresultcounts)
- [jane_assistant.sampling.SampleResult.of_type](#jane_assistantsamplingsampleresultof_type)
- [jane_assistant.sampling.SampleResult.wire](#jane_assistantsamplingsampleresultwire)
- [jane_assistant.sampling.Evidence](#jane_assistantsamplingevidence)
- [jane_assistant.sampling.Evidence.__init__](#jane_assistantsamplingevidence__init__)
- [jane_assistant.sampling.Evidence.hosts](#jane_assistantsamplingevidencehosts)
- [jane_assistant.sampling.Evidence.limits](#jane_assistantsamplingevidencelimits)
- [jane_assistant.sampling.Evidence.shas](#jane_assistantsamplingevidenceshas)
- [jane_assistant.sampling.Evidence.canonicals](#jane_assistantsamplingevidencecanonicals)
- [jane_assistant.sampling.Evidence.patterns](#jane_assistantsamplingevidencepatterns)
- [jane_assistant.sampling.Evidence.examples](#jane_assistantsamplingevidenceexamples)
- [jane_assistant.sampling.Evidence.pagination](#jane_assistantsamplingevidencepagination)
- [jane_assistant.sampling.Evidence.observe](#jane_assistantsamplingevidenceobserve)
- [jane_assistant.sampling.Evidence.canonical_wire](#jane_assistantsamplingevidencecanonical_wire)
- [jane_assistant.sampling.Evidence.wire](#jane_assistantsamplingevidencewire)
- [jane_assistant.sampling.coverage](#jane_assistantsamplingcoverage)
- [jane_assistant.sampling.sampling_rules](#jane_assistantsamplingsampling_rules)
- [jane_assistant.sampling.sample_source](#jane_assistantsamplingsample_source)

## jane_assistant.sampling.Sample

**Клас.** Код: [services/assistant/src/jane_assistant/sampling.py:71](../../../../../../services/assistant/src/jane_assistant/sampling.py#L71).

```python
class Sample:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [material](jane_assistant.sampling.md#jane_assistantsamplingsamplematerial) | Поле | ні |
| [text](jane_assistant.sampling.md#jane_assistantsamplingsampletext) | Поле | ні |
| [shape](jane_assistant.sampling.md#jane_assistantsamplingsampleshape) | Поле | ні |
| [material_type](jane_assistant.sampling.md#jane_assistantsamplingsamplematerial_type) | Поле | ні |
| [confidence](jane_assistant.sampling.md#jane_assistantsamplingsampleconfidence) | Поле | ні |
| [reduced_from_bytes](jane_assistant.sampling.md#jane_assistantsamplingsamplereduced_from_bytes) | Поле | ні |
| [__init__](jane_assistant.sampling.md#jane_assistantsamplingsample__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:33](../../../../../../services/assistant/tests/test_units.py#L33).

```python
reserve = [Sample({}, "", s) for s in ["p", "p", "p", "c", "c", "n"]]
```

Контекст і передумови: [services/assistant/tests/test_units.py:293](../../../../../../services/assistant/tests/test_units.py#L293).

```python
sample = SampleResult(
        [Sample({"material_id": "web:1"}, "text", "t/*", "product", 0.9)], 0.9, True, None, {"k": 1}
    )
```

## jane_assistant.sampling.Sample.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/sampling.py:71](../../../../../../services/assistant/src/jane_assistant/sampling.py#L71).

```python
def __init__(self, material: dict[str, Any], text: str, shape: str, material_type: str = 'other', confidence: float = 0.0, reduced_from_bytes: int | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `shape` | `str` | `—` | positional-or-keyword |
| `material_type` | `str` | `'other'` | positional-or-keyword |
| `confidence` | `float` | `0.0` | positional-or-keyword |
| `reduced_from_bytes` | `int \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:33](../../../../../../services/assistant/tests/test_units.py#L33).

```python
reserve = [Sample({}, "", s) for s in ["p", "p", "p", "c", "c", "n"]]
```

Контекст і передумови: [services/assistant/tests/test_units.py:293](../../../../../../services/assistant/tests/test_units.py#L293).

```python
sample = SampleResult(
        [Sample({"material_id": "web:1"}, "text", "t/*", "product", 0.9)], 0.9, True, None, {"k": 1}
    )
```

## jane_assistant.sampling.Sample.material

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:72](../../../../../../services/assistant/src/jane_assistant/sampling.py#L72).

```python
material: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.Sample.text

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:73](../../../../../../services/assistant/src/jane_assistant/sampling.py#L73).

```python
text: str
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.Sample.shape

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:74](../../../../../../services/assistant/src/jane_assistant/sampling.py#L74).

```python
shape: str
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.Sample.material_type

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:75](../../../../../../services/assistant/src/jane_assistant/sampling.py#L75).

```python
material_type: str = 'other'
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.Sample.confidence

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:76](../../../../../../services/assistant/src/jane_assistant/sampling.py#L76).

```python
confidence: float = 0.0
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.Sample.reduced_from_bytes

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:77](../../../../../../services/assistant/src/jane_assistant/sampling.py#L77).

```python
reduced_from_bytes: int | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Size of the page as served when ``material`` holds its reduced copy (``material.max_fixture_bytes``).
```

## jane_assistant.sampling.SampleResult

**Клас.** Код: [services/assistant/src/jane_assistant/sampling.py:82](../../../../../../services/assistant/src/jane_assistant/sampling.py#L82).

```python
class SampleResult:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [samples](jane_assistant.sampling.md#jane_assistantsamplingsampleresultsamples) | Поле | ні |
| [confidence](jane_assistant.sampling.md#jane_assistantsamplingsampleresultconfidence) | Поле | ні |
| [sufficient](jane_assistant.sampling.md#jane_assistantsamplingsampleresultsufficient) | Поле | ні |
| [message](jane_assistant.sampling.md#jane_assistantsamplingsampleresultmessage) | Поле | ні |
| [hints](jane_assistant.sampling.md#jane_assistantsamplingsampleresulthints) | Поле | ні |
| [counts](jane_assistant.sampling.md#jane_assistantsamplingsampleresultcounts) | Метод | ні |
| [of_type](jane_assistant.sampling.md#jane_assistantsamplingsampleresultof_type) | Метод | ні |
| [wire](jane_assistant.sampling.md#jane_assistantsamplingsampleresultwire) | Метод | ні |
| [__init__](jane_assistant.sampling.md#jane_assistantsamplingsampleresult__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:293](../../../../../../services/assistant/tests/test_units.py#L293).

```python
sample = SampleResult(
        [Sample({"material_id": "web:1"}, "text", "t/*", "product", 0.9)], 0.9, True, None, {"k": 1}
    )
```

## jane_assistant.sampling.SampleResult.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/sampling.py:82](../../../../../../services/assistant/src/jane_assistant/sampling.py#L82).

```python
def __init__(self, samples: list[Sample], confidence: float, sufficient: bool, message: str | None, hints: dict[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `samples` | `list[Sample]` | `—` | positional-or-keyword |
| `confidence` | `float` | `—` | positional-or-keyword |
| `sufficient` | `bool` | `—` | positional-or-keyword |
| `message` | `str \| None` | `—` | positional-or-keyword |
| `hints` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:293](../../../../../../services/assistant/tests/test_units.py#L293).

```python
sample = SampleResult(
        [Sample({"material_id": "web:1"}, "text", "t/*", "product", 0.9)], 0.9, True, None, {"k": 1}
    )
```

## jane_assistant.sampling.SampleResult.samples

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:83](../../../../../../services/assistant/src/jane_assistant/sampling.py#L83).

```python
samples: list[Sample]
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.SampleResult.confidence

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:84](../../../../../../services/assistant/src/jane_assistant/sampling.py#L84).

```python
confidence: float
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.SampleResult.sufficient

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:85](../../../../../../services/assistant/src/jane_assistant/sampling.py#L85).

```python
sufficient: bool
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.SampleResult.message

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:86](../../../../../../services/assistant/src/jane_assistant/sampling.py#L86).

```python
message: str | None
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.SampleResult.hints

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:87](../../../../../../services/assistant/src/jane_assistant/sampling.py#L87).

```python
hints: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_assistant.sampling.SampleResult.counts

**Метод.** Код: [services/assistant/src/jane_assistant/sampling.py:89](../../../../../../services/assistant/src/jane_assistant/sampling.py#L89).

```python
def counts(self) -> Counter[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Counter[str]`.

## jane_assistant.sampling.SampleResult.of_type

**Метод.** Код: [services/assistant/src/jane_assistant/sampling.py:92](../../../../../../services/assistant/src/jane_assistant/sampling.py#L92).

```python
def of_type(self, material_type: str) -> list[Sample]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `material_type` | `str` | `—` | positional-or-keyword |

Результат: `list[Sample]`.

## jane_assistant.sampling.SampleResult.wire

**Метод.** Код: [services/assistant/src/jane_assistant/sampling.py:95](../../../../../../services/assistant/src/jane_assistant/sampling.py#L95).

```python
def wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.sampling.Evidence

**Клас.** Код: [services/assistant/src/jane_assistant/sampling.py:113](../../../../../../services/assistant/src/jane_assistant/sampling.py#L113).

```python
class Evidence:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [hosts](jane_assistant.sampling.md#jane_assistantsamplingevidencehosts) | Поле | ні |
| [limits](jane_assistant.sampling.md#jane_assistantsamplingevidencelimits) | Поле | ні |
| [shas](jane_assistant.sampling.md#jane_assistantsamplingevidenceshas) | Поле | ні |
| [canonicals](jane_assistant.sampling.md#jane_assistantsamplingevidencecanonicals) | Поле | ні |
| [patterns](jane_assistant.sampling.md#jane_assistantsamplingevidencepatterns) | Поле | ні |
| [examples](jane_assistant.sampling.md#jane_assistantsamplingevidenceexamples) | Поле | ні |
| [pagination](jane_assistant.sampling.md#jane_assistantsamplingevidencepagination) | Поле | ні |
| [observe](jane_assistant.sampling.md#jane_assistantsamplingevidenceobserve) | Метод | ні |
| [canonical_wire](jane_assistant.sampling.md#jane_assistantsamplingevidencecanonical_wire) | Метод | ні |
| [wire](jane_assistant.sampling.md#jane_assistantsamplingevidencewire) | Метод | ні |
| [__init__](jane_assistant.sampling.md#jane_assistantsamplingevidence__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
What sampled pages say about discovery: canonical declarations, link patterns, pagination.
```

## jane_assistant.sampling.Evidence.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/sampling.py:113](../../../../../../services/assistant/src/jane_assistant/sampling.py#L113).

```python
def __init__(self, hosts: list[str], limits: OnboardingLimits, shas: dict[str, str] = <factory dict>, canonicals: list[tuple[str, str]] = <factory list>, patterns: Counter[str] = <factory Counter>, examples: dict[str, list[str]] = <factory dict>, pagination: dict[str, dict[str, Any]] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `hosts` | `list[str]` | `—` | positional-or-keyword |
| `limits` | `OnboardingLimits` | `—` | positional-or-keyword |
| `shas` | `dict[str, str]` | `factory: dict` | positional-or-keyword |
| `canonicals` | `list[tuple[str, str]]` | `factory: list` | positional-or-keyword |
| `patterns` | `Counter[str]` | `factory: Counter` | positional-or-keyword |
| `examples` | `dict[str, list[str]]` | `factory: dict` | positional-or-keyword |
| `pagination` | `dict[str, dict[str, Any]]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_assistant.sampling.Evidence.hosts

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:116](../../../../../../services/assistant/src/jane_assistant/sampling.py#L116).

```python
hosts: list[str]
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.Evidence.limits

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:117](../../../../../../services/assistant/src/jane_assistant/sampling.py#L117).

```python
limits: OnboardingLimits
```

Доступ: читання — так; запис — так.

## jane_assistant.sampling.Evidence.shas

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:118](../../../../../../services/assistant/src/jane_assistant/sampling.py#L118).

```python
shas: dict[str, str] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_assistant.sampling.Evidence.canonicals

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:119](../../../../../../services/assistant/src/jane_assistant/sampling.py#L119).

```python
canonicals: list[tuple[str, str]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_assistant.sampling.Evidence.patterns

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:120](../../../../../../services/assistant/src/jane_assistant/sampling.py#L120).

```python
patterns: Counter[str] = field(default_factory=Counter)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "Counter"
}
```

## jane_assistant.sampling.Evidence.examples

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:121](../../../../../../services/assistant/src/jane_assistant/sampling.py#L121).

```python
examples: dict[str, list[str]] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_assistant.sampling.Evidence.pagination

**Поле.** Код: [services/assistant/src/jane_assistant/sampling.py:122](../../../../../../services/assistant/src/jane_assistant/sampling.py#L122).

```python
pagination: dict[str, dict[str, Any]] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_assistant.sampling.Evidence.observe

**Метод.** Код: [services/assistant/src/jane_assistant/sampling.py:124](../../../../../../services/assistant/src/jane_assistant/sampling.py#L124).

```python
def observe(self, material: dict[str, Any], raw: bytes, text: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |
| `raw` | `bytes` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.sampling.Evidence.canonical_wire

**Метод.** Код: [services/assistant/src/jane_assistant/sampling.py:145](../../../../../../services/assistant/src/jane_assistant/sampling.py#L145).

```python
def canonical_wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.sampling.Evidence.wire

**Метод.** Код: [services/assistant/src/jane_assistant/sampling.py:161](../../../../../../services/assistant/src/jane_assistant/sampling.py#L161).

```python
def wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.sampling.coverage

**Функція.** Код: [services/assistant/src/jane_assistant/sampling.py:202](../../../../../../services/assistant/src/jane_assistant/sampling.py#L202).

```python
def coverage(counts: Counter[str], min_examples: int) -> float:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `counts` | `Counter[str]` | `—` | positional-or-keyword |
| `min_examples` | `int` | `—` | positional-or-keyword |

Результат: `float`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:26](../../../../../../services/assistant/tests/test_units.py#L26).

```python
assert coverage(Counter(), 2) == 0.0
```

Контекст і передумови: [services/assistant/tests/test_units.py:27](../../../../../../services/assistant/tests/test_units.py#L27).

```python
assert coverage(Counter({"a": 1, "b": 1, "c": 1}), 2) == 0.0
```

## jane_assistant.sampling.sampling_rules

**Функція.** Код: [services/assistant/src/jane_assistant/sampling.py:252](../../../../../../services/assistant/src/jane_assistant/sampling.py#L252).

```python
def sampling_rules(source_kind: str, url: str | None, telegram_username: str | None, allowed: list[str], hints: dict[str, Any] | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `source_kind` | `str` | `—` | positional-or-keyword |
| `url` | `str \| None` | `—` | positional-or-keyword |
| `telegram_username` | `str \| None` | `—` | positional-or-keyword |
| `allowed` | `list[str]` | `—` | positional-or-keyword |
| `hints` | `dict[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:173](../../../../../../services/assistant/tests/test_material.py#L173).

```python
hinted = sampling_rules(
        "web",
        BASE,
        None,
        ["shop.example.test"],
        {
            "scope": {"allowed_schemes": ["https"], "path_prefixes": ["/catalog/c80004/"]},
            "strategies": [{"type": "listing", "start_urls": [BASE]}],
        },
    )
```

Контекст і передумови: [services/assistant/tests/test_material.py:190](../../../../../../services/assistant/tests/test_material.py#L190).

```python
default = sampling_rules("web", BASE, None, ["shop.example.test"], None)
```

## jane_assistant.sampling.sample_source

**Функція.** Код: [services/assistant/src/jane_assistant/sampling.py:322](../../../../../../services/assistant/src/jane_assistant/sampling.py#L322).

```python
async def sample_source(*, collector: CollectorClient, llm: LlmSession, limits: ServiceLimits, job_key: str, source_id: str, source_kind: str, rules: dict[str, Any], model: str, progress: Progress, crawl_limits: dict[str, Any] | None=None) -> SampleResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `collector` | `CollectorClient` | `—` | keyword-only |
| `llm` | `LlmSession` | `—` | keyword-only |
| `limits` | `ServiceLimits` | `—` | keyword-only |
| `job_key` | `str` | `—` | keyword-only |
| `source_id` | `str` | `—` | keyword-only |
| `source_kind` | `str` | `—` | keyword-only |
| `rules` | `dict[str, Any]` | `—` | keyword-only |
| `model` | `str` | `—` | keyword-only |
| `progress` | `Progress` | `—` | keyword-only |
| `crawl_limits` | `dict[str, Any] \| None` | `None` | keyword-only |

Результат: `SampleResult`.

### Опис із вихідного коду

```text
``crawl_limits``: the user's ``crawl_hints.limits.crawl`` (validated by the caller); its
``max_pages_per_run`` can only lower the sampling bound.
```
