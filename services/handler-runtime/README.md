# Handler Runtime

Сервіс виконує пакети обробників на Python — екстрактори й перетворення — в ізольованій контейнерній пісочниці через спільний API обробників `handler.v1`. Працює окремо, без Orchestrator і Registry.

Повна документація модуля — [docs/components/handler-runtime](../../docs/components/handler-runtime/README.md): [швидкий старт](../../docs/components/handler-runtime/quickstart.md), [конфігурація](../../docs/components/handler-runtime/configuration.md), [інтеграція](../../docs/components/handler-runtime/integration.md), [будова](../../docs/components/handler-runtime/internals.md), [експлуатація](../../docs/components/handler-runtime/operations.md).

Коротко, з кореня репозиторію:

```powershell
uv run --package jane-handler-runtime jane-handler-runtime build-image
uv run --package jane-handler-runtime jane-handler-runtime test libs/extractor-sdk/examples/testsite-product-extractor
uv run --package jane-handler-runtime jane-handler-runtime serve
```

Тести: `just test handler-runtime` (unit і контрактні, бекенд `subprocess`); ізоляція на справжньому Docker — `just isolation` (лише Linux).
