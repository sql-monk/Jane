# Extractor SDK: параметри та обмеження

SDK не читає змінні середовища й не має сервісного порту. Параметри надходять у функції та `Context`.

## Context

| Аргумент | Типове значення | Значення |
|---|---|---|
| `material` | Обов’язковий Mapping | Матеріал або input callable |
| `params` | `None` → порожній Mapping | Параметри екстрактора |
| `content_loader` | `None` | Callback bytes для підготовленого blob |
| `test_mode` | `False` | Ознака тестового виконання |

`text(errors="replace")` декодує з charset content, далі format, далі UTF-8; невідомий charset пропускається. `bytes()` кешує вміст. Blob без loader викликає RuntimeError.

## Локальні тести

`run_local` типово має `test_mode=True`. `apply_param_defaults` переносить тільки top-level defaults params schema; це не повна schema validation. `run_package_tests` дозволяє вибрати `names`; compare — `exact` чи `subset` із маніфесту.

## Runner

Протокол — `1`; `package_dir` типово `package`; `params` та `inputs` типово порожні; `test_mode` приводиться до bool. Runner записує до 50 порушень audit hook; traceback обрізається до 8000 символів. Це внутрішні константи діагностики, а не sandbox policy.

## Ліміти виконання

CPU, пам’ять, час, мережа, процеси й розмір відповіді задаються [Handler Runtime](../handler-runtime/configuration.md). Локальний `run_local` їх не застосовує. `test_mode` інформує callable; сам SDK не блокує запис до файлів.
