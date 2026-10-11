# Довідники Jane

Обери HTTP API для інтеграції сервісу, публічний тип для роботи з кодом або формат пакета для розширення обробки.

## Модульні довідники

| Модуль | API | Публічні типи й члени | Конфігурація |
|---|---|---|---|
| Web Collector | [Операції](../components/web-collector/reference/api/README.md) | [Типи](../components/web-collector/reference/types/README.md) | [Параметри](../components/web-collector/configuration.md) |
| Telegram Collector | [Операції](../components/telegram-collector/reference/api/README.md) | [Типи](../components/telegram-collector/reference/types/README.md) | [Параметри](../components/telegram-collector/configuration.md) |
| Storage | [Операції](../components/storage/reference/api/README.md) | [Типи](../components/storage/reference/types/README.md) | [Параметри](../components/storage/configuration.md) |
| LLM | [Операції](../components/llm/reference/api/README.md) | [Типи](../components/llm/reference/types/README.md) | [Параметри](../components/llm/configuration.md) |
| Handler Runtime | [Операції](../components/handler-runtime/reference/api/README.md) | [Типи](../components/handler-runtime/reference/types/README.md) | [Параметри](../components/handler-runtime/configuration.md) |
| Registry | [Операції](../components/registry/reference/api/README.md) | [Типи](../components/registry/reference/types/README.md) | [Параметри](../components/registry/configuration.md) |
| Orchestrator | [Операції](../components/orchestrator/reference/api/README.md) | [Типи](../components/orchestrator/reference/types/README.md) | [Параметри](../components/orchestrator/configuration.md) |
| Assistant | [Операції](../components/assistant/reference/api/README.md) | [Типи](../components/assistant/reference/types/README.md) | [Параметри](../components/assistant/configuration.md) |
| Admin | [Операції](../components/admin/reference/api/README.md) | [Типи](../components/admin/reference/types/README.md) | [Параметри](../components/admin/configuration.md) |
| Jane Kit | [Операції](../components/jane-kit/reference/api/README.md) | [Типи](../components/jane-kit/reference/types/README.md) | [Параметри](../components/jane-kit/configuration.md) |
| Extractor SDK | [Операції](../components/extractor-sdk/reference/api/README.md) | [Типи](../components/extractor-sdk/reference/types/README.md) | [Параметри](../components/extractor-sdk/configuration.md) |

## Спільні формати

- [Пакети, маніфест і мінімальний приклад](packages/README.md).
- [Публікація](packages/publishing.md) та [версії й форки](packages/versions.md).
- [Контракти API, JSON Schema та Protocol-и](../../contracts/README.md).
- [Коди помилок і повторні спроби](../../contracts/docs/errors.md).
- [Документи, ContentRef і власність даних](../architecture/data.md).

## Генеровані декларації

Декларації автоматично звіряються з кодом: [symbols.json](symbols.json), [api-operations.json](api-operations.json), [configuration.json](configuration.json). Опис сигнатури містить параметри, типи, defaults, результати, public-члени й доступність властивостей; ручні сторінки пояснюють застосування та обмеження.

Повноту декларацій і повноту пояснень перевіряють окремо. Незакриті пояснення, приклади й залежні винятки записані в `symbols.json → coverage.explanation_gaps` і [матриці приймання](../acceptance/documentation-matrix.md). Оновлення довідників — [інструменти документації](../development/documentation-tools.md).
