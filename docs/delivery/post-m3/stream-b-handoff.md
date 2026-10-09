# Потік B (Codex): приймання й адмінка після M3

Спершу прочитай [README потоків](README.md) (спільні правила), `CLAUDE.md`, скіли `jane-wp` і `jane-contracts`.
База: `origin/codex/jane-integration` не раніше `7a38c21` (`merge: accept WP-20 …`). Пакет власності — **`22`**
(`tests/e2e/**`, `docs/acceptance/**`, `web/admin/**`, `contracts/**`). Журнал потоку — `docs/delivery/post-m3/stream-b.md`
(гілки, SHA, вердикти рецензентів, реальний вивід команд). Окремі звіти інкрементів — у тому ж журналі, розділами.

Контекст: [WP-20.md](../WP-20.md) (адмінка після M3, «Запити до інших власників»), [WP-21.md](../WP-21.md)
(e2e R-03, S-M3-01/02, «Відкриті питання»), [WP-16.md](../WP-16.md) (R15), [WP-15.md](../WP-15.md),
[WP-17.md](../WP-17.md), матриця [docs/acceptance/matrix.md](../../acceptance/matrix.md) і
[scenarios.md](../../acceptance/scenarios.md).

## Завдання

### B-1. Матриця й сценарії (документи, без тестів і рецензентів)
- Розділ «S-M2-10: адмінка на реальному API»: **25 повністю / 0 частково / 1 навмисний мок** (рядок 10 став повним
  після R26), real-набір адмінки — **18** сценаріїв. Готове формулювання й таблиця — у WP-20.md, «Запити до інших
  власників».
- Додати S-M3-01 (повторна обробка з `stored_materials.object_ids`) і S-M3-02 (JSON-RAW Telegram) та уточнення R-03
  (`attempt_history`/`available_at`) до матриці/сценаріїв із посиланням на CI
  [37905643300](https://github.com/sql-monk/Jane/actions/runs/37905643300) (гілка WP-21, success).
- Не змінювати блок «Фінальна ревізія» M3 — він історичний; новий стан — окремим розділом «Після M3».

### B-2. Real-покриття решти адмінки (`web/admin/e2e`, real через Caddy)
Після WP-20 лише на моках лишились: збереження примітки групи людиною (`ProblemGroup.note`); кнопка повторної
обробки прикладів групи (`object_ids`); показ `retry_scheduled`/`available_at` в елементах запуску; `observation_ids`
і ручні id на сторінці запуску; фільтри `package_id`/`status` у списку запусків вдосконалення. Додай real-сценарії
(`@hybrid`) за зразком наявних (`e2e/hybrid-*.spec.ts`, `scripts/configure-real-stack.mjs`; як піднімати —
WP-20.md і [M3/stream-b.md](../M3/stream-b.md), четверта черга). Заодно дрібне з рев'ю WP-20:
`AssistantPage.tsx` ~167–172, 267–279 — поле `min_onboarding_confidence` відправляє `0`, хоча контракт
`exclusiveMinimum: 0`: валідація в UI. Mock-тести — лише з контрактних прикладів. Одне незалежне рев'ю.

### B-3. L2: дві репліки Web Collector на спільному `STATE_DIR` (`tests/e2e`)
WP-16 (R15) зробив спільний per-host лімітер між екземплярами зі спільним сховищем стану; перевірено лише двома
застосунками в одному процесі. Потрібен e2e: дві репліки web-collector у compose зі спільним томом `STATE_DIR`,
обидві збирають один хост testsite; перевірити, що паралельність і темп на хост не перевищено сумарно
(`max_parallel_fetches_per_host`, інтервал), і що вбита репліка блокує хост не довше TTL. Налаштування — з
`collector.shared_host_*`. Один локальний прогін, далі CI. Одне незалежне рев'ю.

### B-4. Приклад `/v1/info` асистента з `limits` (`contracts/`)
У assistant.v1 немає прикладу `/v1/info` з `limits`, тому mock-тест адмінки підставляє профіль `ci` сам. Додай
приклад (зворотно сумісно), онови mock-тест адмінки, щоб брав його з контракту. Після зміни:
`uv run contracts/tools/check_contracts.py --require-redocly`, `uv run contracts/tools/compat.py --base
origin/codex/jane-integration --oasdiff`, `corepack pnpm --dir web/admin gen:api` (якщо змінились типи). Один прохід
contract-guardian.

### B-5. Після WP-19: прибрати обхід у S-M3-02 (`tests/e2e`)
Чекай у `git log origin/codex/jane-integration` маркер `merge: accept WP-19`. WP-19 виправляє: storage закривав
адаптер на кожен `PUT /v1/connections` (запис падав `adapter is not open`), і `storage.v1 getObjectContent`
перелічував лише три медіатипи. Тоді: прибери очікування `connections_synced` з S-M3-02 (хелпер
`tests/e2e/jane_e2e/orchestration.py`, де це потрібно лише як обхід) і читання `text/plain` поза контрактним
клієнтом, а також виняток у `scenarios.md` (принцип 1), якщо контракт тепер це покриває. Один локальний прогін
S-M3-01/02, далі повний CI.

## Завершення
Після всіх злиттів потоку — один `gh workflow run ci --ref codex/jane-integration`, результат у журнал. Повідом
людину одним реченням: що злито, посилання на CI.
