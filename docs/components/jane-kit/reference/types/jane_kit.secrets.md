# Модуль `jane_kit.secrets`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/secrets.py](../../../../../libs/jane-kit/src/jane_kit/secrets.py). Не редагуйте вручну.

Secret references of managed connections and allowlists of their destinations (ADR-0006, R17).

A connection decides *where* a resolved secret goes, and connections arrive through ``PUT /v1/connections/{id}``, so an executor (storage, llm, the collectors) restricts both ends with one policy:

* :class:`SecretPolicy` - ``env:VAR`` only for variables with the configured prefix (default ``JANE_SECRET_``; a name equal to the prefix or not a plain upper-case variable name is refused), ``file:<path>`` only for a file strictly inside the configured directory (default ``/run/secrets``; ``None`` disables files; the path is resolved first, so ``..`` and symlinks do not escape), ``vault:`` and anything else refused. Violations are ``FieldError`` with code ``secret_ref_not_allowed`` (``PUT`` -> 422); a connection stored bypassing the API gets no secrets when it is resolved.
* :func:`read_secret_file` - reads the resolved path through pinned filesystem objects (POSIX: directory descriptors and ``O_NOFOLLOW`` on every component; Windows: a non-delete-sharing handle per component, reparse points refused, final path checked), so a component swapped after the check is not followed (TOCTOU).
* :class:`HostAllowlist` - ``hostname`` (any port) or ``hostname:port`` entries; :func:`parse_host_port` - the strict ``hostname[:port]`` parser shared with the ``ContentRef`` reader's ``download_url`` allowlist.
* :class:`OriginAllowlist` - exact ``http(s)://host[:port]`` origins (default ports normalized); a checked URL may have a path, never userinfo, backslashes or whitespace.

## Зміст

- [Клас `HostAllowlist`](#клас-hostallowlist)
- [Клас `OriginAllowlist`](#клас-originallowlist)
- [Клас `SecretPolicy`](#клас-secretpolicy)
- [Функція `parse_host_port`](#функція-parse_host_port)
- [Функція `read_secret_file`](#функція-read_secret_file)

## Класи

### Клас `HostAllowlist`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.secrets` |
| Код | [secrets.py:67](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L67) |

```python
@dataclass(frozen=True)
class HostAllowlist: ...
```

``hostname`` entries allow any port, ``hostname:port`` entries only that port; an invalid entry raises ``ValueError`` (a typo in the setting stops the service at start).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `entries` | `tuple[str, ...]` | `()` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `HostAllowlist.of`

```python
@classmethod
def of(cls, entries: Iterable[str]) -> HostAllowlist: ...
```

Код: [secrets.py:84](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L84).

#### Метод `HostAllowlist.allows`

```python
def allows(self, host: str, port: int | None) -> bool: ...
```

``port=None`` (not known) matches only ``hostname`` entries.

Код: [secrets.py:87](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L87).

### Клас `OriginAllowlist`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.secrets` |
| Код | [secrets.py:114](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L114) |

```python
@dataclass(frozen=True)
class OriginAllowlist: ...
```

Exact ``http(s)://host[:port]`` origins; an entry with a path, userinfo or another scheme raises ``ValueError``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `entries` | `tuple[str, ...]` | `()` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `OriginAllowlist.of`

```python
@classmethod
def of(cls, entries: Iterable[str]) -> OriginAllowlist: ...
```

Код: [secrets.py:128](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L128).

#### Метод `OriginAllowlist.allows`

```python
def allows(self, url: object) -> bool: ...
```

The origin of ``url`` (path allowed; userinfo, backslash, whitespace refused) is on the list.

Код: [secrets.py:131](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L131).

### Клас `SecretPolicy`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.secrets` |
| Код | [secrets.py:141](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L141) |

```python
@dataclass(frozen=True)
class SecretPolicy: ...
```

Bounds of ``secret_refs`` (see the module docstring).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `env_prefix` | `str` | `'JANE_SECRET_'` | читання |  |
| `files_dir` | `Path \| None` | `Path('/run/secrets')` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `SecretPolicy.secret_file`

```python
def secret_file(self, ref: str) -> Path | None: ...
```

Resolved path (``..`` and symlinks resolved) of an allowed ``file:`` reference, else ``None``.

The reader must still pin every component (:func:`read_secret_file`): resolving a pathname alone does not prevent a later replacement of the target or a parent directory.

Код: [secrets.py:147](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L147).

#### Метод `SecretPolicy.ref_error`

```python
def ref_error(self, ref: str) -> str | None: ...
```

Why a secret reference is not allowed (``None`` if allowed).

Код: [secrets.py:167](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L167).

#### Метод `SecretPolicy.violations`

```python
def violations(self, refs: object, pointer: str = '/secret_refs') -> list[FieldError]: ...
```

``FieldError`` (code ``secret_ref_not_allowed``) for every reference of ``refs`` that is not allowed.

Код: [secrets.py:189](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L189).

#### Метод `SecretPolicy.resolve`

```python
def resolve(self, ref: str, environ: Mapping[str, str] | None = None) -> str | None: ...
```

Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing, empty or not allowed.

Код: [secrets.py:201](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L201).

## Функції

### Функція `parse_host_port`

```python
def parse_host_port(value: object) -> tuple[str, int | None] | None: ...
```

Strict ``hostname[:port]`` -> ``(lower-case host, port)``; anything else (userinfo, IPv6 literal, trailing dot, path, whitespace, port outside 1..65535) -> ``None``.

Код: [secrets.py:52](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L52).

### Функція `read_secret_file`

```python
def read_secret_file(path: Path) -> str | None: ...
```

Text of the resolved secret ``path`` (stripped; ``None`` if empty). Fails closed (``None``) on a changed component, a non-regular file or an unsupported platform; validation precedes reading any secret bytes.

Код: [secrets.py:213](../../../../../libs/jane-kit/src/jane_kit/secrets.py#L213).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `SECRET_REF_NOT_ALLOWED` | — | `'secret_ref_not_allowed'` |  |
