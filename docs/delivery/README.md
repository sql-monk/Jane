# Звіти й передача робіт

Стан робіт і відкриті питання. Звіти пакетів робіт попередніх етапів лежать в архіві: [docs-archive](../../docs-archive/README.md).

## Перебудова документації, 2026-10-11

Документацію створено заново за [вимогами](../../DOCUMENTATION_REQUIREMENTS.md): стару перенесено в `docs-archive/`, новий зміст написано за кодом, контрактами й ТЗ на ревізіях `48389a3`–`c59d26d`.

| Що | Де |
|---|---|
| Точка входу | [docs/README.md](../README.md) |
| Модулі (12 комплектів) | [docs/components/README.md](../components/README.md) |
| Довідники API й типів (генеруються) | [docs/reference/README.md](../reference/README.md) |
| Діаграми: Draw.io + світлий і темний PNG | [docs/diagrams/README.md](../diagrams/README.md) |
| Приймання | [docs/acceptance/README.md](../acceptance/README.md) |

Інструменти:

```powershell
uv run --no-project python scripts/docs_check.py
uv run --script scripts/docs_diagrams.py check
uv run --script scripts/docs_reference.py check
```

Що перевірено й як:

- **Статичні перевірки** (`docs_check.py`: посилання, якорі, мови блоків, HTML, заголовки) — усі активні сторінки без помилок.
- **Діаграми** (`docs_diagrams.py check`: XML, RGBA-прозорість, непорожні пікселі, однаковий розмір тем, контрольні суми) — усі без помилок. Вибірково переглянуто PNG на світлому й темному тлі.
- **Довідники** (`docs_reference.py check`) — актуальні.
- **Приклади** — quickstart кожного модуля виконано на Windows 11 (PowerShell і Git Bash) з реальним виводом; докази — у сторінках модулів і [матриці приймання](../acceptance/README.md). Linux не перевірявся — це позначено на сторінках.
- **Рендер** — кореневий README переглянуто в Chromium (локальний GFM-рендер) у світлій і темній темах; рендер на GitHub не перевірявся.

## Відкриті питання

Розбіжності й дефекти, знайдені під час документування. На сторінках модулів їх позначено поруч із відповідною можливістю.

| Питання | Де описано |
|---|---|
| Звичайний `just up` не зв'язує сервіси: у Orchestrator немає виконавців, у Registry — профілів runtime; робочий ланцюжок дає `deploy/profiles/stack.py` або `infra/compose.local.yaml` | [getting-started](../getting-started/README.md), [Orchestrator](../components/orchestrator/operations.md) |
| Підключення, надіслані виконавцю, губляться після його перезапуску; Orchestrator не синхронізує їх повторно | [Orchestrator](../components/orchestrator/operations.md), [Storage](../components/storage/operations.md) |
| Storage тримає підключення, job та ключі ідемпотентності в пам'яті екземпляра | [Storage](../components/storage/operations.md) |
| Registry за недоступності БД чи blob повертає `500`, а не `502 upstream_unavailable` | [Registry](../components/registry/operations.md) |
| Orchestrator: `upstream_conflict` з HTTP 502 проти 409 у моделі помилок; стани `leased` і `skipped` з контракту не встановлюються; `overlap: queue` окремо не обробляється | [overview/limitations.md](../overview/limitations.md) |
| `contracts/docs/data-ownership.md`: SQLite для Handler Runtime і PostgreSQL для колекторів — у коді інакше; Registry не запускає тестів | [overview/limitations.md](../overview/limitations.md) |
| `vault:` у схемі підключення дозволено, у коді відхиляється | [overview/limitations.md](../overview/limitations.md) |
| Handler Runtime: `wall_time_ms` рахується від старту контейнера (на Docker Desktop 2–6 с) | [Handler Runtime](../components/handler-runtime/configuration.md) |
| Інтеграційні тести Orchestrator: 6 з 60 впали в одному локальному прогоні (таймінги під навантаженням не виключено) | [матриця приймання](../acceptance/README.md) |
| 6 тестів `services/web-collector/tests/test_render_js.py` падають на Windows | — |
| Скіл `jane-wp` посилається на `.Codex/wp-paths.json`; фактичний шлях — `.claude/wp-paths.json` | [development/wp-process.md](../development/wp-process.md) |
