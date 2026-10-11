# Registry

Registry — репозиторій пакетів обробників і правил колекторів Jane. Він зберігає незмінні версії пакетів із дайджестом, тести й походження, підтримує форки, порівняння версій і явне перенесення змін батька, віддає архів версії для виконання без самого Registry. API — `registry.v1`.

## Зміст

- [Межі відповідальності](#межі-відповідальності)
- [Тип і автономність](#тип-і-автономність)
- [Основні сценарії](#основні-сценарії)
- [Будова в одному абзаці](#будова-в-одному-абзаці)
- [Комплект документації](#комплект-документації)

## Межі відповідальності

Registry відповідає за:

- пакети всіх типів (`extractor`, `transform`, `storage`, `llm`, `collector-rules`) і їхні налаштування (`auto_changes_allowed`, мітки, позначку `deprecated`);
- публікацію версій із перевірками: схема маніфесту, файли, схеми, тести, профіль runtime, пошук секретів;
- канонічний ZIP і `digest` кожної версії, зберігання архівів у blob-сховищі;
- статуси версій (`draft`, `approved`, `rejected`, `deprecated`, `yanked`) і звіти тестів;
- форки, diff, стан батька форку та перенесення змін батька за явною командою;
- експорт архівів і їх офлайн-перевірку (CLI `jane-registry`).

Registry не відповідає за:

- **виконання пакетів** — це Handler Runtime, Storage, LLM gateway і колектори;
- **запуск тестів** — звіти надходять від виконавця через `POST …/test-results`;
- **прив'язку версії до етапу завдання й активацію** — це Orchestrator;
- **генерацію чи виправлення пакетів** — це Assistant, який публікує результат у Registry як звичайний клієнт.

Формат пакетів описано окремо, у загальному довіднику [Пакети обробників](../../reference/packages/README.md).

## Тип і автономність

| Властивість | Значення |
|---|---|
| Тип модуля | репозиторій |
| Окремий запуск | так; для дослідів — без зовнішніх сервісів (`JANE_REGISTRY_DB=memory`, `JANE_REGISTRY_BLOB=filesystem`) |
| Обов'язкові залежності | PostgreSQL (власна БД `jane_registry`) і S3-сумісне сховище (MinIO) — у робочому режимі |
| Опційні залежності | Джерела профілів runtime (Handler Runtime `GET /v1/info` або файли) — потрібні для публікації пакетів із `dependencies.runtime_profile` |
| Від інших сервісів Jane | не залежить; Orchestrator не потрібен |
| Точка входу | `python -m jane_registry`, CLI `jane-registry` |
| Порт за замовчуванням | 8105 (у контейнері — 8000) |

Повний опис залежностей і поведінки за їхньої недоступності — [dependencies.md](dependencies.md).

![Клієнти Registry і його залежності](../../diagrams/registry/context.light.png#gh-light-mode-only)
![Клієнти Registry і його залежності](../../diagrams/registry/context.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/registry/context.light.png), [темне](../../diagrams/registry/context.dark.png); джерело — [context.drawio](../../diagrams/registry/context.drawio).

Admin UI, Assistant і сторонні застосунки керують пакетами через `registry.v1`; Orchestrator і виконавці пакетів лише читають версії й архіви. Registry сам звертається лише до власних сховищ і, за налаштування, до джерела профілів runtime.

## Основні сценарії

| Сценарій | Операції | Де описано |
|---|---|---|
| Опублікувати пакет і погодити версію | `POST /v1/packages`, `POST …/versions`, `POST …/status` | [quickstart.md](quickstart.md), [Публікація й статуси](../../reference/packages/publication.md) |
| Записати результати тестів | `POST …/test-results` | [Схеми й тести](../../reference/packages/schemas-and-tests.md#звіти-тестів-у-версії) |
| Знайти пакет для матеріалу | `GET /v1/packages?kind=&entity_type=&media_type=&domain=` | [integration.md](integration.md#пошук-пакетів) |
| Зробити форк і порівняти з батьком | `POST …/forks`, `GET …/diff` | [Походження й форки](../../reference/packages/provenance-and-forks.md) |
| Перенести зміни батька у форк | `GET …/upstream`, `POST …/upstream-ports`, `GET /v1/jobs/{id}` | [integration.md](integration.md#перенесення-змін-батька) |
| Використати пакет без Registry | `GET …/archive`, `jane-registry export`, `verify` | [Експорт і сумісність](../../reference/packages/export-and-compatibility.md) |

## Будова в одному абзаці

HTTP-шар ([app.py](../../../services/registry/src/jane_registry/app.py)) перевіряє автентифікацію, scope й ідемпотентність і передає запит доменній логіці ([service.py](../../../services/registry/src/jane_registry/service.py)). Метадані пакетів і версій лежать у сховищі метаданих (PostgreSQL або пам'ять процесу), архіви — у content-addressed blob-сховищі (S3/MinIO або каталог). Кілька екземплярів працюють на одній БД і одному бакеті. Деталі — [internals.md](internals.md).

## Комплект документації

| Документ | Зміст |
|---|---|
| [quickstart.md](quickstart.md) | Запуск без зовнішніх сервісів, публікація, форк, diff, експорт — з реальним виводом |
| [dependencies.md](dependencies.md) | PostgreSQL, blob-сховище, профілі runtime, бібліотеки; поведінка за недоступності |
| [configuration.md](configuration.md) | Змінні середовища, автентифікація, ліміти й спосіб застосування змін |
| [integration.md](integration.md) | Виклики зі стороннього застосунку, місце в Jane, заміна сумісною реалізацією |
| [internals.md](internals.md) | Компоненти коду, алгоритми, ER власної БД, гарантії |
| [operations.md](operations.md) | Health, метрики, журнали, оновлення й міграції, резервування, масштабування, типові проблеми |
| [Довідник API](reference/api/README.md) | Операції `registry.v1`, запити, відповіді, помилки |
| [Довідник типів](reference/types/README.md) | Публічні типи й члени пакета `jane_registry` |
| [Пакети обробників](../../reference/packages/README.md) | Формат і життєвий цикл пакетів |

Контракт — [registry.v1.yaml](../../../contracts/openapi/registry.v1.yaml); код — [services/registry](../../../services/registry/).
