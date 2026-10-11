# jane_registry.__main__

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.__main__.main](#jane_registry__main__main)

## jane_registry.__main__.main

**Функція.** Код: [services/registry/src/jane_registry/__main__.py:36](../../../../../../services/registry/src/jane_registry/__main__.py#L36).

```python
def main(argv: Sequence[str] | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `argv` | `Sequence[str] \| None` | `None` | positional-or-keyword |

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_export.py:140](../../../../../../services/registry/tests/test_export.py#L140).

```python
assert main(["verify", str(archive)]) == 0
```

Контекст і передумови: [services/registry/tests/test_export.py:149](../../../../../../services/registry/tests/test_export.py#L149).

```python
assert main(["verify", str(out / f"{rules_id}-1.0.0.zip")]) == 0
```
