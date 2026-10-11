# Extractor SDK: швидкий старт

Напишіть і викличте екстрактор у власному процесі.

## Встановлення

Python 3.12+, uv, checkout Jane; команди з кореня.

```powershell
uv sync --package jane-extractor-sdk
```

Збережіть `demo_extract.py` у корені:

```python
from jane_extractor_sdk import Context, entity, success

def extract(material, params, ctx):
    title = ctx.text().strip()
    ctx.log.info("Назву прочитано")
    return success([entity("note", {"title": title})])

material = {
    "material_id": "demo-note",
    "content": {"kind": "inline", "encoding": "utf-8", "data": "Jane"},
}
result = extract(material, {}, Context(material))
assert result["status"] == "success"
assert result["entities"][0]["fields"] == {"title": "Jane"}
print(result)
```

```powershell
uv run --package jane-extractor-sdk python demo_extract.py
```

Очікувані поля:

```json
{"status": "success", "entities": [{"entity_type": "note", "fields": {"title": "Jane"}}]}
```

Це бібліотечний виклик; для формування повного `EntityRecord` зі спостереженням використовуйте пакет і runner.

## Готовий локальний пакет

```powershell
uv run --package jane-extractor-sdk python -c "from pathlib import Path; from jane_extractor_sdk.testing import assert_package_tests_pass; assert_package_tests_pass(Path('libs/extractor-sdk/examples/testsite-product-extractor')); print('package tests passed')"
```

Для цього прикладу додатково потрібні parser-залежності пакета; вони є в workspace. Локальний runner виконує довірений код у поточному процесі. Для sandbox-перевірки — [Handler Runtime](../handler-runtime/README.md).
