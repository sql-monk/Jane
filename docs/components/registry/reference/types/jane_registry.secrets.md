# Модуль `jane_registry.secrets`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/secrets.py](../../../../../services/registry/src/jane_registry/secrets.py). Не редагуйте вручну.

Secret detection in package files (ADR-0002 §5, ADR-0006 §6): a finding rejects the publish with 422 ``secret_detected``.

Checks for every file of the package (including ``jane-package.json``):

1. **file names** that hold credentials by convention (``.env``, ``*.pem``, ``id_rsa``, ``.netrc``...);
2. **known formats** in any file: private key blocks (also split or escaped), AWS, GitHub, GitLab, Slack, Google, SendGrid, Stripe, Hugging Face, OpenAI/Anthropic-style ``sk-`` keys, Azure storage account keys and SAS signatures, Telegram bot tokens, JWTs, credentials inside URLs (``scheme://user:password@host``);
3. **authorization values** - a token after ``Bearer``/``Basic``/``token`` (``Authorization: Bearer …``);
4. **assignments** to secret-like names: quoted (``password = "..."``, ``"api_key": "..."``) in any file, unquoted (``password: …`` in YAML, ``password = …`` in INI/.env/.properties) in configuration files, ``Password=…;`` / ``Pwd=…;`` in connection strings anywhere;
5. **high-entropy tokens** (quoted strings and assigned values) in code/config files only - not in test inputs such as HTML pages, where base64 images and hashes are normal.

Decoding: UTF-8 (with replacement); files with a UTF-16 BOM, or with NUL bytes, are also decoded as UTF-16 and as Latin-1 so that NUL-padded or UTF-16 text cannot hide a secret. A file larger than ``secrets.max_scan_bytes_per_file`` is not accepted unscanned: :func:`oversized_files` lists them and the publish fails with ``limit_exceeded``.

Cost: every pattern is linear in the input (see the note at the patterns); a lower-case keyword pre-filter skips patterns that cannot match; the whole scan has a time budget ``secrets.scan_time_budget_ms`` (exceeded -> :class:`ScanBudgetExceeded` -> ``limit_exceeded``).

Findings never contain the matched value (it would leak the secret into responses and logs).

## Зміст

- [Клас `ScanBudgetExceeded`](#клас-scanbudgetexceeded)
- [Клас `SecretFinding`](#клас-secretfinding)
- [Функція `oversized_files`](#функція-oversized_files)
- [Функція `scan_files`](#функція-scan_files)

## Класи

### Клас `ScanBudgetExceeded`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.secrets` |
| Успадкування | `Exception` |
| Код | [secrets.py:57](../../../../../services/registry/src/jane_registry/secrets.py#L57) |

```python
class ScanBudgetExceeded(Exception): ...
```

Scanning took longer than ``secrets.scan_time_budget_ms`` (the publish is refused).

#### Конструктор `ScanBudgetExceeded.__init__`

```python
def __init__(self, budget_ms: int, path: str) -> None: ...
```

Код: [secrets.py:60](../../../../../services/registry/src/jane_registry/secrets.py#L60).

### Клас `SecretFinding`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.secrets` |
| Код | [secrets.py:46](../../../../../services/registry/src/jane_registry/secrets.py#L46) |

```python
@dataclass(frozen=True)
class SecretFinding: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `path` | `str` | — | читання |  |
| `code` | `str` | — | читання |  |
| `message` | `str` | — | читання |  |
| `line` | `int \| None` | `None` | читання |  |
| `pointer` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `oversized_files`

```python
def oversized_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[str]: ...
```

Files the scanner would not read completely (the publish must be refused).

Код: [secrets.py:456](../../../../../services/registry/src/jane_registry/secrets.py#L456).

### Функція `scan_files`

```python
def scan_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[SecretFinding]: ...
```

All findings, sorted by path and line. Callers reject :func:`oversized_files` first.

Raises :class:`ScanBudgetExceeded` when the whole scan takes longer than ``secrets.scan_time_budget_ms`` (checked between detectors and every few hundred matches - a safeguard on top of the linear patterns).

Винятки в коді функції: `ScanBudgetExceeded`.

Код: [secrets.py:461](../../../../../services/registry/src/jane_registry/secrets.py#L461).
