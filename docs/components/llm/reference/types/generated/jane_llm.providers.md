# jane_llm.providers

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.providers.AnthropicProvider](#jane_llmprovidersanthropicprovider)
- [jane_llm.providers.ProviderAdapter](#jane_llmprovidersprovideradapter)
- [jane_llm.providers.ProviderError](#jane_llmprovidersprovidererror)
- [jane_llm.providers.ProviderRequest](#jane_llmprovidersproviderrequest)
- [jane_llm.providers.ProviderResponse](#jane_llmprovidersproviderresponse)
- [jane_llm.providers.ResolvedConnection](#jane_llmprovidersresolvedconnection)
- [jane_llm.providers.FakeProvider](#jane_llmprovidersfakeprovider)
- [jane_llm.providers.ADAPTERS](#jane_llmprovidersadapters)

## jane_llm.providers.AnthropicProvider

**Повторний експорт.** Код: [services/llm/src/jane_llm/providers/__init__.py:5](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L5).

```python
from jane_llm.providers.anthropic import AnthropicProvider as AnthropicProvider
```

Повторний експорт: [jane_llm.providers.anthropic.AnthropicProvider](jane_llm.providers.anthropic.md#jane_llmprovidersanthropicanthropicprovider).

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:642](../../../../../../services/llm/tests/test_service.py#L642).

```python
resp = asyncio.run(AnthropicProvider().complete(req, conn, ServiceLimits()))
```

Контекст і передумови: [services/llm/tests/test_service.py:658](../../../../../../services/llm/tests/test_service.py#L658).

```python
asyncio.run(AnthropicProvider().complete(req, bad, ServiceLimits()))
```

## jane_llm.providers.ProviderAdapter

**Повторний експорт.** Код: [services/llm/src/jane_llm/providers/__init__.py:6](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L6).

```python
from jane_llm.providers.base import ProviderAdapter as ProviderAdapter
```

Повторний експорт: [jane_llm.providers.base.ProviderAdapter](jane_llm.providers.base.md#jane_llmprovidersbaseprovideradapter).

## jane_llm.providers.ProviderError

**Повторний експорт.** Код: [services/llm/src/jane_llm/providers/__init__.py:6](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L6).

```python
from jane_llm.providers.base import ProviderError as ProviderError
```

Повторний експорт: [jane_llm.providers.base.ProviderError](jane_llm.providers.base.md#jane_llmprovidersbaseprovidererror).

## jane_llm.providers.ProviderRequest

**Повторний експорт.** Код: [services/llm/src/jane_llm/providers/__init__.py:6](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L6).

```python
from jane_llm.providers.base import ProviderRequest as ProviderRequest
```

Повторний експорт: [jane_llm.providers.base.ProviderRequest](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequest).

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:58](../../../../../../services/llm/tests/test_fake_provider.py#L58).

```python
response = asyncio.run(
        fake.complete(ProviderRequest("m", prompt.system, prompt.user, 200), conn, limits or ServiceLimits())
    )
```

Контекст і передумови: [services/llm/tests/test_injection.py:119](../../../../../../services/llm/tests/test_injection.py#L119).

```python
naive = ProviderRequest(
        model_id="fake-deterministic-1",
        system="Classify the page type.",
        user=f"Page:\n{ATTACKS['plain']}",
        max_output_tokens=64,
        output_schema=SCHEMA,
    )
```

## jane_llm.providers.ProviderResponse

**Повторний експорт.** Код: [services/llm/src/jane_llm/providers/__init__.py:6](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L6).

```python
from jane_llm.providers.base import ProviderResponse as ProviderResponse
```

Повторний експорт: [jane_llm.providers.base.ProviderResponse](jane_llm.providers.base.md#jane_llmprovidersbaseproviderresponse).

## jane_llm.providers.ResolvedConnection

**Повторний експорт.** Код: [services/llm/src/jane_llm/providers/__init__.py:6](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L6).

```python
from jane_llm.providers.base import ResolvedConnection as ResolvedConnection
```

Повторний експорт: [jane_llm.providers.base.ResolvedConnection](jane_llm.providers.base.md#jane_llmprovidersbaseresolvedconnection).

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:57](../../../../../../services/llm/tests/test_fake_provider.py#L57).

```python
conn = None if params is None else ResolvedConnection("slow", "llm_provider", params)
```

Контекст і передумови: [services/llm/tests/test_service.py:632](../../../../../../services/llm/tests/test_service.py#L632).

```python
conn = ResolvedConnection(
        "anthropic-main", "llm_provider", {"api_base": url}, {"api_key": "test-key-not-secret"}
    )
```

## jane_llm.providers.FakeProvider

**Повторний експорт.** Код: [services/llm/src/jane_llm/providers/__init__.py:13](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L13).

```python
from jane_llm.providers.fake import FakeProvider as FakeProvider
```

Повторний експорт: [jane_llm.providers.fake.FakeProvider](jane_llm.providers.fake.md#jane_llmprovidersfakefakeprovider).

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:137](../../../../../../services/llm/tests/test_fake_provider.py#L137).

```python
ask(FakeProvider(), {"provider": "fake", "delay_ms": 200}, "x")
```

Контекст і передумови: [services/llm/tests/test_injection.py:126](../../../../../../services/llm/tests/test_injection.py#L126).

```python
resp = asyncio.run(FakeProvider().complete(naive, None, ServiceLimits()))
```

## jane_llm.providers.ADAPTERS

**Константа.** Код: [services/llm/src/jane_llm/providers/__init__.py:26](../../../../../../services/llm/src/jane_llm/providers/__init__.py#L26).

```python
ADAPTERS: dict[str, ProviderAdapter] = {'fake': FakeProvider(), 'anthropic': AnthropicProvider()}
```
