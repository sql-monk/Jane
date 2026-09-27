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

## Автономне використання

`GET /v1/packages/{id}/versions/{v}/archive` дає архів, достатній для виконання без репозиторію:
handler-runtime CLI (WP-06) виконує екстрактор на локальному файлі; будь-який виконавець приймає
архів у `HandlerInvocation.package_archive`.
