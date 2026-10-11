# Admin: конфігурація

Браузер завантажує `/config.json` з `cache=no-store`. Значення доповнюють DEFAULT_CONFIG у [config.ts](../../../web/admin/src/config.ts); після заміни файла достатньо перезавантажити сторінку. Значення публічні: секретів у цьому документі немає.

[Runtime-поля](#runtime-поля) · [Auth](#auth) · [Локальне середовище](#локальне-середовище) · [Застосування](#застосування)

## Runtime-поля

| Поле | Тип | Default | Обов’язковість / межі | Вплив |
|---|---|---|---|---|
| `api_base` | string | `/api` | Необов’язковий; непорожній рядок | Proxy prefix, завершаючі `/` прибираються |
| `services.orchestrator` | string | `orchestrator` | Необов’язковий; regex імені | Orchestrator service prefix |
| `services.registry` | string | `registry` | Те саме | Registry prefix |
| `services.storage` | string | `storage` | Те саме | Storage prefix |
| `services.llm` | string | `llm` | Те саме | LLM prefix |
| `services.handler` | string | `handler-runtime` | Те саме | Handler Runtime prefix |
| `services.assistant` | string | `assistant` | Те саме | Assistant prefix |
| `services.collector` | string | `web-collector` | Те саме | Collector prefix; інші executor names можуть бути задані етапом |
| `polling.initial_ms` | number | `1000` | ≥100, finite | Перша пауза Job polling |
| `polling.max_ms` | number | `15000` | ≥100; після parse не менше initial_ms | Верхня пауза polling |
| `polling.multiplier` | number | `1.5` | ≥1, finite | Множник backoff |
| `page_size` | number | `50` | ≥1, finite; floor | Default limit списку; backend застосовує власний cap |
| `preview_max_bytes` | number | `262144` | ≥1, finite; floor | Range preview об’єкта Storage |

Service names відповідають regex `^[a-z0-9][a-z0-9._-]*$`. Невалідні service/numeric значення замінюються default, а невідомі поля не додаються до AdminConfig. Браузерний polling/page_size не перекриває серверних hard caps, budgets або job timeout.

## Auth

| Поле | Тип | Default | Обов’язковість / вплив |
|---|---|---|---|
| `auth.mode` | enum | `api_key` | `api_key`, `none`, `oidc` |
| `auth.authority` | string | Немає | Обов’язкове непорожнє при oidc; URL IdP |
| `auth.client_id` | string | Немає | Обов’язкове непорожнє при oidc |
| `auth.scope` | string | `openid profile` | Опційне при oidc; потрібні також API scopes |
| `auth.redirect_path` | string | `/auth/callback` | Опційний callback path; origin додається браузером |
| `auth.post_logout_redirect_path` | string | `/` | Опційний logout path; origin додається браузером |

Невалідний oidc без authority/client_id спричиняє помилку config; не мовчазний перехід у none. OIDC використовує Code + PKCE; tokens/state зберігаються в sessionStorage, automaticSilentRenew увімкнено. Ключ у режимі api_key задає користувач, не config.json. Серверні scopes налаштовуються окремо.

## Локальне середовище

| Змінна | Тип / default | Межі | Вплив |
|---|---|---|---|
| `JANE_ADMIN_PORT` | integer / `4600` | Vite strictPort; число має бути вільним TCP портом | Dev і preview слухають 127.0.0.1 |
| `JANE_ADMIN_MOCK_PORT_BASE` | integer / `4611` | 1024–65000; перевіряє mockPortBase | 7 моків отримують base + index |
| `JANE_ADMIN_API_TARGET` | string / відсутня | Base URL reverse proxy | Якщо задана, всі /api ідуть до цілі без strip |
| `JANE_ADMIN_TARGET_ORCHESTRATOR` | string / відсутня | Base URL сервісу | Hybrid заміна Orchestrator моку |
| `JANE_ADMIN_TARGET_REGISTRY` | string / відсутня | Те саме | Registry |
| `JANE_ADMIN_TARGET_STORAGE` | string / відсутня | Те саме | Storage |
| `JANE_ADMIN_TARGET_LLM` | string / відсутня | Те саме | LLM |
| `JANE_ADMIN_TARGET_HANDLER` | string / відсутня | Те саме | Handler Runtime |
| `JANE_ADMIN_TARGET_ASSISTANT` | string / відсутня | Те саме | Assistant |
| `JANE_ADMIN_TARGET_COLLECTOR` | string / відсутня | Те саме | Web Collector |

Hybrid variables діють лише за відсутності API_TARGET. У hybrid/mock режимі Vite знімає `/api/<service>`; у реального proxy залишає його. Це налаштування dev серверу, а не браузерного bundle; після env-змін перезапустіть Vite.

## Застосування

Приклад runtime-файла:

```json
{
  "api_base": "/api",
  "auth": {"mode": "none"},
  "polling": {"initial_ms": 1000, "max_ms": 10000, "multiplier": 1.5},
  "page_size": 25,
  "preview_max_bytes": 131072
}
```

Відсутні services успадковуються з DEFAULT_CONFIG. Інтерфейс не має platform/source/task/stage ієрархії власних лімітів: їх обчислює Orchestrator; [інтеграція](integration.md). Несумісні JSON або відсутній config перевіряйте за [діагностикою](operations.md#типові-проблеми): HTTP неуспіх config дає defaults, помилка JSON чи oidc конфігурації може зупинити bootstrap.
