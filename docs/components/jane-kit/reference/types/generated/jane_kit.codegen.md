# jane_kit.codegen

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.codegen.generate_client_source](#jane_kitcodegengenerate_client_source)
- [jane_kit.codegen.generate_models](#jane_kitcodegengenerate_models)
- [jane_kit.codegen.generate_client](#jane_kitcodegengenerate_client)
- [jane_kit.codegen.main](#jane_kitcodegenmain)

## jane_kit.codegen.generate_client_source

**Функція.** Код: [libs/jane-kit/src/jane_kit/codegen.py:65](../../../../../../libs/jane-kit/src/jane_kit/codegen.py#L65).

```python
def generate_client_source(spec: OpenAPISpec, class_name: str, source: str, with_models: bool) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `spec` | `OpenAPISpec` | `—` | positional-or-keyword |
| `class_name` | `str` | `—` | positional-or-keyword |
| `source` | `str` | `—` | positional-or-keyword |
| `with_models` | `bool` | `—` | positional-or-keyword |

Результат: `str`.

## jane_kit.codegen.generate_models

**Функція.** Код: [libs/jane-kit/src/jane_kit/codegen.py:117](../../../../../../libs/jane-kit/src/jane_kit/codegen.py#L117).

```python
def generate_models(spec_path: Path, out_file: Path) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `spec_path` | `Path` | `—` | positional-or-keyword |
| `out_file` | `Path` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `RuntimeError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Pydantic v2 models via datamodel-code-generator (dev dependency; falls back to ``uvx``).
```

## jane_kit.codegen.generate_client

**Функція.** Код: [libs/jane-kit/src/jane_kit/codegen.py:145](../../../../../../libs/jane-kit/src/jane_kit/codegen.py#L145).

```python
def generate_client(spec_path: str | Path, out_dir: str | Path, class_name: str | None=None, with_models: bool=True) -> Path:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `spec_path` | `str \| Path` | `—` | positional-or-keyword |
| `out_dir` | `str \| Path` | `—` | positional-or-keyword |
| `class_name` | `str \| None` | `None` | positional-or-keyword |
| `with_models` | `bool` | `True` | positional-or-keyword |

Результат: `Path`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_codegen.py:21](../../../../../../libs/jane-kit/tests/test_codegen.py#L21).

```python
out = generate_client(DATA / "openapi.yaml", tmp_path / "sample_client")
```

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:191](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L191).

```python
generate_client(spec_path, tmp_path / "collector_client", class_name="Collector", with_models=False)
```

## jane_kit.codegen.main

**Функція.** Код: [libs/jane-kit/src/jane_kit/codegen.py:172](../../../../../../libs/jane-kit/src/jane_kit/codegen.py#L172).

```python
def main(argv: list[str] | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `argv` | `list[str] \| None` | `None` | positional-or-keyword |

Результат: `int`.
