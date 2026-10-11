# Інтеграція Registry

Сторонній застосунок використовує registry.v1 без Orchestrator. Нижче клієнт працює з локальним сервером із [quickstart](quickstart.md). Збережіть код у локальному файлі й виконайте через uv run --all-packages python з кореня Jane.

## Публікація й digest

```python
from pathlib import Path
from uuid import uuid4
import httpx
from jane_registry.archive import canonical_archive, digest_of, files_from_dir

archive = canonical_archive(files_from_dir(
    Path("examples/documentation/minimal-package")))
with httpx.Client(base_url="http://127.0.0.1:8105", timeout=30) as client:
    response = client.post(
        "/v1/packages",
        json={"package_id": "documentation.simple-product",
              "kind": "extractor", "title": "Simple product",
              "auto_changes_allowed": False},
        headers={"Idempotency-Key": str(uuid4())})
    response.raise_for_status()
    response = client.post(
        "/v1/packages/documentation.simple-product/versions",
        content=archive,
        headers={"Content-Type": "application/zip",
                 "Idempotency-Key": str(uuid4())})
    response.raise_for_status()
    version = response.json()
    downloaded = client.get(
        "/v1/packages/documentation.simple-product/versions/1.0.0/archive")
    downloaded.raise_for_status()
    assert version["digest"] == digest_of(archive) == digest_of(downloaded.content)
    print(version["status"], version["digest"])
```

Перший запуск повертає draft і однакові digest. Новій логічній команді потрібен новий ключ; для повтору після мережевого збою збережіть той самий ключ і тіло. Повторний запуск прикладу на тому самому Registry отримує conflict: перечитайте наявний пакет/версію, не переписуйте їх. Мережевий клієнт додає bearer token із секрету.

![Публікація Registry](../../diagrams/registry/publish-sequence.light.png)

[Темна тема](../../diagrams/registry/publish-sequence.dark.png) · [Draw.io](../../diagrams/registry/publish-sequence.drawio)

Blob записується перед метаданими версії. Збій між цими записами може залишити blob без посилання: це не розподілена транзакція S3/PostgreSQL. Успішну публікацію підтверджує запис версії.

## Експорт і виконання

```powershell
uv run --all-packages jane-registry export documentation.simple-product@1.0.0 --registry http://127.0.0.1:8105 --out .jane/registry-export
uv run --all-packages jane-registry verify .jane/registry-export/documentation.simple-product-1.0.0.zip --contracts contracts
uv run --all-packages jane-handler-runtime test .jane/registry-export/documentation.simple-product-1.0.0.zip
```

Остання команда потребує Docker та [sandbox image](../handler-runtime/quickstart.md). Export проходить точні dependencies.packages, звіряє metadata digest, ETag та байти й пише jane-export.json. --no-dependencies вимикає обхід; --max-packages обмежує його.

## Сумісна заміна

Інший Registry має підтримувати [v1 API](../../../contracts/openapi/registry.v1.yaml), ZIP, digest/ETag, незмінні версії, errors, cursor, POST keys і статуси. Runtime може обійти Registry через локальний пакет/package_archive; це усуває каталог і download, але не валідацію package/profile.

Registry не активує пакет у TaskConfig й не викликає колектор після публікації. Підтверджений coordinator-run publish_package.py перевіряє download_digest_matches; він не замінює окрему перевірку цього автономного прикладу.
