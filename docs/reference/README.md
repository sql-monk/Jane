# Довідники

Індекс довідників Jane: публічні API, типи й публічні члени модулів, формат пакетів обробників. Довідники генеруються з актуальних контрактів і коду; ця сторінка лише веде до них.

## Зміст

- [API](#api)
- [Типи й публічні члени](#типи-й-публічні-члени)
- [Пакети обробників](#пакети-обробників)
- [Нормативні джерела](#нормативні-джерела)

## API

| Довідник | Контракт |
|---|---|
| [Загальний індекс API](api/README.md) | усі контракти `contracts/openapi` |
| [Колектор](api/collector/README.md) | `collector.v1` — Web Collector, Telegram Collector |
| [Обробник](api/handler/README.md) | `handler.v1` — Storage, Handler Runtime, LLM gateway |
| [Storage](../components/storage/reference/api/README.md) | `storage.v1` |
| [Registry](../components/registry/reference/api/README.md) | `registry.v1` |
| [Orchestrator](../components/orchestrator/reference/api/README.md) | `orchestrator.v1` |
| [LLM gateway](../components/llm/reference/api/README.md) | `llm.v1` |
| [Assistant](../components/assistant/reference/api/README.md) | `assistant.v1` |

Спільні конвенції всіх API (версії, помилки, ідемпотентність, асинхронні операції, пагінація, автентифікація) — [архітектура](../architecture/README.md#спільні-конвенції-api).

## Типи й публічні члени

Довідники у стилі MSDN: класи, функції, протоколи, переліки й налаштування з сигнатурами, параметрами та посиланнями на код.

| Модуль | Довідник |
|---|---|
| Web Collector | [типи](../components/web-collector/reference/types/README.md) |
| Telegram Collector | [типи](../components/telegram-collector/reference/types/README.md) |
| Storage | [типи](../components/storage/reference/types/README.md) |
| Handler Runtime | [типи](../components/handler-runtime/reference/types/README.md) |
| LLM gateway | [типи](../components/llm/reference/types/README.md) |
| Registry | [типи](../components/registry/reference/types/README.md) |
| Orchestrator | [типи](../components/orchestrator/reference/types/README.md) |
| Assistant | [типи](../components/assistant/reference/types/README.md) |
| jane-kit | [типи](../components/jane-kit/reference/types/README.md) |
| jane-extractor-sdk | [типи](../components/extractor-sdk/reference/types/README.md) |
| jane-contracts | [типи](../components/contracts/reference/types/README.md) |
| Admin UI | [типи](../components/admin/reference/types/README.md) |

## Пакети обробників

[Довідник пакетів](packages/README.md): структура архіву, маніфест `jane-package.json`, схеми, версії, залежності, тести, походження, форки, публікація й сумісність.

## Нормативні джерела

| Джерело | Зміст |
|---|---|
| [contracts/openapi](../../contracts/openapi/) | OpenAPI 3.1 усіх API |
| [contracts/schemas](../../contracts/schemas/) | JSON Schema даних: матеріал, сутність, джерело, завдання, маніфест пакета, спільні типи |
| [contracts/docs](../../contracts/docs/) | модель помилок, власність даних, пакети, адаптери збереження, стратегії пошуку |
| [contracts/README.md](../../contracts/README.md) | структура контрактів, команди перевірки, дозволи операцій |
