# Фінальний gate M3 — 2026-10-09

**M3 досягнуто в інтеграційній гілці; WP-13 і WP-14 accepted.** Прийнятий код:
`77c58905de860c68dfceaf2beadf7496afc3f95d`. [Матриця всіх 13 критеріїв](../../acceptance/matrix.md#фінальна-ревізія);
[незалежне фінальне рев'ю](final-review-delta.md#дельта-2) — нових блокерів M3 немає.

## CI на фінальному коді

[CI 37865985595](https://github.com/sql-monk/Jane/actions/runs/37865985595), workflow_dispatch на незмінному
тегу `codex/m3-2026-10-09-77c5890`, **13/13 job success**. Тег вказує на остаточну інтеграційну
ревізію після B-11/C-4. Окремий ref зберіг активний проміжний CI 37863992541 на `8d7683b`:
concurrency-групи різні. Це один фінальний повний CI після всіх кодових злиттів.

| Job | Висновок |
|---|---|
| lint | success |
| unit | success |
| web | success |
| web-mock-e2e | success |
| contract | success |
| isolation | success |
| limits | success |
| stack | success |
| e2e | success |
| adapters (sqlserver) | success |
| adapters (minio) | success |
| adapters (s3) | success |
| adapters (mongodb) | success |

Команди перевірки:

```powershell
gh run view 37865985595 --json status,conclusion,headSha,headBranch,jobs
gh api --allow-escape-sequences repos/sql-monk/Jane/actions/jobs/113614524271/logs
gh run download 37865985595 --name limits-ci-37865985595-1 --dir .jane/evidence/final-ci-37865985595
```

Metadata і журнал e2e збережено в `.jane/evidence/final-ci-37865985595/` та звірено: SHA збігається,
всі 13 jobs success, 75 рядків PASSED, SKIPPED/XFAIL/XPASS/FAILED відсутні.
Усі 29 назв тестів, наведених у матриці, знайдено серед PASSED.

```text
status=completed conclusion=success headSha=77c58905de860c68dfceaf2beadf7496afc3f95d
======================= 75 passed in 1453.72s (0:24:13) ========================
E2E_PASSED_ROWS=75
E2E_NONPASS_ROWS=0
JANE_E2E_REQUIRED=1
MATRIX_TEST_NAMES_VERIFIED=29
```

Lint/types, `uv sync --all-packages --locked` і gitleaks пройдено: `no leaks found`.
`web-mock-e2e` — `29 passed (25.1s), 14 skipped`: це навмисно виключені real-тести,
окремі від обов'язкового backend-e2e з нульовими skips.

## Профіль ci

Артефакт `limits-ci-37865985595-1`, каталог `ci-20261009T004740Z`.
Git `77c58905de860c68dfceaf2beadf7496afc3f95d`, dirty:false; Docker 28.0.4,
Ubuntu 24.04.5 LTS, 4 CPU, 15.6 GiB; foreign containers:0.

```text
Verdict: warn
L1 single gap (jitter), s: value=0.013882637023925781, limit >= 0.015 -> warn
Усі інші вимірювання L1–L8 -> ok
L7 OOM-killed containers: 0
L7 container restarts: 0
```

`warn` дозволений фінальним gate, записаний як попередження. Профіль `ci` прийнято наживо.
`dev-laptop` / `single-node` — кандидати, не перевірені наживо; рішення про виключення
`dev-laptop` ×3 від 2026-10-08 збережено у [WP-14](../WP-14.md).

## Незалежні та real-докази

- B1/B2 закрито; B2 злитий `5fd7acd`, виправлення рев'ю перевірено A з мутантом JWKS
  ([звіт](01g-auth-coordinator.md)).
- [C-4](final-review-delta.md#дельта-2) переглянув `d37c522..19d58a1`, включно з B2,
  WP-06d і B-11. Нових блокерів M3 немає; C-W1/C-W3 виправлено, C-N4 закрито.
- [C-2](final-review-delta.md#відтворення-після-b2), чистий клон `b3b1101`: вісім healthy сервісів,
  health 200, info без ключа 401 / із ключем 200, admin assets 200; demo ok:true,
  23 RAW / 16 сутностей, 4 оновлення цін; записаний Telegram ok:true, 5 RAW / 3 події.
- [B-11 real-адмінка](stream-b.md#четверта-черга): повний набір на
  `7eed2e18799ad8ae36c40ca48b8b004f9943fdb3` — `16 passed (4.1m), 1 failed`.
  Прямі GET одного тесту отримали 401 без Bearer; після виправлення тесту на
  `48af2a1bdf075a27f1568fbc2d5ca088ec03d65d` — `1 passed (26.9s)`.
  Сукупно всі 17 real-сценаріїв підтверджено; UI/сервіси/wrapper/fixture й решта 16 тестів тотожні.
  Повний прогін лишається 16/1. Покриття адмінки — 24 повністю / 1 частково / 1 навмисний mock із 26.

Межі приймання й замінники збережено в матриці. Реальні LLM/IdP/AWS не оголошено перевіреними;
C-W2/R33 та інші [після-M3 запити](open-requests.md) лишаються відкритими. Прибирання
worktree/гілок не виконувалося; сторонні ресурси не змінювалися.

## Передача до main

Пізніші зміни — лише документи: **код ідентичний `77c58905de860c68dfceaf2beadf7496afc3f95d`**.
Прийнятий стан із фінальними документами — тег `codex/m3-2026-10-09`;
пізніші злиття після M3 до нього не входять. Основний checkout перевірено:
чистий `main` на `d37c522`, предок прийнятої ревізії. Координатор A не змінює `main`; людина виконує:

```powershell
git -C C:/repos/Jane fetch origin
git -C C:/repos/Jane merge --ff-only codex/m3-2026-10-09
git -C C:/repos/Jane push origin main
```

Після людського push перевірити CI на `main`. Документальний коміт має `[skip ci]`;
для окремого workflow_dispatch на `main` — `gh workflow run ci --ref main`.
