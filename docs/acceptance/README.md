# Приймання

Матриця зв'язує критерії приймання [ТЗ §12](../../TECHNICAL_SPECIFICATION.md#12-критерії-приймання) зі сценаріями, автоматичними тестами й доказами перевірок. Сценарії описано в [scenarios.md](scenarios.md), запуск наскрізних тестів — у [tests/e2e/README.md](../../tests/e2e/README.md). Відповідність вимогам до документації — у [documentation.md](documentation.md).

![Карта критеріїв приймання](../diagrams/acceptance/criteria-map.light.png#gh-light-mode-only)
![Карта критеріїв приймання](../diagrams/acceptance/criteria-map.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../diagrams/acceptance/criteria-map.light.png), [темне](../diagrams/acceptance/criteria-map.dark.png); джерело — [criteria-map.drawio](../diagrams/acceptance/criteria-map.drawio).

## Як читати докази

- **Перевірено** — команду виконано під час підготовки цієї документації 2026-10-11 на Windows 11, ревізії `48389a3`–`c59d26d` (код між ними не змінювався); результат наведено.
- **Не перевірено** — тест існує, але в цій роботі не запускався. Наскрізні тести `just e2e` у цій роботі не запускалися.

## Матриця

| № | Критерій ТЗ §12 | Сценарії | Тести | Доказ у цій роботі |
|---|---|---|---|---|
| 1 | Незалежне використання колектора й екстрактора стороннім застосунком | S-M1-01, S-M1-04 | `tests/e2e/test_m1.py` | Перевірено: Web Collector окремо віддає матеріал ([README](../../README.md#модуль-окремо-web-collector)); `jane-handler-runtime test` і `run` на прикладі екстрактора → 5 passed, `success` ([Handler Runtime](../components/handler-runtime/quickstart.md)) |
| 2 | Ланцюжок із розгалуженням, екстракцією та збереженням | S-M1-03, S-M2-11 | `test_m1.py`, `test_m2_llm_routing.py` | Перевірено: `jane_examples.py demo` на стеку — collect 23, store-raw 23, extract 16, store 16 ([end-to-end](../getting-started/end-to-end.md)); quickstart Orchestrator → запуск `succeeded` ([Orchestrator](../components/orchestrator/quickstart.md)) |
| 3 | Зміна сховища без зміни коду колектора й екстрактора | S-M1-05, S-M2-08 | `test_m1.py`, `test_m2_storage.py` | Частково: Storage з файловим адаптером і PostgreSQL ([Storage](../components/storage/quickstart.md)); перемикання в завданні не перевірено |
| 4 | Підготовка екстрактора через LLM для нового джерела | S-M2-06 | `test_m2_assistant.py` | Не перевірено |
| 5 | Окремі завдання повного каталогу й перевірки цін | S-M2-04 | `test_m2_prices.py` | Перевірено: demo — 16 сутностей, 4 часткові оновлення цін (версія 2) |
| 6 | Вдосконалення екстрактора з тестуванням і відкатом | S-M2-07 | `test_m2_assistant.py` | Не перевірено |
| 7 | Незмінність форку після оновлення батька | S-M2-01 | `test_m2_registry.py` | Перевірено: форк, diff, `upstream-port` з конфліктом у Registry; `just test registry` → 117 passed, `just integration … services/registry` → 30 passed |
| 8 | Відновлення після збою й повторна доставка | R-* | `test_reliability*.py`, `test_r04_*.py`, `test_r06_*.py`, `test_r07_*.py` | Частково: повтор `delivery_key` → `duplicate: true` у Storage і Handler Runtime; інтеграційні тести Orchestrator → 54 passed, **6 failed** (див. [звіт](../delivery/README.md#відкриті-питання)) |
| 9 | Пакети різних типів в одному Registry, фіксація версій, форки | S-M2-01 | `test_m2_registry.py`, `test_m2_registry_types.py` | Перевірено частково: публікація, `version_exists`, дайджест збігся з `examples/packages.lock.json` |
| 10 | Рекурсивний обхід, Sitemap і додаткові способи окремо й разом | S-M2-03 | `test_m2_discovery.py` | Не перевірено |
| 11 | LLM не викликається для невідомої сторінки без опції, викликається з нею | S-M2-05 | `test_m2_llm_routing.py` | Частково: невідомий матеріал зареєстровано з `forwarded_to_llm: false`; виклик після ввімкнення не перевірено |
| 12 | Кожен адаптер зберігає RAW і результати | S-M2-08 | `test_m2_storage.py` | Частково: files і PostgreSQL (`just integration … adapters/postgres` → 17 passed); SQL Server, MongoDB, MinIO, S3 не перевірено |
| 13 | Зміна лімітів без зміни коду; перевірені профілі середовищ | S-M2-09 | `test_m2_limits.py`, `deploy/profiles/` | Частково: ліміт через змінну середовища в jane-kit і Web Collector; профіль `ci` у цій роботі не вимірювався ([deploy/profiles](../../deploy/profiles/README.md)) |

## Як повторити

```powershell
just e2e
```

Тест піднімає власний ізольований стек і прибирає його сам; тривалість і вимоги — у [tests/e2e/README.md](../../tests/e2e/README.md).
