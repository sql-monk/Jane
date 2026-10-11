# Extractor SDK: експлуатація

## Перевірка змін

З кореня checkout:

```powershell
uv run --package jane-extractor-sdk pytest libs/extractor-sdk/tests/test_sdk.py
```

Для конкретного пакета запускайте manifest tests і sandbox tests Handler Runtime. Локальний success не підтверджує network isolation, budgets чи відповідність усіх сутностей схемі.

## Оновлення та відновлення

Оновлюйте SDK разом із пакетом або image Runtime. Зафіксуйте версії dependency, protocol і маніфесту. SDK не виконує міграцій даних; version/provenance результату визначає callable та Runtime.

Зберігайте вихідний пакет, manifest, schemas, tests, expected outputs і залежності. Після restart відновлення input/result належить caller.

## Діагностика

| Ознака | Причина або дія |
|---|---|
| `RuntimeError: material content is not available` | Blob не підготовлений; передайте loader |
| `error.stage=import` | Перевірте entry module/callable і залежності пакета |
| `error.stage=extract` | Виняток або недопустимий JSON/status |
| Немає context diagnostics у прямому result | Direct call повертає result; злиття `ctx.log` виконує runner |
| Відсутнє поле сутності | `entity` прибирає None; явне очищення — через `cleared` |
| Manifest tests не мають cases | `assert_package_tests_pass` піднімає AssertionError |
| Порушення audit hook | Перевірте network/process подію; isolation задає Runtime |

`ctx.log` створює повідомлення для HandlerResult, `print` runner відводить до stderr. SDK audit hook записує спроби мережі/процесів для діагностики й не встановлює sandbox сам.
