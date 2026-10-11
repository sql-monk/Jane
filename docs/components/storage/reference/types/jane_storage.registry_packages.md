# Модуль `jane_storage.registry_packages`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/registry_packages.py](../../../../../services/storage/src/jane_storage/registry_packages.py). Не редагуйте вручну.

Storage packages from the handler registry (``registry.v1``: ``GET /v1/packages/{id}/versions/{v}/archive``).

ADR-0009 §4: storage executes a package from the registry **or** the archive in the request. The handler looks at ``package_archive`` first, then at the built-in catalog; this module is the third source, used only when ``JANE_STORAGE_REGISTRY_URL`` is set:

* the address and the bearer token are operator configuration (never from a request); the archive path is built from ``package_id``/``version`` checked against the contract patterns; no redirects, no proxies from the environment; the download stops at ``packages.max_archive_bytes`` and within ``packages.registry_request_timeout_ms``;
* ``ETag`` (when sent) must equal ``sha256:`` of the bytes; the package is read by :func:`~jane_storage.packages.package_from_archive` (storage kind only, no dependencies, archive limits) and its digest is that of the canonical archive (the registry's algorithm); its manifest must be the requested ``package_id``/``version`` and the digest must equal ``handler.digest`` when given;
* verified packages are kept in memory by digest (LRU, ``packages.cache_max_entries``). A cache hit is checked against the requested ``package_id``/``version`` exactly like a download, so a digest of another version is ``digest_mismatch`` with a cold and a warm cache alike. Requests without a digest use the version cached under its ``package_id@version`` (registry versions are immutable);
* concurrent requests for one version share one download.

## Класи

### Клас `RegistryPackages`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.registry_packages` |
| Код | [registry_packages.py:98](../../../../../services/storage/src/jane_storage/registry_packages.py#L98) |

```python
class RegistryPackages: ...
```

Storage packages downloaded from one registry and cached by digest (one instance per service).

#### Конструктор `RegistryPackages.__init__`

```python
def __init__(
    self,
    base_url: str,
    limits: PackageLimits,
    *,
    token: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None: ...
```

Код: [registry_packages.py:101](../../../../../services/storage/src/jane_storage/registry_packages.py#L101).

#### Метод `RegistryPackages.get`

```python
async def get(self, ref: Mapping[str, Any]) -> StoragePackage: ...
```

The verified storage package of ``ref`` (``PackageRef``) from the cache or the registry.

Raises ``NotFound`` (registry 404), ``UpstreamUnavailable`` (502: no answer, 5xx, refused), ``digest_mismatch``, ``ValidationFailed`` / ``limit_exceeded`` / ``dependency_not_allowed`` (422).

Код: [registry_packages.py:137](../../../../../services/storage/src/jane_storage/registry_packages.py#L137).

## Функції

### Функція `check_ref`

```python
def check_ref(pkg: StoragePackage, ref: Mapping[str, Any], source: str) -> None: ...
```

``pkg`` is the requested ``package_id@version`` and, when ``digest`` is given, has that digest.

Винятки в коді функції: `ValidationFailed`.

Код: [registry_packages.py:73](../../../../../services/storage/src/jane_storage/registry_packages.py#L73).

### Функція `digest_mismatch`

```python
def digest_mismatch(detail: str) -> JaneError: ...
```

Код: [registry_packages.py:54](../../../../../services/storage/src/jane_storage/registry_packages.py#L54).
