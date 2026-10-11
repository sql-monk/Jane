# Admin: залежності

Admin — статичний браузерний застосунок, який використовує серверні API за потребою відкритої сторінки.

## Середовище

| Залежність | Версія або джерело | Потрібна для |
|---|---|---|
| Node.js | [.node-version](../../../.node-version) | Розробка й збірка |
| pnpm | `11.27.1`, [package.json](../../../web/admin/package.json) | Відтворення залежностей із pnpm-lock.yaml |
| Браузер | Chromium у Playwright перевірках | Runtime React, fetch, sessionStorage |
| Статичний сервер | SPA fallback та `config.json` | Production hosting |
| Reverse proxy | `/api/<service>/v1/...` | Реальні API без вбудованих адрес у bundle |
| Python/uv | Версії репозиторію | Лише локальні контрактні моки |

Підтримку інших браузерів перевіряйте окремо; наявність браузерного API сама по собі не підтверджує сумісність усіх версій. Прямі залежності React, Router, React Query, AJV, CodeMirror та oidc-client-ts задані у package.json; точні версії у [pnpm-lock.yaml](../../../web/admin/pnpm-lock.yaml).

## API за сторінками

| Розділ | Сервіси |
|---|---|
| Джерела, завдання, запуски, проблеми, ліміти, аудит | Orchestrator |
| Пакети, версії, код, форки | Registry, Handler Runtime при тестуванні |
| Матеріали й результати | Orchestrator та Storage |
| LLM | LLM |
| Асистент | Assistant; він сам викликає своїх сусідів |
| Підключення | API керованих connections відповідного виконавця |

Сервіс, що недоступний, спричиняє помилку конкретного запиту. Admin не читає таблиці напряму. Повторити без повної платформи можна через сім контрактних моків; [quickstart](quickstart.md#запуск).

## Автентифікація

`api_key` використовує bearer ключ із sessionStorage. `oidc` потребує доступного authority, client_id та дозволених redirect URI; серверні сервіси мають перевіряти отриманий JWT. `none` придатний для локального сценарію з відповідно налаштованими API. Перемикання UI в `none` не вимикає серверну перевірку прав.

## Заміна API

Сумісний backend або proxy має зберігати контракт і service prefixes. `config.json.services` задає імена префіксів; [dev-proxy.ts](../../../web/admin/dev-proxy.ts) задає локальні цілі. Заміна на generic REST API без контрактних типів потребує зміни клієнта, а не лише адреси.
