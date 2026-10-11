# Extractor SDK: публічні типи

## Індекс

- [`jane_extractor_sdk.context`](generated/jane_extractor_sdk.context.md)
- [`jane_extractor_sdk.result`](generated/jane_extractor_sdk.result.md)
- [`jane_extractor_sdk.types`](generated/jane_extractor_sdk.types.md)
- [`jane_extractor_sdk.testing`](generated/jane_extractor_sdk.testing.md)
- [`jane_extractor_sdk.runner`](generated/jane_extractor_sdk.runner.md)
- [`jane_extractor_sdk.package`](generated/jane_extractor_sdk.package.md)
- [`jane_extractor_sdk.entities`](generated/jane_extractor_sdk.entities.md)
- [`jane_extractor_sdk.compare`](generated/jane_extractor_sdk.compare.md)

## Основні члени

| Член | Результат і помилки |
|---|---|
| `Context.bytes()` | Кешовані bytes; RuntimeError для blob без loader |
| `Context.text(errors="replace")` | str, декодування за charset |
| `Context.charset()` | Перше відоме кодування content/format або UTF-8 |
| `DiagnosticsLog.add/debug/info/warning/error` | Додають message; повертають None |
| `entity` | EntityOut; None fields пропускаються, `cleared` явне |
| `success` | ExtractResult із entities і необов’язковим data |
| `empty` | ExtractResult із порожнім entities |
| `unrecognized` | Reason/signature та partial entities |
| `run_local` | Спрощений result; ValueError, якщо не задані input/file |
| `run_package_tests` | Список LocalCaseResult |
| `assert_package_tests_pass` | None або AssertionError |

`Context.material`, `params`, `test_mode`, `log` — instance attributes; `DiagnosticsLog.messages` — mutable list. Публічні TypedDict описують форму без примусової runtime validation. Всі сигнатури, bases та поля — у generated сторінках.

## Приклади

[Мінімальний callable](../../quickstart.md), [запуск пакета](../../integration.md), [параметри Context](../../configuration.md).
