# Пакети обробників

Пакет обробника — незмінний архів, з якого виконавець знає, що й як обробляти: маніфест `jane-package.json`, код або конфігурацію, схеми результатів і тести. В одному форматі версіонуються екстрактори, пакети збереження, LLM-пакети, перетворення й правила колекторів. Пакети зберігає [Registry](../../components/registry/README.md); виконують їх Handler Runtime, Storage, LLM gateway або колектори.

Нормативні джерела формату — схема [package-manifest.schema.json](../../../contracts/schemas/package-manifest.schema.json) і опис [handler-packages.md](../../../contracts/docs/handler-packages.md). Цей довідник пояснює їх і показує на реальних пакетах із [examples/packages](../../../examples/packages/); за розбіжності правильні схема й контракт.

## Зміст

- [Сторінки довідника](#сторінки-довідника)
- [Життєвий цикл пакета](#життєвий-цикл-пакета)
- [Приклади в репозиторії](#приклади-в-репозиторії)
- [Пов'язані документи](#повязані-документи)

## Сторінки довідника

| Сторінка | Про що |
|---|---|
| [Структура й маніфест](manifest.md) | Файли архіву, усі поля `jane-package.json` із типами й обов'язковістю |
| [Типи пакетів](kinds.md) | `extractor`, `transform`, `storage`, `llm`, `collector-rules`: що в пакеті й хто його виконує |
| [Схеми й тести](schemas-and-tests.md) | Схеми параметрів, сутностей і виходу; тестові випадки, запуск і звіти тестів |
| [Версії, архів і дайджест](versions-and-archive.md) | SemVer, незмінність, канонічний ZIP, `digest` |
| [Залежності й доступи](dependencies.md) | Профілі runtime, Python-вимоги, залежності від пакетів, мережа, підключення, заборона секретів |
| [Походження й форки](provenance-and-forks.md) | `provenance`, `fork_of`, форк, diff, перенесення змін батька |
| [Публікація й статуси](publication.md) | Порядок перевірок, помилки, статуси версії, погодження й активація |
| [Експорт і сумісність](export-and-compatibility.md) | Автономне використання архіву, `jane-registry export`/`verify`, правила сумісності |

## Життєвий цикл пакета

1. **Підготовка.** Автор (людина або Assistant) складає каталог пакета: маніфест, код чи конфігурацію, схеми, тести. Тести запускаються локально — для екстрактора це `jane-handler-runtime test <каталог>`.
2. **Публікація.** Клієнт створює пакет (`POST /v1/packages`) і публікує версію (`POST /v1/packages/{id}/versions`). Registry перевіряє маніфест, файли, секрети й залежності, перепаковує файли в канонічний ZIP і обчислює `digest`. Нова версія має статус `draft`.
3. **Перевірка.** Звіти тестів записуються в версію (`POST …/test-results`); з них Registry обчислює `test_status` і `test_summary`.
4. **Погодження.** Версію переводять у `approved` вручну або за політикою автоактивації; `rejected`, `deprecated`, `yanked` — інші рішення.
5. **Використання.** Етап завдання в Orchestrator посилається на точну версію `package_id@version` (+ `digest`); виконавець завантажує архів і перевіряє дайджест. Архів можна експортувати й виконувати без Registry.
6. **Зміни.** Будь-яка зміна — нова версія з `provenance.based_on`. Чужий або спільний пакет змінюють через форк; зміни батька переносяться у форк лише явною командою.

Деталі кожного кроку — на сторінках із таблиці вище; схема станів версії — на сторінці [Публікація й статуси](publication.md#статуси-версії).

## Приклади в репозиторії

| Пакет | kind | Що показує |
|---|---|---|
| [examples.testsite-catalog-extractor](../../../examples/packages/examples.testsite-catalog-extractor/jane-package.json) | `extractor` | Повний екстрактор товарів тестового сайту з тестами `success`, `empty`, `unrecognized` |
| [examples.testsite-price-extractor](../../../examples/packages/examples.testsite-price-extractor/jane-package.json) | `extractor` | Часткове оновлення товару; тест із `origin: problem_sample` |
| [examples.telegram-event-extractor](../../../examples/packages/examples.telegram-event-extractor/jane-package.json) | `extractor` | Вхід тестів як JSON `Material`, порівняння `subset` |
| [examples.testsite-web-rules](../../../examples/packages/examples.testsite-web-rules/jane-package.json) | `collector-rules` | Правила Web Collector |
| [examples.telegram-rules](../../../examples/packages/examples.telegram-rules/jane-package.json) | `collector-rules` | Правила Telegram Collector |

Маніфести типів `storage` і `llm` є серед прикладів контрактів: [contracts/examples/schemas/package-manifest](../../../contracts/examples/schemas/package-manifest/). Дайджести пакетів прикладів зафіксовано в [examples/packages.lock.json](../../../examples/packages.lock.json); Registry видає ті самі значення після публікації.

## Пов'язані документи

- [Registry](../../components/registry/README.md) — сервіс, що зберігає пакети; його API — [довідник API Registry](../../components/registry/reference/api/README.md).
- [Контракт handler.v1](../api/handler/README.md) — як виконавці приймають пакет і повертають результат.
- [Модель помилок](../../../contracts/docs/errors.md) — коди `validation_failed`, `secret_detected`, `dependency_not_allowed` та інші.
