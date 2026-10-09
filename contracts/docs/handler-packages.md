# Що є пакетом для кожного типу обробника

Усі типи версіонуються в одному репозиторії (registry.v1) з однаковими механізмами: незмінні
версії з дайджестом, тести, походження, форки, статуси. Відрізняється лише `entry` маніфесту і
те, хто виконує пакет. Схема маніфесту — [`package-manifest.schema.json`](../schemas/package-manifest.schema.json),
приклади — `examples/schemas/package-manifest/`.

| kind | Що в пакеті | Хто виконує | entry |
|---|---|---|---|
| `extractor` | **Код** Python (`src/`), схеми сутностей (`schemas/`), параметри, тести (`tests/`) | handler-runtime у пісочниці | `PythonEntry` (`runtime: python`, `module`, `callable`) |
| `transform` | Код Python або посилання на операцію сервісу | handler-runtime або вказаний виконавець | `PythonEntry` або `ExecutorEntry` |
| `storage` | **Маніфест і конфігурація**: тип адаптера, що пише (raw/entities), формати, історія, схема параметрів. Коду немає — адаптери живуть у сервісі storage | storage | `StorageEntry` (`executor: storage`, `adapter`, `writes`, `format`) |
| `llm` | **Маніфест і конфігурація**: інструкції (промпт), шаблон вхідних даних, схема виходу, псевдонім моделі, параметри. Коду немає | llm | `LlmEntry` (`executor: llm`, `instructions`, `output_schema`, `model`) |
| `collector-rules` | Файл правил за `collector-rules.schema.json` + тести (очікувані URL) | web-collector / telegram-collector | `CollectorRulesEntry` (`collector`, `rules`) |

## Структура архіву

```text
jane-package.json            # маніфест (обов'язково)
src/<module>/…               # код (extractor, transform)
schemas/*.schema.json        # схеми параметрів, сутностей, виходу
prompts/*.md                 # інструкції й шаблони (llm)
rules.json                   # правила колектора (collector-rules)
tests/<case>/…               # вхідні матеріали й очікувані результати
README.md                    # необов'язково
```

Архів — zip, шляхи з `/`, без `..`, без симлінків, без секретів. Дайджест: `sha256` від
канонічного архіву (файли відсортовані за шляхом, фіксовані час і права) — обчислює registry.

Канонічний ZIP містить лише звичайні файли у порядку ASCII-шляхів: `ZIP_STORED` (без стиснення),
час `1980-01-01 00:00:00`, Unix `create_system = 3`, права `0o100644 << 16`, без extra/comment.
Вхідний ZIP registry розпаковує й перепаковує; digest — SHA-256 цих канонічних байтів, а не вхідного ZIP.
`jane-package.json` із JSON-запиту серіалізується в UTF-8, з відступом 2, збереженим порядком ключів,
без ASCII escaping і з кінцевим newline. Точна реалізація —
[`archive.py`](../../services/registry/src/jane_registry/archive.py).

Digest у JSON/OpenAPI прикладах **ілюстративні**: вони показують формат і зв'язки посилань,
а не підтверджують байти архіву, який не постачається з прикладом. Для виконання/імпорту беріть digest
із відповіді registry або обчислюйте з фактичного канонічного ZIP; його перевіряють також storage/runtime.
Невідомий `dependencies.runtime_profile` registry відхиляє як `dependency_not_allowed`; якщо профілі
не вдалося завантажити із зовнішнього джерела, повертає `upstream_unavailable`. Runtime також відхиляє
відсутній профіль/образ як `dependency_not_allowed`. У diff `jane-package.json`
представлено тільки в `manifest_changes`, решта файлів — у `files`
([`diffing.py`](../../services/registry/src/jane_registry/diffing.py)).

## Обов'язкові властивості

- **Точна версія** (SemVer); етап завдання посилається на `package_id@version` (+ `digest`).
- **Незмінність**: зміна = нова версія; `provenance.based_on` — попередня версія.
- **Походження**: `provenance.created_by` = human | llm | import; для LLM — модель, job асистента, причина.
- **Форк**: `fork_of` (батько, версія, дайджест) встановлює registry; перенесення змін батька —
  лише командою `upstream-ports`, результат — нова версія з `provenance.upstream_port`.
- **Без секретів**: лише `required_connections` (логічні імена + kind); значення підключень
  задаються в середовищі виконання і не копіюються під час форку.
- **Тести**: кожен пакет `extractor`/`llm` має щонайменше один тест `success` і один `empty` або
  `unrecognized`; тести запускаються без запису в робочі дані (`POST /v1/test-runs`).
- **Залежності** екстрактора — лише з профілю runtime (`dependencies.runtime_profile`); мережі під
  час виконання немає, якщо `access.network` не `allowlist` і політика платформи це дозволяє.

## Пакет `llm`: вихід моделі → результат обробника

Так виконує пакети `kind: llm` сервіс llm (`handler.v1`, реалізація —
[`handler.py`](../../services/llm/src/jane_llm/handler.py)); інший виконавець пакетів `llm` має дотримуватися
того самого правила, щоб пакет давав однакові сутності.

1. **Один запит на вхід.** Для кожного елемента `inputs` — один структурований запит: файл `entry.instructions` —
   довірений канал; вхід (метадані й вміст матеріалу, `entities` чи `data`, або заповнений `entry.input_template`) —
   лише недовірені дані. Вихід перевіряється за `entry.output_schema` (з повторами шлюзу); невідповідність —
   `failed` / `schema_mismatch` з `diagnostics.validation_errors`.
2. **`output.data`** — розібраний вихід моделі; для кількох входів — `{"results": [<вихід входу 0>, …]}`.
3. **`output.entities`** є, лише якщо маніфест оголошує `output.entities[]`, і заповнюється лише для входів
   `kind: material`. Для кожного оголошеного типу `T` береться верхньорівневе поле виходу `T + "s"`, а якщо його
   немає — `T`; об'єкт вважається масивом з одного елемента, інші значення (і елементи, що не є об'єктами)
   пропускаються. Кожен елемент стає `EntityRecord`:
   - `entity_type` = `T`; `schema` = `<package_id>@<version>#<T>`;
   - `fields` — поля елемента без значень `null` (пропуск ≠ очищення; `cleared` LLM-обробник не заповнює,
     `completeness` не задає — типово `partial`);
   - `key.natural` — значення `key_fields` типу з елемента (лише рядок, число чи boolean); ключове поле з іменем
     `message`, `material` або `material_id`, якого немає серед скалярів елемента, береться з `material_id`
     матеріалу (і додається до `fields`); бракує іншого ключового поля — помилка елемента;
   - `key.scope` — `material.source.source_id`, інакше `context.trace.source_id` виклику, інакше `local`;
   - `observation` — з матеріалу: `observation_id`, `observed_at` = `fetched_at`, `material_id`, а також
     `revision.sequence` і `revision.content_sha256`, якщо є.
   `fields` перевіряються за схемою сутності `output.entities[].schema` (якщо файл є в пакеті). Помилка ключа чи схеми хоча б
   одного елемента — уся відповідь `failed` / `schema_mismatch` з вказівниками `/<T>s/<i>/…`.
4. **Стан:** пакет оголошує сутності → `success`, якщо є хоча б одна сутність, інакше `empty`; не оголошує →
   `success`, якщо вихід хоча б одного входу непорожній, інакше `empty`. Вичерпаний бюджет LLM — `failed` /
   `budget_exhausted` (без звернення до провайдера; повторна доставка після збільшення бюджету виконується
   знову), невалідні параметри чи вхід, який пакет не приймає, — `failed` / `invalid_params`.
5. Витрати — `usage.llm` (провайдер, модель, токени, вартість); бюджети — за `context.trace.{source_id, task_id,
   run_id}` (див. `Budget` у [`limits.schema.json`](../schemas/common/limits.schema.json)).

## Автономне використання

`GET /v1/packages/{id}/versions/{v}/archive` дає архів, достатній для виконання без репозиторію:
handler-runtime CLI (WP-06) виконує екстрактор на локальному файлі; будь-який виконавець приймає
архів у `HandlerInvocation.package_archive`.
