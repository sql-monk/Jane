# Модуль `jane_handler_runtime.cli`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/cli.py](../../../../../services/handler-runtime/src/jane_handler_runtime/cli.py). Не редагуйте вручну.

Command line: run a package on a local file or run its tests without any other Jane service.

    jane-handler-runtime run  &lt;package dir|zip> &lt;file> [--media-type text/html] [--url URL] [--params JSON|@file]
    jane-handler-runtime test &lt;package dir|zip> [--case NAME ...] [--json]
    jane-handler-runtime profile [--json]
    jane-handler-runtime build-image [--profile python-extractor@1] [--tag jane/python-extractor:1]
    jane-handler-runtime serve                    # the HTTP service (same as python -m jane_handler_runtime)

Execution always happens in the sandbox backend from the settings (``docker`` by default). ``--backend subprocess --unsafe-no-sandbox`` runs trusted code without isolation (local development only). Exit codes: ``run`` 0 = success/empty, 1 = unrecognized/failed; ``test`` 0 = all passed, 1 = failures; 2 = the call could not be made (invalid package, params, no sandbox...).

## Функції

### Функція `main`

```python
def main(argv: Sequence[str] | None = None) -> int: ...
```

Код: [cli.py:222](../../../../../services/handler-runtime/src/jane_handler_runtime/cli.py#L222).
