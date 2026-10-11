# jane_handler_runtime.cli

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.cli.main](#jane_handler_runtimeclimain)

## jane_handler_runtime.cli.main

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/cli.py:222](../../../../../../services/handler-runtime/src/jane_handler_runtime/cli.py#L222).

```python
def main(argv: Sequence[str] | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `argv` | `Sequence[str] \| None` | `None` | positional-or-keyword |

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_units.py:115](../../../../../../services/handler-runtime/tests/test_units.py#L115).

```python
code = main(
        ["run", str(h.example), str(page), "--media-type", "text/html", "--url", "https://t.test/product/phone-alpha",
         "--backend", "subprocess", "--unsafe-no-sandbox", "-o", str(out)]
    )
```

Контекст і передумови: [services/handler-runtime/tests/test_units.py:122](../../../../../../services/handler-runtime/tests/test_units.py#L122).

```python
code = main(
        [
            "run",
            str(h.example),
            str(page),
            "--params",
            '{"default_currency": 1}',
            "--backend",
            "subprocess",
            "--unsafe-no-sandbox",
        ]
    )
```
