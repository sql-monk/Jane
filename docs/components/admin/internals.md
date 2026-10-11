# Admin: будова

React-застосунок завантажує runtime config, створює auth/context і API клієнти, після чого сторінки використовують React Query та згенеровані контрактні типи.

[Код](#код) · [Типи](#типи) · [Сценарії](#сценарії) · [Власні дані](#власні-дані) · [Розробка](#розробка)

## Код

```text
web/admin/
├── public/config.json        # Runtime адреси, auth, polling
├── src/config.ts             # Parse config із defaults
├── src/app/context.tsx       # Auth/API/query context
├── src/auth/                 # API key session та OIDC Code+PKCE
├── src/api/client.ts         # HTTP, Problem, службові заголовки
├── src/api/generated/        # Типи з OpenAPI і JSON Schemas
├── src/pages/                # Джерела, завдання, пакети, дані, LLM
├── src/components/           # JobPanel, editors, DAG, forms
├── dev-proxy.ts              # Real/mock/hybrid routing
└── e2e/                    # Browser smoke і real-stack сценарії
```

## Типи

AdminConfig/AuthConfig — інтерфейси конфігурації, ApiClient — HTTP-клас, JobPanel і сторінки — function components. Схема відображає використання, а не приписує React-компонентам класове успадкування.

Config і auth визначають ApiClient, яким користуються React Query сторінки.

![Config і auth визначають ApiClient, яким користуються React Query сторінки.](../../diagrams/admin/types.light.png)

[Темна тема](../../diagrams/admin/types.dark.png) · [Редаговане джерело](../../diagrams/admin/types.drawio)

## Сценарії

Навігація [navigation.ts](../../../web/admin/src/lib/navigation.ts) об’єднує робочий простір, дані/якість і налаштування. Запуск завдання повертає job/run, панель показує прогрес і помилку; матеріал має маршрут обробки й збережений результат. Зміна пакета створює нову версію, тестує її runtime та показує diff/походження.

Користувач переходить від джерела й завдання до запуску, матеріалу та результату.

![Користувач переходить від джерела й завдання до запуску, матеріалу та результату.](../../diagrams/admin/user-flow.light.png)

[Темна тема](../../diagrams/admin/user-flow.dark.png) · [Редаговане джерело](../../diagrams/admin/user-flow.drawio)

## Власні дані

Застосунок не має server-side DB. API ключ і OIDC state/tokens — sessionStorage, query cache — пам’ять, тема — браузерні налаштування. Власна ER схема N/A: source/task/run/entity/package дані належать відповідним сервісам. Job lifecycle також належить серверу; UI відображає контрактний стан і polling, не створює власну таблицю jobs.

## Розробка

```powershell
pnpm --dir web/admin gen:api
pnpm --dir web/admin typecheck
pnpm --dir web/admin test
pnpm --dir web/admin build
```

`gen:api` генерує клієнтські типи із contracts; вручну generated файли не редагуйте. Unit/component tests знаходяться поруч із `.test.ts/.test.tsx`; браузерні сценарії — [e2e](../../../web/admin/e2e/). `e2e` запускає контрольовані моки, `e2e:real` потребує real stack конфігурації. Команди цього розділу — порядок розробки; у звіті цього пакета власний виконаний доказ обмежено `build`.

## Застосовність діаграм

Context — контекст, browser/static-server/proxy deployment і залежності; types — інтерфейси/клас/function components; request-flow у integration — послідовність HTTP/job polling; user-flow — процес користувача. ER власної DB й окрема server job state machine N/A через відсутність таких власних даних; показувати чужі таблиці як власні було б некоректно.
