---
name: jane-handler-package
description: Як скласти пакет обробника Jane (екстрактор, збереження, LLM, перетворення, правила колектора) — маніфест jane-package.json, схеми, тести, походження, канонічний архів і дайджест, публікація в репозиторій, форк і перенесення змін батька, експорт. Використовуй, коли створюєш, змінюєш, тестуєш чи генеруєш (зокрема через LLM) пакет, або реалізуєш репозиторій/runtime, що їх обробляє. Уточнено WP-05 (registry); код екстрактора — README SDK (WP-06).
---

# Пакет обробника Jane

Джерела правди: `contracts/schemas/package-manifest.schema.json`, `contracts/docs/handler-packages.md`,
`contracts/openapi/registry.v1.yaml`, ADR-0002/0003. Реалізація репозиторію — `services/registry/`
(README: публікація, перевірки, статуси, форки, експорт). Приклади маніфестів —
`contracts/examples/schemas/package-manifest/`.

## 1. Структура пакета
```text
jane-package.json        маніфест (обов'язково, у корені)
src/<module>/...         код Python (extractor, transform); entry.module відносно src/
schemas/*.schema.json    params, сутності (одна схема на entity_type), вихід LLM
prompts/*.md             інструкції та шаблон входу (llm)
rules.json               правила колектора (collector-rules), за collector-rules.schema.json
tests/<case>/...         вхід і очікуваний результат кожного тесту
```
Шляхи — ASCII `[A-Za-z0-9._/-]`, `/`, без `..`, без початкового `/`, без симлінків, без записів тек.
**Жодних секретів, токенів, cookie, `.env`, `*.pem`, паролів в URL** — registry відхилить
(`422 secret_detected`, значення не повертається). Підключення — лише `required_connections` (ім'я + kind).

## 2. Маніфест — мінімум
```json
{
  "schema_version": "1",
  "package_id": "shop-example.product-extractor",
  "version": "1.3.0",
  "kind": "extractor",
  "title": "Shop Example product cards",
  "entry": {"runtime": "python", "module": "product_extractor.main", "callable": "extract"},
  "input": {"accepts": ["material"], "media_types": ["text/html"]},
  "params_schema": "schemas/params.schema.json",
  "output": {"entities": [{"entity_type": "product", "schema": "schemas/product.schema.json", "key_fields": ["sku"]}]},
  "dependencies": {"runtime_profile": "python-extractor@1", "python": ["selectolax>=0.3,<0.4"]},
  "access": {"network": "none"},
  "tests": [
    {"name": "product-a100", "input": {"file": "tests/product-a100/page.html", "media_type": "text/html",
     "url": "https://shop.example.test/product/a-100"}, "expected_status": "success",
     "expected": "tests/product-a100/expected.json"},
    {"name": "category-empty", "input": {"file": "tests/category/page.html", "media_type": "text/html"},
     "expected_status": "empty"}
  ],
  "provenance": {"created_by": "llm", "based_on": {"package_id": "shop-example.product-extractor", "version": "1.2.0"},
                 "change_summary": "Support .price-new selector.",
                 "llm": {"model": "strong", "reason": "improvement"}},
  "bindings_hint": {"source_kinds": ["web"], "domains": ["shop.example.test"]}
}
```
`entry` за типом (registry перевіряє відповідність `kind ↔ entry`): extractor — `{runtime: python, module,
callable}` (файл `src/<module>.py` або `src/<module>/__init__.py` має бути в пакеті); transform — те саме або
`{executor, operation}`; storage — `{executor: storage, adapter, writes, format}`; llm — `{executor: llm,
instructions, output_schema, model}` (`model` — псевдонім `default|cheap|strong`); collector-rules —
`{collector: web|telegram, rules}`. Кожен файл, на який посилається маніфест (схеми, промпти, правила, входи й
`expected` тестів), має бути в пакеті.

## 3. Код екстрактора
Контракт коду, стани результату, контекст і тестові утиліти — [README SDK](../../../libs/extractor-sdk/README.md)
(`libs/extractor-sdk`, WP-06; runtime і CLI — `services/handler-runtime/README.md`). Коротко: `extract(material,
params, ctx)` повертає `success(...)`, `empty()` або `unrecognized(...)`; `failed` — виняток або рішення runtime;
без мережі, `subprocess`, запису поза `/tmp`, детерміновано; лише бібліотеки профілю runtime; пропущене поле ≠
очищення (`cleared`), `null` у `fields` заборонено.

## 4. Схеми
- `schemas/<entity>.schema.json` — JSON Schema 2020-12 полів сутності; `key_fields` **мають бути** в `required`
  (registry перевіряє).
- `schemas/params.schema.json` — параметри етапу (типові значення через `default`).
- Для llm — `schemas/output.schema.json`: модель відповідає лише за цією схемою.
- Registry перевіряє, що кожна схема — валідний JSON і валідна JSON Schema.

## 5. Тести (обов'язково)
- Щонайменше один `success` і один `empty` або `unrecognized` на пакет extractor/llm (інакше `422`,
  `errors[].code = tests_required`); імена тестів унікальні.
- `expected` — JSON `{"entities": [...]}` без `observation`/`provenance`; `compare: subset` — якщо
  допускаються зайві поля.
- Проблемний приклад, що спричинив нову версію, додається як тест із `origin: problem_sample`.
- Для llm — тест на ін'єкцію: вміст із «ignore previous instructions» дає звичайний результат (`empty`).
- Запуск без запису: `POST /v1/test-runs` (handler.v1) або CLI runtime на теці чи zip
  (`jane-handler-runtime test <пакет>`). Звіт прогону → `POST /v1/packages/{id}/versions/{v}/test-results`.

## 6. Залежності
- `dependencies.python` — PEP 508 з обмеженою версією, **лише** бібліотеки профілю `runtime_profile`
  (перелік публікує handler-runtime: `jane-handler-runtime profile` або `GET <runtime>/v1/info` →
  `capabilities.runtime_profiles`). Прямі URL заборонені; вимоги з маркером, хибним для Linux-пісочниці,
  ігноруються. Порушення — `422 dependency_not_allowed` з `pointer` на вимогу.
- `dependencies.python` без `runtime_profile` або невідомий профіль — теж `dependency_not_allowed`.
- `dependencies.packages` — точні версії інших пакетів registry (з `digest` — має збігтися).

## 7. Канонічний архів і дайджест
Дайджест версії — `sha256:` **канонічного zip** (registry і storage вже однакові; `build_archive` SDK має
перейти на stored — запит WP-05 до WP-06; README registry):
файли відсортовані за байтами шляху, без тек; метод **stored (без стиснення)**; час `1980-01-01 00:00:00`;
права `0o100644`, `create_system = 3`; без extra-полів і коментарів. Registry перепаковує будь-який
завантажений zip канонічно, тож дайджест залежить лише від шляхів і вмісту. Для JSON-публікації
`jane-package.json` = `json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"` (UTF-8, порядок ключів як у
запиті). Локально той самий дайджест: `jane-registry archive <тека> --out pkg.zip`.

## 8. Версії, походження, статуси
- SemVer: несумісна зміна полів/схеми виходу — major; нові поля/селектори — minor; виправлення — patch.
  Версія незмінна: повтор — `409 version_exists`; зміна = нова версія.
- Кожна нова версія: `provenance.based_on` = попередня; `created_by` = human | llm | import.
- Якщо `auto_changes_allowed = false` — версія з `created_by: llm` відхиляється `403 forbidden`; LLM лише
  пропонує diff людині.
- Статуси: нова версія — `draft`; `draft → approved | rejected | deprecated | yanked`, `approved → deprecated |
  yanked`, `deprecated → approved | yanked` (scope `registry:approve`). `yanked` — заборонено для нових
  прив'язок, архів доступний. Активація й відкат в етапі — оркестратор
  (`POST /v1/tasks/{task}/stages/{stage}/activations`).

## 9. Форки й перенесення змін
- Форк створює registry (`POST /v1/packages/{id}/forks`): копія файлів, у маніфесті змінено лише `package_id`,
  `version`, `fork_of` (батько, версія, дайджест) і `provenance.based_on`. Зміни батька форк не змінюють.
- Кожна наступна версія форку несе `fork_of` **без змін** (інакше `422`); не додавай `fork_of` у не-форк.
- Відмінності: `GET /diff?from=<v>|parent:<v>&to=...`; оновлення батька: `GET /upstream`.
- Перенесення змін батька — лише `POST /upstream-ports` за явною командою користувача (job `upstream_port`,
  трьохстороннє злиття). Конфлікт — job `failed`, `upstream_conflict`, `error.details.conflicts`; нічого не
  застосовано. Успіх — нова `draft`-версія з `provenance.upstream_port`.

## 10. Публікація
1. `POST /v1/packages` (якщо пакета ще немає) → `POST /v1/packages/{id}/versions` (zip або JSON
   `{manifest, files}`; `jane-package.json` не клади в `files`), заголовок `Idempotency-Key` (детермінований,
   наприклад від дайджесту тіла — повтор із тим самим тілом безпечний).
2. Версія з'являється як `draft`; прогін тестів → `POST …/test-results`.
3. Спільний пакет: перевір на всіх прив'язках (етапи завдань, що його використовують) або зроби форк.
4. `approved` — вручну або за політикою автоактивації.
5. Автономно: `jane-registry export <id>@<v> --registry <url> --out <тека>` (з `dependencies.packages`),
   офлайн-перевірка `jane-registry verify <zip>`; архів виконує handler-runtime (CLI або `package_archive`).

## Чекліст перед публікацією
- [ ] `jane-package.json` валідний за схемою; `package_id`/`kind` збігаються з пакетом; усі шляхи з маніфесту існують.
- [ ] Немає секретів і абсолютних шляхів; залежності — з профілю runtime.
- [ ] Тести `success` + `empty|unrecognized` проходять локально (CLI runtime).
- [ ] `provenance` заповнено; для форку — `fork_of` від registry без змін.
