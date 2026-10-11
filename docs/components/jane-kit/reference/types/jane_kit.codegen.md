# Модуль `jane_kit.codegen`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/codegen.py](../../../../../libs/jane-kit/src/jane_kit/codegen.py). Не редагуйте вручну.

Generate typed clients from OpenAPI contracts.

    uv run jane-codegen client contracts/&lt;svc>/openapi.yaml --out services/&lt;me>/src/&lt;pkg>/_generated/&lt;svc>

writes a package with
  * ``models.py`` - Pydantic v2 models of ``components/schemas`` (datamodel-code-generator);
  * ``client.py`` - ``<Name>Client(ServiceClient)`` with one async method per ``operationId``;
    responses whose schema is a ``$ref`` to a component are parsed into that model.

Generated code goes into ``_generated/`` directories, which ruff and mypy skip. Regenerate instead of editing. CONNECTION POINT (WP-00): the contract locations are defined in ``contracts/``.

## Зміст

- [Функція `generate_client`](#функція-generate_client)
- [Функція `generate_client_source`](#функція-generate_client_source)
- [Функція `generate_models`](#функція-generate_models)
- [Функція `main`](#функція-main)

## Функції

### Функція `generate_client`

```python
def generate_client(
    spec_path: str | Path,
    out_dir: str | Path,
    class_name: str | None = None,
    with_models: bool = True,
) -> Path: ...
```

Код: [codegen.py:145](../../../../../libs/jane-kit/src/jane_kit/codegen.py#L145).

### Функція `generate_client_source`

```python
def generate_client_source(
    spec: OpenAPISpec,
    class_name: str,
    source: str,
    with_models: bool,
) -> str: ...
```

Код: [codegen.py:65](../../../../../libs/jane-kit/src/jane_kit/codegen.py#L65).

### Функція `generate_models`

```python
def generate_models(spec_path: Path, out_file: Path) -> None: ...
```

Pydantic v2 models via datamodel-code-generator (dev dependency; falls back to ``uvx``).

Винятки в коді функції: `RuntimeError`.

Код: [codegen.py:117](../../../../../libs/jane-kit/src/jane_kit/codegen.py#L117).

### Функція `main`

```python
def main(argv: list[str] | None = None) -> int: ...
```

Код: [codegen.py:172](../../../../../libs/jane-kit/src/jane_kit/codegen.py#L172).
