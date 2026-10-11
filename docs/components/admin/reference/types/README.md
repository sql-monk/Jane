# Admin: типи й публічні члени

Generated довідник перелічує всі публічні декларації поточного source: класи/інтерфейси/протоколи, конструктори, методи, функції, поля, властивості й constants. Сторінка кожного модуля містить сигнатури, parameters/results, source links та доступність property. Ручні пояснення нижче допомагають вибрати точку розширення; generated файли змінює тільки генератор.

## Навігація

| Завдання | Типи та модулі |
|---|---|
| Повний перелік | [Generated index](generated/README.md) |
| Runtime configuration | [AdminConfig, AuthConfig, parseConfig, serviceBaseUrl](generated/config.md) |
| HTTP клієнт | [ApiClient](generated/api.client.md), [ApiProblem](generated/api.problem.md) |
| Контрактні DTO й schemas | Generated api.generated.* у загальному індексі |
| React context/query hooks | [app.context](generated/app.context.md), [api.hooks](generated/api.hooks.md) |
| Jobs | [JobPanel](generated/components.JobPanel.md) |
| DAG і navigation | [lib.dag](generated/lib.dag.md), [lib.navigation](generated/lib.navigation.md) |
| Theme/auth session | [app.theme](generated/app.theme.md), [auth.session](generated/auth.session.md), [auth.oidc](generated/auth.oidc.md) |
| Сторінки й редактори | Generated pages.* та components.* в індексі |

## Типи та доступність

AdminConfig/AuthConfig є TypeScript interfaces/unions, поля задає parsed runtime config. ApiClient — клас HTTP поведінки; React screens/components — функції, їхні props описані типами. Generated довідник розрізняє function/type/interface/class/method/property; не приписуйте function components конструктори класів.

API ключ/session setter змінює sessionStorage, config parser повертає normalized config; malformed oidc може кинути Error. Backend Problem перетворюється на ApiProblem. [Configuration](../../configuration.md) містить допустимі значення й defaults, [integration](../../integration.md) — runtime використання.

## Приклад

```typescript
import { parseConfig, serviceBaseUrl } from "./config";

const config = parseConfig({ api_base: "/api", auth: { mode: "none" }, page_size: 25 });
const storageBase = serviceBaseUrl(config, "storage");
// storageBase: "/api/storage"
```

Приклад виконується з source середовища Admin; `./config` відноситься до `web/admin/src`. Повна побудова перевірена командою build, окремий уривок в ізоляції тут не виконувався.
