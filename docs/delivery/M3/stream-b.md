# Потік B до M3 (2026-10-09)

Доручення: [перша черга](../HANDOFF-2026-10-09-stream-b.md),
[друга черга](../HANDOFF-2026-10-09-stream-b-2.md).
Координатор потоку B працює через detached checkout `.claude/worktrees/integ-b` і публікує прийняті інкременти
в `codex/jane-integration`. Злиття в `main` та фінальний gate M3 залишаються людині й потоку A.

## Стан

| Інкремент | Гілка | Стан | Доказ / наступна дія |
|---|---|---|---|
| WP-13s | `wp/13s-r04-completions`, `892a2e1` | **accepted, злито `86cdece`** | незалежне review 1 accepted; [CI 37847417132](https://github.com/sql-monk/Jane/actions/runs/37847417132) на `fcf798c`: 12/12 success, e2e 75 passed, 4 нові PASSED, 0 skipped/xfail/failed; `892a2e1` лише доповнює звіт |
| WP-14d | `wp/14d-docs-entrypoints`, `467bf84` | **accepted, злито `0507ef9`** | незалежне review 1 accepted; повний [CI 37819395884](https://github.com/sql-monk/Jane/actions/runs/37819395884) на `f21947f`: 12/12, e2e 62 passed; push [CI 37848025370](https://github.com/sql-monk/Jane/actions/runs/37848025370) на `359eb0d`: success, нові offline-тести 83 passed; `467bf84` лише доповнює звіт |
| M3 should-fix | `wp/m3-should-fix`, код `aa2b974`, звіт `8718dd2` | **accepted, злито `69ab303`** | незалежне review 2 accepted; [CI 37853233033](https://github.com/sql-monk/Jane/actions/runs/37853233033): lint/types, unit, contract, web, isolation success; розширену частину зупинено за уточненим дорученням користувача; фінальний повний gate — A |
| WP-12d | `wp/12d2-real-reprocessing`, `b6777fb` | **accepted, злито `bf69429`** | незалежне review 2 accepted; [CI 37850908072](https://github.com/sql-monk/Jane/actions/runs/37850908072) на `d5d8efc` success, включно з новим `web-mock-e2e` (29 passed/14 skipped); останній single real WP-09 — 1 passed/exit 0 на accepted backend `69ab303`, `test.fail` знято; новий CI анотації/звіту зупинено за рішенням користувача |

**Перша черга потоку B завершена: 4 із 4 інкрементів accepted і злиті в origin/codex/jane-integration.**
Кодовий підсумок злиттів — `bf69429`; цей журнал додається окремим документальним комітом.
Фінальний gate M3 залишається потоку A; у `main` потік B не зливав.

## Уточнення користувача щодо мінімальних gates

2026-10-09 користувач прямо доручив скоротити рев'ю й тести до необхідного мінімуму та завершити головне.
Після незалежного підтвердження двох виправлень should-fix і success необхідних CI job не очікуємо
branch full e2e/stack/adapters/limits. Запуск 37853233033 зупинено; його загальний статус `cancelled`, а не
`success`. Повний gate зведеної ревізії залишається потоку A. Для фінальної дельти WP-12d (зняття одного
`test.fail` без зміни assert + звіт) достатньо одного real-сценарію на прийнятому backend і перевірки логу/дельти
рецензентом; повторні mock/real suites та новий повний CI цієї дельти не потрібні.

## Журнал

- Прочитано handoff із `origin/codex/jane-integration` (`37c9192`), `CLAUDE.md`, план, довідник розробки,
  кінець `status.md`, фінальне рев'ю M3, скіли `jane-wp` / `jane-contracts` та інструкції незалежного рецензента.
- Перевірено фактичні `git status` / `git log` чотирьох checkout. Незакомічені зміни попередніх авторів
  збережені й продовжуються; WP-13s має два завершені адресні прогони після rebase, хоча handoff їх ще не згадував.
- Запущено окремих виконавців WP-12d і should-fix та незалежного `wp-reviewer` WP-14d. Повні локальні
  `just check` / `just e2e` повторно не запускаються: повні gates — CI, real Playwright — локально.
- Попереднє `git merge-tree --write-tree` для WP-13s і WP-14d проти `37c9192` — без конфліктів.
- **WP-14d — accepted (review 1), `467bf84`; злиття `0507ef9` опубліковано в origin.** Рецензент сам отримав
  `83 passed`; ruff / format / mypy успішні; `unit -k progress_log` запускає додаткову сесію (`1 passed,
  82 deselected`); 122 локальні посилання без помилок. На власних проєктах відтворив dump/restore через
  dev/profile stack: health `ok`, ліміт `777`, профіль і ETag `v3` збережені, перемикачі `false/false → true/true`;
  після прибирання `leftovers: {}`. Власність: 18 файлів, 8 поза WP-14, усі явно делеговані handoff; хуки,
  `libs/jane-kit`, `status.md`, контракти незмінні. Злиття без конфліктів; повний CI сукупної ревізії — gate потоку A.
- **WP-13s — accepted (review 1), `892a2e1`; злиття `86cdece` опубліковано в origin.** Незалежно:
  LLM 68 passed; assistant 15 passed; PostgreSQL 3 passed; нові e2e 4 passed, 9 deselected (282.24 с), без
  skip/xfail. Регресія `unknown.py` відтворена до виправлення і проходить на HEAD. Active window спостерігається
  журналом і станом роботи; повтори не додають викликів/витрат/версій. Root і рецензент перевірили повний CI
  37847417132: 12/12 success, `75 passed in 1476.24s`, усі 4 нові явно PASSED. Злиття без конфліктів.
- **Should-fix review 1 — changes requested.** Рецензент відтворив чотири TOCTOU (resolved target/parent
  для LLM/Telegram) і довільний останній RAW id за двох копій одного observation. Автор виправив обидва;
  CI 37850604947 на `3b45a7b` не є фінальним доказом після цих виправлень. Решта адресних перевірок
  рецензента: 67 passed/4 deselected та 3 integration passed/0 skipped; власність 26/0.
- **Should-fix review 2 — accepted, код `aa2b974`; злиття `69ab303` опубліковано в origin.** Обидва findings
  закриті: власні 4 TOCTOU підміни рецензента повертають `None`; Windows 19 passed/2 deselected;
  Linux 10 filesystem-перевірок/0 skipped. RAW-репро: collect/sample id `None`, ambiguity `True`, порушення
  storage-контракту `[]`; PostgreSQL-набір 10 passed/0 skipped (72.97 с), міграції 3/4 → 5. CI на точному
  `aa2b974`: lint/types/secret scan, unit, contract, web, isolation success; unit `857 passed, 5 skipped,
  326 deselected in 268.62s`. Загальний CI скасовано після цих gates за уточненням користувача.
  Документальний підсумок `8718dd2` коду не змінює. Злиття поверх прийнятого B1 потоку A — без конфліктів;
  зміни потоку A збережені. Власність дельти B: 28 файлів, 0 поза делегованими областями.
- **WP-12d review 2 — accepted, `b6777fb`; злиття `bf69429` опубліковано в origin.** Рецензент незалежно
  перевірив усі 5 виправлень першого раунду, lint/types/build, mock 29 passed/14 skipped і змінені real-сценарії,
  зокрема failed LLM trace та точні витрати. CI 37850908072 на `d5d8efc` success; новий mock job —
  `29 passed (35.0s), 14 skipped`, без Docker. Остання дельта `b6777fb` — лише зняття `test.fail`, коментарі й звіт;
  точні `toContain` / `toEqual` assertions збережено. Новий автоматичний CI 37854575454 цієї дельти зупинено,
  повторні gates не потрібні за рішенням користувача.
- Фінальний single real WP-09: `1 passed (33.6s), exit 0`; accepted backend `69ab303`, image revision
  збігається; встановлений `engine.py` має SHA256
  `a61432844c5d2a36edbbd7c4bb28f27484d1d17f8b79ffd12c1849ea46185f61` — рецензент сам звірив із Git.
  Використано незмінний сценарій/тайм-аути з ignored Chromium new-headless конфігом; runner завершився штатно.
  Лог і fingerprint — `.jane/wp12d2-final-real-wp09.txt`, `.jane/wp12d2-final-backend-update.txt` у checkout WP-12d.
  Власний `jane-wp12d2-r2` прибрано, залишків немає. Відоме зависання Windows headless-shell у попередніх
  bulk-прогонах прозоро описано у WP-12.md; Linux CI та останній контроль завершилися штатно.
- Єдиний конфлікт злиття WP-12d — вставка нового job поруч з оновленим коментарем isolation у `ci.yml`.
  Збережено обидві сторони. YAML-перевірка підтвердила: **усі попередні job семантично незмінні**, додано
  точний уже перевірений `web-mock-e2e`; YAML валідний. Код сервісів/адмінки конфліктів не мав.

## Межі й відкриті запити

`wp01g`, `wp01h`, їхні гілки, `libs/jane-kit/**` і `docs/delivery/status.md` залишаються потоку A.
Документи приймання делеговано потоку B у другій черзі (B-5); остаточний блок ревізії заповнює A.
Checkout потоку A не використовується для злиття. `puluj-g-*` не зачіпається.

Відкриті запити (не блокують прийняті інкременти; `contracts/` потік B не змінював):

1. WP-00 / contract-guardian: явно описати 409 `idempotency_in_progress` у `POST /v1/completions` у
   `llm.v1.yaml`. Нині його задає загальна конвенція; один sync e2e перевіряє тіло Problem напряму.
   Деталі — розділ WP-13s у [WP-13.md](../WP-13.md).
2. WP-00: визначити точний вибір RAW за `object_id` / `observation_id` у повторній обробці. Поточні
   `material_ids` обирають спостереження матеріалу в межах джерела/часу; source-фільтр виправлено, нових
   полів не додано. Деталі — [m3-should-fix.md](m3-should-fix.md).

Необов'язковий запит WP-10 (`py.typed` для імпорту HOLD_LOG_MESSAGE) лишається у звіті WP-13s.
Запит WP-12d щодо зняття `test.fail` **закрито** наведеним real-контролем.

Потоку A залишено: CI на остаточній зведеній ревізії, заповнення фінальної ревізії матриці, рев'ю дельти,
оновлення `status.md`; merge до `main` виконує людина. Зведений real-прогін адмінки передано B-7 другої черги.
Не слід трактувати завершення першої черги потоку B як завершення M3.

## Друга черга

| Завдання | Стан | Коміт / доказ |
|---|---|---|
| B-5 — документи приймання | **Виконано, злито `8726647`** | `1323cbc`: [матриця](../../acceptance/matrix.md) — 13 критеріїв із CI/рядками e2e, R-04 усіх виконавців, S-M2-10 24/1/1, рішення щодо профілів, окремі живі обмеження; [сценарії](../../acceptance/scenarios.md) — актуальні статуси без старих branch/xfail тверджень. Фінальні SHA/CI/e2e залишені для A |
| B-6 — беклог після M3 | **Виконано, злито `8726647`** | `e2dac90`: [open-requests.md](open-requests.md) — 31 група відкритих запитів, окремі вузькі уточнення, закриті пункти з власниками й посиланнями на код; B1, WP-13s, should-fix, WP-12d враховані |
| B-7 — auth real-admin і scopes шаблону | **Очікує злиття B2; не розпочато** | Після B-5/B-6 `git fetch origin`, у `git log origin/codex/jane-integration --grep="^merge: accept B2"` маркер відсутній (origin `76a03f7`). За handoff зупиняємось; повний real-прогін на зведеному auth SHA ще не запускався |
| B-8 — ADR-0005 | **Очікує злиття B2; не розпочато** | Той самий gate; звіт `01g-auth.md` до прийняття B2 не використано |

Мінімум перевірок другої черги дотримано: **нових тестів / CI dispatch / незалежного рев'ю — 0**.
Коротко звірено код закритих запитів (`rg`); локальні посилання — `163`, помилок — `0` разом із журналом;
`git diff --check` — exit 0. Commit hooks: `no leaks found` для обох документальних комітів.
Найновіший завершений limits job [CI 37853683903](https://github.com/sql-monk/Jane/actions/runs/37853683903/job/113574852621)
на `cdf261a` має `verdict: warn` (L2); попередження збережено в матриці, не підмінене `pass`.

Злиття зроблено в detached `integ-b` поверх нового origin `76a03f7`; два нові коміти потоку A збережено,
конфліктів немає. Власна дельта — лише matrix/scenarios/open-requests і цей журнал. `main`, worktree/гілки
потоку A, jane-kit і status потік B не змінював. Подальші B-7/B-8 — після `merge: accept B2`.
