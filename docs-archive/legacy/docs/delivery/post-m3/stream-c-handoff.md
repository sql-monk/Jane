# Потік C (Codex): гігієна репозиторію й документація після M3

Спершу прочитай [README потоків](README.md) (спільні правила), `CLAUDE.md`, `DEVELOPMENT.md`, скіл `jane-wp`.
База: свіжий `origin/codex/jane-integration`. Пакет власності — **`23`** (`.github/**`, `DEVELOPMENT.md`, `README.md`,
`docs/operations/**`, `contracts/python/**`, `contracts/tools/**`, кореневий і сервісні `pyproject.toml`, `justfile`,
`scripts/**`). Журнал потоку — `docs/delivery/post-m3/stream-c.md`.

Контекст: [WP-18.md](../WP-18.md) (інструменти контрактів, R27), [WP-21.md](../WP-21.md) (закріплений oasdiff),
[M3/cleanup-plan.md](../M3/cleanup-plan.md), [status.md](../status.md#після-m3-2026-10-09).

## Завдання

### C-1. CI й документація розробника (документи/CI, без рецензента, якщо лише текст)
- `JANE_OASDIFF_IMAGE` (WP-21: образ oasdiff закріплено за тегом і дайджестом у `contracts/tools/compat.py`, змінна
  перекриває) — згадати в `DEVELOPMENT.md` (розділ команд контрактів WP-18) і коментарем у job `contracts-compat`
  `.github/workflows/ci.yml`.
- Перевірити, що `DEVELOPMENT.md` і кореневий `README.md` відповідають стану після WP-15…21: нові `just`-команди
  контрактів (WP-18), списки onboarding/improvement у асистенті, спільний per-host лімітер Web Collector, нові
  ліміти (`collector.shared_host_*`, storage `conflict_retries`, llm `provider.request_timeout_ms`, асистент
  `llm_call.request_timeout_ms`). Лише факти з коду й звітів; посилання перевірити.

### C-2. `contracts/python` у uv workspace (код збірки; одне незалежне рев'ю)
WP-18 (R27в) залишив `contracts/python` path-залежністю: з ним як членом workspace `uv lock` падає
(«`jane-contracts` is included as a workspace member, but references a path in `tool.uv.sources`»), а виправлення
потребує правок `pyproject.toml` сервісів. **Починати лише після маркера `merge: accept WP-19`** у
`origin/codex/jane-integration` (WP-19 зараз змінює сервіси). Перевірки: `uv lock --check`,
`uv sync --all-packages --locked`, `just types`, `just lint`, `just contract`; повний CI після злиття. Якщо зміна
виявиться ризикованою чи непропорційною — задокументуй рішення лишити path-залежність і закрий пункт.

### C-3. Дрібне форматування
Рецензент WP-16 помітив, що `contracts/python/src/jane_contracts/storage_adapter.py` не проходить
`ruff format --check` (не змінювався WP-16). Перевір, чи `just lint` його охоплює; якщо ні — додай `contracts/python`
до перевірки формату й відформатуй.

### C-4. Прибирання worktree й гілок — **останнім**, після маркерів `merge: accept WP-19` і завершення потоку B
Скрипт людини `C:\repos\Jane\.jane\cleanup-post-m3.ps1` (не в Git; `.jane/` ігнорується): без `-Apply` лише
показує дії; злиті гілки видаляє, незлиті перед видаленням позначає тегом `archive/<гілка>` (локально й на origin),
прибирає 13 осиротілих каталогів `.claude/worktrees/agent-*` (лишились лише `web/node_modules` із задовгими
шляхами) і чисті злиті worktree; `.jane/` кожного worktree перед видаленням копіює в `.jane/archive/worktrees/`.
1. Спершу онови в скрипті список захищених гілок/worktree: не чіпати активні гілки потоків A/B/C і їхні worktree
   (`integ-a` та ваші власні checkout).
2. Запусти без `-Apply`, перевір вивід (жодна гілка з незлитою роботою не має видалятися без тегу `archive/*`).
3. Лише тоді `-Apply`. Не використовувати force-видалення worktree з незакоміченими змінами; брудні — лишити й
   записати в журнал. Результат (скільки worktree/гілок/тегів) — у журнал.
Попередній координатор (Claude) не зміг виконати видалення через обмеження дозволів своєї сесії; якщо у вашій сесії
дії теж заблоковано — не обходь обмеження, залиш людині команду з журналу.

## Завершення
Повний CI — лише якщо змінено код/збірку (C-2/C-3): один `gh workflow run ci --ref codex/jane-integration` після
злиттів, результат у журнал. Повідом людину одним реченням.
