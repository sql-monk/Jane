# Модуль `jane_registry.__main__`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/__main__.py](../../../../../services/registry/src/jane_registry/__main__.py). Не редагуйте вручну.

Entry point.

    jane-registry [serve]                                        # the HTTP service (python -m jane_registry)
    jane-registry export &lt;package_id>@&lt;version> --registry URL --out DIR [--no-dependencies] [--token-env VAR]
    jane-registry verify &lt;archive.zip> [--digest sha256:...]     # offline, no registry needed
    jane-registry archive &lt;package dir> --out FILE.zip           # canonical archive + digest of a local package

Exit codes: 0 - ok; 1 - verification failed; 2 - the command could not run.

## Функції

### Функція `main`

```python
def main(argv: Sequence[str] | None = None) -> int: ...
```

Код: [__main__.py:36](../../../../../services/registry/src/jane_registry/__main__.py#L36).
