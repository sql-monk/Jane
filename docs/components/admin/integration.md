# Admin: інтеграція

Admin звертається до `<api_base>/<services.name>/v1/...`. [ApiClient](../../../web/admin/src/api/client.ts) надсилає auth, перетворює Problem у зрозумілу помилку й підтримує службові заголовки; типи клієнтів генеруються з контрактів.

## Реальний proxy

На Windows, у терміналі розробки:

```powershell
$env:JANE_ADMIN_API_TARGET = "http://127.0.0.1:8080"
pnpm --dir web/admin dev
```

На Linux/Bash:

```bash
export JANE_ADMIN_API_TARGET=http://127.0.0.1:8080
pnpm --dir web/admin dev
```

Ціль повинна вже маршрутизувати `/api/orchestrator`, `/api/registry`, `/api/storage`, `/api/llm`, `/api/handler-runtime`, `/api/assistant`, `/api/web-collector` у відповідні сервіси. Vite з `API_TARGET` передає `/api` без зняття service prefix. Для production таку маршрутизацію реалізує зовнішній reverse proxy; Vite dev server не є production сервером.

## Один реальний сервіс

Без `API_TARGET` змінна `JANE_ADMIN_TARGET_LLM=http://127.0.0.1:8110` спрямовує тільки LLM у реальний сервіс, знімаючи `/api/llm` перед передачею. Решта префіксів ідуть на моки. Аналогічно працюють `TARGET_ASSISTANT`, `TARGET_STORAGE` та інші назви контрактів. [Правила dev proxy](../../../web/admin/dev-proxy.ts).

UI читає config, додає auth і відстежує результат через Job API.

![UI читає config, додає auth і відстежує результат через Job API.](../../diagrams/admin/request-flow.light.png)

[Темна тема](../../diagrams/admin/request-flow.dark.png) · [Редаговане джерело](../../diagrams/admin/request-flow.drawio)

## Власна інтеграція

Сторонній застосунок може викликати ті самі [контракти](reference/api/README.md) або повторно використати клієнт із [типовим довідником](reference/types/README.md). Admin не експортує окремого серверного REST API. Для API-записів клієнт передає Idempotency-Key, а для редагування конфігурації зберігає ETag і надсилає If-Match. Після 412 перечитайте версію перед повтором.

## OIDC

Задайте authority, client_id, scope і redirect paths у config.json; зареєструйте повні redirect URI в OIDC provider. Сервіси потребують узгоджених issuer/audience/JWKS/scopes. [oidc.ts](../../../web/admin/src/auth/oidc.ts) виконує браузерний flow, [серверна auth-конфігурація](../jane-kit/README.md) належить Jane Kit. Зовнішній OIDC у цьому пакеті не перевірено.
