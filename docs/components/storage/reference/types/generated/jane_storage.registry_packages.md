# jane_storage.registry_packages

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.registry_packages.digest_mismatch](#jane_storageregistry_packagesdigest_mismatch)
- [jane_storage.registry_packages.check_ref](#jane_storageregistry_packagescheck_ref)
- [jane_storage.registry_packages.RegistryPackages](#jane_storageregistry_packagesregistrypackages)
- [jane_storage.registry_packages.RegistryPackages.__init__](#jane_storageregistry_packagesregistrypackages__init__)
- [jane_storage.registry_packages.RegistryPackages.base_url](#jane_storageregistry_packagesregistrypackagesbase_url)
- [jane_storage.registry_packages.RegistryPackages.limits](#jane_storageregistry_packagesregistrypackageslimits)
- [jane_storage.registry_packages.RegistryPackages.downloads](#jane_storageregistry_packagesregistrypackagesdownloads)
- [jane_storage.registry_packages.RegistryPackages.get](#jane_storageregistry_packagesregistrypackagesget)

## jane_storage.registry_packages.digest_mismatch

**Функція.** Код: [services/storage/src/jane_storage/registry_packages.py:54](../../../../../../services/storage/src/jane_storage/registry_packages.py#L54).

```python
def digest_mismatch(detail: str) -> JaneError:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `detail` | `str` | `—` | positional-or-keyword |

Результат: `JaneError`.

## jane_storage.registry_packages.check_ref

**Функція.** Код: [services/storage/src/jane_storage/registry_packages.py:73](../../../../../../services/storage/src/jane_storage/registry_packages.py#L73).

```python
def check_ref(pkg: StoragePackage, ref: Mapping[str, Any], source: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pkg` | `StoragePackage` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `source` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`, `digest_mismatch`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``pkg`` is the requested ``package_id@version`` and, when ``digest`` is given, has that digest.
```

## jane_storage.registry_packages.RegistryPackages

**Клас.** Код: [services/storage/src/jane_storage/registry_packages.py:98](../../../../../../services/storage/src/jane_storage/registry_packages.py#L98).

```python
class RegistryPackages:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.registry_packages.md#jane_storageregistry_packagesregistrypackages__init__) | Конструктор | ні |
| [base_url](jane_storage.registry_packages.md#jane_storageregistry_packagesregistrypackagesbase_url) | Поле екземпляра | ні |
| [limits](jane_storage.registry_packages.md#jane_storageregistry_packagesregistrypackageslimits) | Поле екземпляра | ні |
| [downloads](jane_storage.registry_packages.md#jane_storageregistry_packagesregistrypackagesdownloads) | Поле екземпляра | ні |
| [get](jane_storage.registry_packages.md#jane_storageregistry_packagesregistrypackagesget) | Метод | ні |

### Опис із вихідного коду

```text
Storage packages downloaded from one registry and cached by digest (one instance per service).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:432](../../../../../../services/storage/tests/test_registry_packages.py#L432).

```python
packages = RegistryPackages(REGISTRY_URL, PackageLimits(), transport=httpx.MockTransport(answer))
```

Контекст і передумови: [services/storage/tests/test_registry_packages.py:450](../../../../../../services/storage/tests/test_registry_packages.py#L450).

```python
packages = RegistryPackages(
        REGISTRY_URL, PackageLimits(cache_max_entries=2), transport=httpx.MockTransport(answer)
    )
```

## jane_storage.registry_packages.RegistryPackages.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/registry_packages.py:101](../../../../../../services/storage/src/jane_storage/registry_packages.py#L101).

```python
def __init__(self, base_url: str, limits: PackageLimits, *, token: str | None=None, transport: httpx.AsyncBaseTransport | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `base_url` | `str` | `—` | positional-or-keyword |
| `limits` | `PackageLimits` | `—` | positional-or-keyword |
| `token` | `str \| None` | `None` | keyword-only |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:432](../../../../../../services/storage/tests/test_registry_packages.py#L432).

```python
packages = RegistryPackages(REGISTRY_URL, PackageLimits(), transport=httpx.MockTransport(answer))
```

Контекст і передумови: [services/storage/tests/test_registry_packages.py:450](../../../../../../services/storage/tests/test_registry_packages.py#L450).

```python
packages = RegistryPackages(
        REGISTRY_URL, PackageLimits(cache_max_entries=2), transport=httpx.MockTransport(answer)
    )
```

## jane_storage.registry_packages.RegistryPackages.base_url

**Поле екземпляра.** Код: [services/storage/src/jane_storage/registry_packages.py:109](../../../../../../services/storage/src/jane_storage/registry_packages.py#L109).

```python
self.base_url = base_url.rstrip('/')
```

## jane_storage.registry_packages.RegistryPackages.limits

**Поле екземпляра.** Код: [services/storage/src/jane_storage/registry_packages.py:110](../../../../../../services/storage/src/jane_storage/registry_packages.py#L110).

```python
self.limits = limits
```

## jane_storage.registry_packages.RegistryPackages.downloads

**Поле екземпляра.** Код: [services/storage/src/jane_storage/registry_packages.py:116](../../../../../../services/storage/src/jane_storage/registry_packages.py#L116).

```python
self.downloads = 0
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:439](../../../../../../services/storage/tests/test_registry_packages.py#L439).

```python
assert calls == packages.downloads == 1
```

Контекст і передумови: [services/storage/tests/test_registry_packages.py:459](../../../../../../services/storage/tests/test_registry_packages.py#L459).

```python
assert packages.downloads == 4
```

## jane_storage.registry_packages.RegistryPackages.get

**Метод.** Код: [services/storage/src/jane_storage/registry_packages.py:137](../../../../../../services/storage/src/jane_storage/registry_packages.py#L137).

```python
async def get(self, ref: Mapping[str, Any]) -> StoragePackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `StoragePackage`.

### Опис із вихідного коду

```text
The verified storage package of ``ref`` (``PackageRef``) from the cache or the registry.

Raises ``NotFound`` (registry 404), ``UpstreamUnavailable`` (502: no answer, 5xx, refused),
``digest_mismatch``, ``ValidationFailed`` / ``limit_exceeded`` / ``dependency_not_allowed`` (422).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:456](../../../../../../services/storage/tests/test_registry_packages.py#L456).

```python
await packages.get(ref("jane.storage-files-lru", archives[v], v))
```

Контекст і передумови: [services/storage/tests/test_registry_packages.py:436](../../../../../../services/storage/tests/test_registry_packages.py#L436).

```python
return await asyncio.gather(*(packages.get(wanted) for _ in range(8)))
```
