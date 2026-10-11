# jane_kit.secrets

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.secrets.SECRET_REF_NOT_ALLOWED](#jane_kitsecretssecret_ref_not_allowed)
- [jane_kit.secrets.parse_host_port](#jane_kitsecretsparse_host_port)
- [jane_kit.secrets.HostAllowlist](#jane_kitsecretshostallowlist)
- [jane_kit.secrets.HostAllowlist.__init__](#jane_kitsecretshostallowlist__init__)
- [jane_kit.secrets.HostAllowlist.entries](#jane_kitsecretshostallowlistentries)
- [jane_kit.secrets.HostAllowlist.of](#jane_kitsecretshostallowlistof)
- [jane_kit.secrets.HostAllowlist.allows](#jane_kitsecretshostallowlistallows)
- [jane_kit.secrets.OriginAllowlist](#jane_kitsecretsoriginallowlist)
- [jane_kit.secrets.OriginAllowlist.__init__](#jane_kitsecretsoriginallowlist__init__)
- [jane_kit.secrets.OriginAllowlist.entries](#jane_kitsecretsoriginallowlistentries)
- [jane_kit.secrets.OriginAllowlist.of](#jane_kitsecretsoriginallowlistof)
- [jane_kit.secrets.OriginAllowlist.allows](#jane_kitsecretsoriginallowlistallows)
- [jane_kit.secrets.OriginAllowlist.__str__](#jane_kitsecretsoriginallowlist__str__)
- [jane_kit.secrets.SecretPolicy](#jane_kitsecretssecretpolicy)
- [jane_kit.secrets.SecretPolicy.__init__](#jane_kitsecretssecretpolicy__init__)
- [jane_kit.secrets.SecretPolicy.env_prefix](#jane_kitsecretssecretpolicyenv_prefix)
- [jane_kit.secrets.SecretPolicy.files_dir](#jane_kitsecretssecretpolicyfiles_dir)
- [jane_kit.secrets.SecretPolicy.secret_file](#jane_kitsecretssecretpolicysecret_file)
- [jane_kit.secrets.SecretPolicy.ref_error](#jane_kitsecretssecretpolicyref_error)
- [jane_kit.secrets.SecretPolicy.violations](#jane_kitsecretssecretpolicyviolations)
- [jane_kit.secrets.SecretPolicy.resolve](#jane_kitsecretssecretpolicyresolve)
- [jane_kit.secrets.read_secret_file](#jane_kitsecretsread_secret_file)

## jane_kit.secrets.SECRET_REF_NOT_ALLOWED

**Константа.** Код: [libs/jane-kit/src/jane_kit/secrets.py:44](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L44).

```python
SECRET_REF_NOT_ALLOWED = 'secret_ref_not_allowed'
```

## jane_kit.secrets.parse_host_port

**Функція.** Код: [libs/jane-kit/src/jane_kit/secrets.py:52](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L52).

```python
def parse_host_port(value: object) -> tuple[str, int | None] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `object` | `—` | positional-or-keyword |

Результат: `tuple[str, int | None] | None`.

### Опис із вихідного коду

```text
Strict ``hostname[:port]`` -> ``(lower-case host, port)``; anything else (userinfo, IPv6 literal, trailing
dot, path, whitespace, port outside 1..65535) -> ``None``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:77](../../../../../../libs/jane-kit/tests/test_secrets.py#L77).

```python
assert parse_host_port("Postgres:5432") == ("postgres", 5432)
```

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:78](../../../../../../libs/jane-kit/tests/test_secrets.py#L78).

```python
assert parse_host_port("minio") == ("minio", None)
```

## jane_kit.secrets.HostAllowlist

**Клас.** Код: [libs/jane-kit/src/jane_kit/secrets.py:67](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L67).

```python
class HostAllowlist:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [entries](jane_kit.secrets.md#jane_kitsecretshostallowlistentries) | Поле | ні |
| [of](jane_kit.secrets.md#jane_kitsecretshostallowlistof) | Метод | ні |
| [allows](jane_kit.secrets.md#jane_kitsecretshostallowlistallows) | Метод | ні |
| [__init__](jane_kit.secrets.md#jane_kitsecretshostallowlist__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
``hostname`` entries allow any port, ``hostname:port`` entries only that port; an invalid entry raises
``ValueError`` (a typo in the setting stops the service at start).
```

## jane_kit.secrets.HostAllowlist.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/secrets.py:67](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L67).

```python
def __init__(self, entries: tuple[str, ...] = ()) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `entries` | `tuple[str, ...]` | `()` | positional-or-keyword |

Результат: `None`.

## jane_kit.secrets.HostAllowlist.entries

**Поле.** Код: [libs/jane-kit/src/jane_kit/secrets.py:71](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L71).

```python
entries: tuple[str, ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_kit.secrets.HostAllowlist.of

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:84](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L84).

```python
def of(cls, entries: Iterable[str]) -> HostAllowlist:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `entries` | `Iterable[str]` | `—` | positional-or-keyword |

Результат: `HostAllowlist`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:81](../../../../../../libs/jane-kit/tests/test_secrets.py#L81).

```python
allow = HostAllowlist.of(["postgres:5432", "minio"])
```

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:85](../../../../../../libs/jane-kit/tests/test_secrets.py#L85).

```python
HostAllowlist.of(["http://x"])
```

## jane_kit.secrets.HostAllowlist.allows

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:87](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L87).

```python
def allows(self, host: str, port: int | None) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `port` | `int \| None` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
``port=None`` (not known) matches only ``hostname`` entries.
```

## jane_kit.secrets.OriginAllowlist

**Клас.** Код: [libs/jane-kit/src/jane_kit/secrets.py:114](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L114).

```python
class OriginAllowlist:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [entries](jane_kit.secrets.md#jane_kitsecretsoriginallowlistentries) | Поле | ні |
| [of](jane_kit.secrets.md#jane_kitsecretsoriginallowlistof) | Метод | ні |
| [allows](jane_kit.secrets.md#jane_kitsecretsoriginallowlistallows) | Метод | ні |
| [__str__](jane_kit.secrets.md#jane_kitsecretsoriginallowlist__str__) | Метод | ні |
| [__init__](jane_kit.secrets.md#jane_kitsecretsoriginallowlist__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Exact ``http(s)://host[:port]`` origins; an entry with a path, userinfo or another scheme raises
``ValueError``.
```

## jane_kit.secrets.OriginAllowlist.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/secrets.py:114](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L114).

```python
def __init__(self, entries: tuple[str, ...] = ()) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `entries` | `tuple[str, ...]` | `()` | positional-or-keyword |

Результат: `None`.

## jane_kit.secrets.OriginAllowlist.entries

**Поле.** Код: [libs/jane-kit/src/jane_kit/secrets.py:118](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L118).

```python
entries: tuple[str, ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_kit.secrets.OriginAllowlist.of

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:128](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L128).

```python
def of(cls, entries: Iterable[str]) -> OriginAllowlist:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `entries` | `Iterable[str]` | `—` | positional-or-keyword |

Результат: `OriginAllowlist`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:89](../../../../../../libs/jane-kit/tests/test_secrets.py#L89).

```python
allow = OriginAllowlist.of(["https://api.anthropic.com", "http://fake-llm:8080/"])
```

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:104](../../../../../../libs/jane-kit/tests/test_secrets.py#L104).

```python
OriginAllowlist.of(["https://api.openai.com/v1"])
```

## jane_kit.secrets.OriginAllowlist.allows

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:131](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L131).

```python
def allows(self, url: object) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `object` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
The origin of ``url`` (path allowed; userinfo, backslash, whitespace refused) is on the list.
```

## jane_kit.secrets.OriginAllowlist.__str__

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:136](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L136).

```python
def __str__(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

## jane_kit.secrets.SecretPolicy

**Клас.** Код: [libs/jane-kit/src/jane_kit/secrets.py:141](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L141).

```python
class SecretPolicy:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [env_prefix](jane_kit.secrets.md#jane_kitsecretssecretpolicyenv_prefix) | Поле | ні |
| [files_dir](jane_kit.secrets.md#jane_kitsecretssecretpolicyfiles_dir) | Поле | ні |
| [secret_file](jane_kit.secrets.md#jane_kitsecretssecretpolicysecret_file) | Метод | ні |
| [ref_error](jane_kit.secrets.md#jane_kitsecretssecretpolicyref_error) | Метод | ні |
| [violations](jane_kit.secrets.md#jane_kitsecretssecretpolicyviolations) | Метод | ні |
| [resolve](jane_kit.secrets.md#jane_kitsecretssecretpolicyresolve) | Метод | ні |
| [__init__](jane_kit.secrets.md#jane_kitsecretssecretpolicy__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Bounds of ``secret_refs`` (see the module docstring).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:32](../../../../../../libs/jane-kit/tests/test_secret_files.py#L32).

```python
policy = SecretPolicy(files_dir=secrets_dir)
```

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:94](../../../../../../libs/jane-kit/tests/test_secret_files.py#L94).

```python
policy = SecretPolicy(files_dir=secrets_dir)
```

## jane_kit.secrets.SecretPolicy.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/secrets.py:141](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L141).

```python
def __init__(self, env_prefix: str = 'JANE_SECRET_', files_dir: Path | None = Path('/run/secrets')) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `env_prefix` | `str` | `'JANE_SECRET_'` | positional-or-keyword |
| `files_dir` | `Path \| None` | `Path('/run/secrets')` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:32](../../../../../../libs/jane-kit/tests/test_secret_files.py#L32).

```python
policy = SecretPolicy(files_dir=secrets_dir)
```

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:94](../../../../../../libs/jane-kit/tests/test_secret_files.py#L94).

```python
policy = SecretPolicy(files_dir=secrets_dir)
```

## jane_kit.secrets.SecretPolicy.env_prefix

**Поле.** Код: [libs/jane-kit/src/jane_kit/secrets.py:144](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L144).

```python
env_prefix: str = 'JANE_SECRET_'
```

Доступ: читання — так; запис — ні.

## jane_kit.secrets.SecretPolicy.files_dir

**Поле.** Код: [libs/jane-kit/src/jane_kit/secrets.py:145](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L145).

```python
files_dir: Path | None = Path('/run/secrets')
```

Доступ: читання — так; запис — ні.

## jane_kit.secrets.SecretPolicy.secret_file

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:147](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L147).

```python
def secret_file(self, ref: str) -> Path | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |

Результат: `Path | None`.

### Опис із вихідного коду

```text
Resolved path (``..`` and symlinks resolved) of an allowed ``file:`` reference, else ``None``.

The reader must still pin every component (:func:`read_secret_file`): resolving a pathname alone does
not prevent a later replacement of the target or a parent directory.
```

## jane_kit.secrets.SecretPolicy.ref_error

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:167](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L167).

```python
def ref_error(self, ref: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Why a secret reference is not allowed (``None`` if allowed).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:33](../../../../../../libs/jane-kit/tests/test_secret_files.py#L33).

```python
assert policy.ref_error(f"file:{link}") is None
```

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:96](../../../../../../libs/jane-kit/tests/test_secret_files.py#L96).

```python
assert policy.ref_error(nul) is not None and policy.resolve(nul) is None
```

## jane_kit.secrets.SecretPolicy.violations

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:189](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L189).

```python
def violations(self, refs: object, pointer: str='/secret_refs') -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `refs` | `object` | `—` | positional-or-keyword |
| `pointer` | `str` | `'/secret_refs'` | positional-or-keyword |

Результат: `list[FieldError]`.

### Опис із вихідного коду

```text
``FieldError`` (code ``secret_ref_not_allowed``) for every reference of ``refs`` that is not allowed.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:56](../../../../../../libs/jane-kit/tests/test_secrets.py#L56).

```python
errors = policy.violations({"a": f"file:{secrets_dir / 'pg'}", "b": "env:PATH"})
```

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:58](../../../../../../libs/jane-kit/tests/test_secrets.py#L58).

```python
assert [e.pointer for e in policy.violations(["x"])] == ["/secret_refs"]
```

## jane_kit.secrets.SecretPolicy.resolve

**Метод.** Код: [libs/jane-kit/src/jane_kit/secrets.py:201](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L201).

```python
def resolve(self, ref: str, environ: Mapping[str, str] | None=None) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |
| `environ` | `Mapping[str, str] \| None` | `None` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing, empty or not allowed.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:34](../../../../../../libs/jane-kit/tests/test_secret_files.py#L34).

```python
assert policy.resolve(f"file:{link}") == "inside-secret"
```

Контекст і передумови: [libs/jane-kit/tests/test_secret_files.py:97](../../../../../../libs/jane-kit/tests/test_secret_files.py#L97).

```python
assert policy.resolve(f"file:{secrets_dir / 'binary'}") is None
```

## jane_kit.secrets.read_secret_file

**Функція.** Код: [libs/jane-kit/src/jane_kit/secrets.py:213](../../../../../../libs/jane-kit/src/jane_kit/secrets.py#L213).

```python
def read_secret_file(path: Path) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `Path` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Text of the resolved secret ``path`` (stripped; ``None`` if empty). Fails closed (``None``) on a changed
component, a non-regular file or an unsupported platform; validation precedes reading any secret bytes.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_secrets.py:73](../../../../../../libs/jane-kit/tests/test_secrets.py#L73).

```python
assert read_secret_file(link) is None
```
