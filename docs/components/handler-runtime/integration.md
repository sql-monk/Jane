# Інтеграція Handler Runtime

Сторонній застосунок запускає пакет через CLI, Python або HTTP без Orchestrator. Збереження додається окремим Storage handler.

## Python із локальним пакетом

Збережіть код у локальному файлі й виконайте uv run --all-packages python з кореня Jane після [підготовки image](quickstart.md):

```python
import asyncio
from pathlib import Path
from jane_extractor_sdk.package import material_from_file
from jane_handler_runtime.runtime import build_runtime
from jane_handler_runtime.settings import Settings

async def main():
    runtime = build_runtime(Settings())
    try:
        package = runtime.store.load_local(
            Path("examples/documentation/minimal-package"))
        material = material_from_file(
            Path("examples/documentation/minimal-package/tests/product/input.txt"),
            media_type="text/plain")
        invocation = {
            "handler": package.ref,
            "inputs": [{"kind": "material", "material": material}],
            "params": {}, "context": {"test_mode": True},
            "delivery": {"delivery_key": "documentation:local:product"}}
        prepared = await runtime.executor.prepare(invocation, package=package)
        result = await runtime.executor.run(prepared)
        assert result["status"] == "success"
        assert len(result["output"]["entities"]) == 1
    finally:
        runtime.close()

asyncio.run(main())
```

Executor.run не додає HTTP-ідемпотентність і не пише ServiceState: повторний прямий Python-виклик запускає sandbox знову.

## HTTP без Registry

Передайте канонічний ZIP як package_archive ContentRef за [контрактним прикладом](../../../contracts/examples/schemas/handler-invocation/local-package-test-mode.json). Для file:// потрібні blob_roots і файл на вузлі сервера; для download_url — allowlist host. Каталог пакета не є HTTP ContentRef.

POST /v1/invocations вимагає Idempotency-Key, рівний delivery.delivery_key. Sync повертає 200 у межах sync budget, інакше 202 + Job + Location; async одразу повертає 202. Опитуйте Location до кінцевого job status і прочитайте result. Job succeeded та HandlerResult failed описують різні рівні.

![Виклик Runtime](../../diagrams/handler-runtime/invoke-sequence.light.png)

[Темна тема](../../diagrams/handler-runtime/invoke-sequence.dark.png) · [Draw.io](../../diagrams/handler-runtime/invoke-sequence.drawio)

Повтор того самого request/key дає replay header, завершений Result може містити duplicate=true. Інше тіло/ключ — 422, in-progress — 409. Replay обмежений TTL та довговічністю state.

## Великі дані й заміна

ContentFetcher перевіряє sha256, size, host/root та не виконує HTTP redirects. S3 URI сам по собі не надає credentials: потрібне доступне download_url або reader. Output.entities проходять схеми пакета; бізнес-результати належать Storage.

Інший handler.v1 executor має підтримувати inputs/Result/Job/cancel/replay/limits. В [Orchestrator](../orchestrator/integration.md) задайте role=handler, package/kind capabilities та base_url. Runtime оголошує connections=false, тож не замінює handler, якому потрібні керовані Storage/LLM secrets.
