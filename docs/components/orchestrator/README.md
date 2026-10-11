# Orchestrator

Orchestrator виконує завдання й розклади, передає матеріали між етапами та зберігає стан у власній PostgreSQL. Він координує виконавців через API; бізнес-дані записують окремі Storage handler.

## Зміст

- [Межі](#межі)
- [Контекст](#контекст)
- [Навігація](#навігація)

## Межі

На вході — SourceConfig, TaskConfig із DAG, connections/limits та команди run/reprocess/cancel/activation. На виході — run/items, підсумки етапів, material trace, unknown materials, problem groups і audit.

Власна PostgreSQL потрібна навіть мінімальному API; брокер не потрібен. Без виконавців API керує конфігурацією, але не збирає матеріали й не запускає пакети. Пряме використання колектора або Runtime не потребує Orchestrator.

Config та limits фіксуються у snapshot run. Зміна TaskConfig/activation впливає на наступні запуски. Registry publication не активує пакет автоматично. Сталі delivery keys захищають повтори лише за дотримання ідемпотентності executor у межах TTL.

## Контекст

![Контекст Orchestrator](../../diagrams/orchestrator/context.light.png)

[Темна тема](../../diagrams/orchestrator/context.dark.png) · [Draw.io](../../diagrams/orchestrator/context.drawio)

Суцільні стрілки — API-виклики або запис own state. Orchestrator не читає таблиці сусідів; матеріали надходять через collector або Storage API.

## Навігація

| Сторінка | Практичне питання |
|---|---|
| [Швидкий старт](quickstart.md) | Мінімальний API і наскрізний run |
| [Залежності](dependencies.md) | PostgreSQL та executor registry |
| [Конфігурація](configuration.md) | Workers, tokens, caps, leases |
| [Інтеграція](integration.md) | Клієнт і сумісний executor |
| [Будова](internals.md) | DAG, queue, routing, власні дані |
| [Експлуатація](operations.md) | Оновлення, backup та recovery |
| [HTTP API](reference/api/README.md) | Config, runs, limits, diagnostics |
| [Типи й члени](reference/types/README.md) | Core, Engine, Admin та функції |

Джерела: [ТЗ §6](../../../TECHNICAL_SPECIFICATION.md#6-завдання-та-розклади), [код](../../../services/orchestrator/src/jane_orchestrator/), [OpenAPI](../../../contracts/openapi/orchestrator.v1.yaml).
