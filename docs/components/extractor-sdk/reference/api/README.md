# Extractor SDK: контракт виконання

HTTP API належить [Handler Runtime](../../../handler-runtime/reference/api/README.md). SDK визначає Python callable і протокол файлів runner.

## Callable

```python
def extract(material, params, ctx):
    ...
```

Повертає JSON Mapping зі status `success`, `empty` або `unrecognized`. Raise означає failure. [Публічні helpers](../types/README.md) формують результат.

## Протокол runner

`request.json` у workdir містить `protocol=1`, `entry.module`, `entry.callable`, `package_dir`, `params`, `test_mode`, `inputs`; кожен input має `input` і необов’язковий `content_file`. Відповідь у stdout містить один JSON із `protocol`, `results`, `violations`, `metrics`.

CLI потребує рівно один argument workdir: неправильна кількість → exit 2; неправильний request або protocol → exit 3; результати виконання → exit 0, навіть якщо callable має error.

## Гарантії

Порядок results відповідає inputs. Exception містить type, message, traceback та stage. Runner перенаправляє user stdout до stderr. Шляхи та sandbox межі мають підготувати Runtime; local testing виконує довірений код у процесі.

Джерело: [runner.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/runner.py).
