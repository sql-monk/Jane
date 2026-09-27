# jane-extractor-sdk

SDK для авторів Python-екстракторів Jane: типи й помічники результату, контекст виконання, раннер пісочниці
(протокол runtime ↔ пісочниця), утиліти пакета й тестів. Лише стандартна бібліотека — SDK встановлено в образ
профілю `python-extractor@1`. Виконує пакети [handler-runtime](../../services/handler-runtime/README.md).
Структура пакета й маніфест — [`contracts/docs/handler-packages.md`](../../contracts/docs/handler-packages.md),
скіл `jane-handler-package`.

## Як написати екстрактор

```python
from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

def extract(material: Material, params: dict, ctx: Context) -> ExtractResult:
    html = ctx.text()                      # вміст (inline чи blob) уже завантажено й перевірено runtime
    if "product" not in html:
        return empty()                     # коректна відсутність сутностей
    sku, price = parse(html)
    if price is None:
        ctx.log.warning("price not found", code="extract.missing_selector", selector=".price")
        return unrecognized("no price", signature="missing-selector:.price",
                            entities=[entity("product", {"sku": sku})])   # partial = True
    return success([entity("product", {"sku": sku, "price": {"amount": price, "currency": "UAH"}})])
```

Маніфест: `"entry": {"runtime": "python", "module": "<модуль у src/>", "callable": "extract"}`,
`"dependencies": {"runtime_profile": "python-extractor@1", "python": ["lxml>=6"]}` — лише бібліотеки профілю
(перелік — README handler-runtime або `jane-handler-runtime profile`).

| Стан ТЗ §9 | Як отримати |
|---|---|
| `success` | `success(entities)` (transform — `success(data=...)`) |
| `empty` | `empty()` |
| `unrecognized` | `unrecognized(reason, signature=..., entities=[...])` — з сутностями це `partial: true` |
| `failed` | підняти виняток; або його ставить runtime (невідповідність схемі, тайм-аут, пам'ять, мережа) |

Правила:
- `entity(type, fields)` відкидає поля зі значенням `None`: відсутнє на сторінці поле **не** передається
  (пропуск ≠ видалення); явне очищення — `cleared=["field"]`. `null` у `fields` → `schema_mismatch`.
- `key` можна не задавати: runtime збудує його з `key_fields` маніфесту (scope — `source.source_id` або `local`).
  `observation`, `provenance`, `schema` додає runtime.
- Діагностика — `ctx.log.info/warning/error(message, code=..., selector=...)`; `print` потрапляє лише в журнал.
- Без мережі (її немає в пісочниці; спроба → `sandbox_violation`), без `subprocess`, без запису поза `/tmp`,
  детермінований результат (без поточного часу чи випадковості).
- Параметри вже перевірені за `params_schema`, типові значення (`default`) підставлено.

## Модулі

| Модуль | Що дає |
|---|---|
| `jane_extractor_sdk` | `success`, `empty`, `unrecognized`, `entity`, `Context`, типи `Material`, `ExtractResult`, `EntityOut`, `Diagnostic` |
| `jane_extractor_sdk.context` | `Context` (`bytes()`, `text()`, `charset()`, `log`, `params`, `test_mode`) |
| `jane_extractor_sdk.runner` | раннер у пісочниці: `python -I -m jane_extractor_sdk.runner <workdir>`, протокол v1 (опис — docstring модуля), аудит-хук спроб мережі/процесів |
| `jane_extractor_sdk.package` | `build_archive` (канонічний zip: сортування, фіксовані час і права), `digest_of`, `safe_unpack` (шляхи, симлінки, ліміти), `load_manifest`, `material_from_file/bytes`, `case_input` (вхід тесту маніфесту) |
| `jane_extractor_sdk.entities` | `to_entity_record`, `build_key`, `observation_of` — спільні з runtime |
| `jane_extractor_sdk.compare` | `compare_output(expected, actual, "exact" | "subset")` → `differences` з JSON Pointer; ігнорує `observation`, `provenance`, `schema` |
| `jane_extractor_sdk.testing` | `run_local`, `run_package_tests`, `assert_package_tests_pass`, `apply_param_defaults` |

## Тестові утиліти

Швидкий цикл у pytest — у поточному процесі, **без пісочниці й без перевірки схем** (лише для власного
довіреного коду):

```python
from pathlib import Path
from jane_extractor_sdk.testing import assert_package_tests_pass, run_local

PKG = Path(__file__).parents[1]

def test_manifest_tests():
    assert_package_tests_pass(PKG)          # tests маніфесту: статус + expected (exact/subset)

def test_one_page():
    assert run_local(PKG, file=PKG / "tests/p/page.html", media_type="text/html")["status"] == "success"
```

Остаточна перевірка — у пісочниці, зі схемами, без інших сервісів:

```
uv run --package jane-handler-runtime jane-handler-runtime test path/to/package
```

## Приклад пакета

[`examples/testsite-product-extractor`](examples/testsite-product-extractor) — картки товарів тестового сайту
(`tests/fixtures/testsite`): JSON-LD із запасним варіантом на мікроданих, `params_schema` з типовими значеннями,
схема сутності `product` (`key_fields: ["sku"]`), п'ять тестів: `success` (exact і subset), два `empty` (файл і
Material JSON з `content_file`), `unrecognized` (сторінка товару без ціни, `origin: problem_sample`).

## Тести SDK

```
just test extractor-sdk
```
