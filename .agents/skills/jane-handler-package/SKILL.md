---
name: jane-handler-package
description: Як скласти пакет обробника Jane (екстрактор, збереження, LLM, перетворення, правила колектора) — маніфест jane-package.json, схеми, тести, походження, форк, публікація в репозиторій. Використовуй, коли створюєш, змінюєш, тестуєш чи генеруєш (зокрема через LLM) пакет, або реалізуєш репозиторій/runtime, що їх обробляє. ЧЕРНЕТКА WP-00; уточнює WP-05, SDK — WP-06.
---

# Пакет обробника Jane (чернетка)

Джерела правди: `contracts/schemas/package-manifest.schema.json`, `contracts/docs/handler-packages.md`,
`contracts/openapi/registry.v1.yaml`, ADR-0002/0003. Приклади маніфестів —
`contracts/examples/schemas/package-manifest/`.

## 1. Структура архіву (zip)
```text
jane-package.json        маніфест (обов'язково)
src/<module>/...         код Python (extractor, transform)
schemas/*.schema.json    params, сутності (одна схема на entity_type), вихід LLM
prompts/*.md             інструкції та шаблон входу (llm)
rules.json               правила колектора (collector-rules)
tests/<case>/...         вхід і очікуваний результат кожного тесту
```
Шляхи відносні, `/`, без `..`, без симлінків. **Жодних секретів, токенів, cookie, .env** — registry
відхилить (`secret_detected`). Підключення — лише `required_connections` (ім'я + kind).

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
`entry` за типом: extractor/transform — `{runtime: python, module, callable}`; storage —
`{executor: storage, adapter, writes, format}`; llm — `{executor: llm, instructions, output_schema, model}`
(`model` — псевдонім `default|cheap|strong`); collector-rules — `{collector: web|telegram, rules}`.

## 3. Код екстрактора (контракт SDK — чернетка, фіналізує WP-06)
```python
def extract(material: dict, params: dict, ctx) -> dict:
    """material — Material (contracts/schemas/material.schema.json) з уже завантаженим вмістом:
    ctx.text() / ctx.bytes(); params — перевірені за params_schema; ctx.log — журнал."""
    return {
        "status": "success",  # success | empty | unrecognized  (failed — лише через виняток)
        "entities": [
            {
                "entity_type": "product",
                "key": {"scope": material["source"].get("source_id", "local"), "natural": {"sku": "A-100"}},
                "fields": {"sku": "A-100", "price": {"amount": 1299.0, "currency": "UAH"}},
            }
        ],
        "unrecognized": None,  # {"partial": true, "reason": "...", "signature": "missing-selector:.price"}
        "diagnostics": [
            {"level": "warning", "code": "extract.missing_selector", "message": "...", "selector": ".price"}
        ],
    }
```
Runtime сам додає `observation` (з матеріалу), `provenance` (пакет, виклик), валідує `fields` за
схемою сутності (`schema_mismatch` → `failed`), обмежує час/пам'ять/вихід, забороняє мережу.
Правила коду: детермінований (без поточного часу/випадковості в результаті), без мережі й файлів
поза `/tmp`, без `subprocess`, лише бібліотеки профілю runtime. Пропущене поле ≠ очищення: не
додавай поле, якого немає на сторінці; явне очищення — `cleared: ["field"]`. `null` у `fields` заборонено.

## 4. Схеми
- `schemas/<entity>.schema.json` — JSON Schema 2020-12 полів сутності; `key_fields` мають бути `required`.
- `schemas/params.schema.json` — параметри етапу (типові значення через `default`).
- Для llm — `schemas/output.schema.json`: модель відповідає лише за цією схемою.

## 5. Тести (обов'язково)
- Щонайменше один `success` і один `empty` або `unrecognized` на пакет extractor/llm.
- `expected` — JSON `{"entities": [...]}` без `observation`/`provenance`; `compare: subset` — якщо
  допускаються зайві поля.
- Проблемний приклад, що спричинив нову версію, додається як тест із `origin: problem_sample`.
- Для llm — тест на ін'єкцію: вміст із «ignore previous instructions» дає звичайний результат (`empty`).
- Запуск без запису: `POST /v1/test-runs` (handler.v1) або CLI runtime (WP-06) на локальній теці.

## 6. Версії, походження, форки
- SemVer: зміна полів/схеми виходу несумісно — major; нові поля/селектори — minor; виправлення — patch.
- Кожна нова версія: `provenance.based_on` = попередня; `created_by` = human | llm | import.
- Форк створює registry (`POST /v1/packages/{id}/forks`) і ставить `fork_of`; не змінюй `fork_of` руками.
  Перенесення змін батька — лише `POST /upstream-ports` за явною командою користувача.
- Якщо `auto_changes_allowed = false` — LLM не публікує нову версію, лише пропонує diff.

## 7. Публікація
1. `POST /v1/packages` (якщо пакета ще немає) → `POST /v1/packages/{id}/versions` (zip або JSON
   `{manifest, files}`), заголовок `Idempotency-Key`.
2. Версія з'являється як `draft`; прогін тестів → `POST …/test-results`.
3. Спільний пакет: перевір на всіх прив'язках (етапи завдань, що його використовують) або зроби форк.
4. `approved` — вручну або за політикою автоактивації; активація в етапі — оркестратор
   (`POST /v1/tasks/{task}/stages/{stage}/activations`), відкат — там само `kind: rollback`.

## Чекліст перед публікацією
- [ ] `jane-package.json` валідний за схемою; усі шляхи з маніфесту існують.
- [ ] Немає секретів і абсолютних шляхів; залежності — з профілю runtime.
- [ ] Тести `success` + `empty|unrecognized` проходять локально.
- [ ] `provenance` заповнено; для форку — `fork_of` від registry.
