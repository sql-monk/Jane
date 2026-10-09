# Потік B: приймання й адмінка після M3

Координатор: Codex. Доручення: [stream-b-handoff.md](stream-b-handoff.md);
обов'язкові правила: [README.md](README.md). Початкова база — `03a172d` від
`origin/codex/jane-integration` (2026-10-09), після приймання WP-20 `7a38c21`.

Кожен інкремент виконує окремий субагент у своєму worktree, `.jane-wp = 22`.
Код приймається після незалежного wp-reviewer (не більше двох раундів),
`contracts/` — також після окремого contract-guardian. Локально запускаються
лише адресні перевірки; новий/змінений e2e — один раз, повтор лише після падіння.
Повний CI потоку — один dispatch після всіх прийнятих злиттів.

Злиття виконує координатор у `.claude/worktrees/stream-b-coord` без `.jane-wp`:
detached checkout інтеграційної вершини, `fetch`, `pull --ff-only origin
codex/jane-integration`, `merge --no-ff` із маркером `merge: accept`,
`push origin HEAD:codex/jane-integration`. Окремий checkout ізолює потік B від
checkout потоку A. `main` і force push не використовуються.

## Стан інкрементів

| Завдання | Гілка / worktree | Стан |
|---|---|---|
| B-1: матриця й сценарії | `wp/22a-acceptance-matrix`, `wp22a` | виконання; лише документи |
| B-2: решта real-адмінки | `wp/22b-admin-real-coverage` | очікує вільного слота виконавця |
| B-3: дві репліки й L2 | `wp/22c-shared-host-replicas`, `wp22c` | виконання |
| B-4: приклад info з limits | `wp/22d-assistant-info-example`, `wp22d` | виконання |
| B-5: S-M3-02 після WP-19 | `wp/22e-storage-contract-cleanup` | очікує маркера `merge: accept WP-19` в origin |

## Початкові перевірки

```text
$ git fetch origin
exit 0
$ git log origin/codex/jane-integration --oneline --grep='^merge: accept WP-19' -3
(порожньо: залежність B-5 ще не прийнята)
$ gh run view 37905643300 --repo sql-monk/Jane --json conclusion,headSha,headBranch,url
conclusion=success
headBranch=wp/21-post-m3-followups
headSha=f69854e429cedf71a6eedfb03897f7518a0da9c5
url=https://github.com/sql-monk/Jane/actions/runs/37905643300
```

Виявлено сторонні контейнери `puluj-g-*` та стек потоку A `jane-wp19-*`;
потік B використовує лише власні унікальні compose-проєкти й прибирає їхні томи.
Профілі `dev-laptop` і `single-node` виключено з обсягу. Реальні зовнішні
LLM/IdP/AWS/Telegram без доступу — не перевірено на реальному сервісі.

## Запити до інших власників

Поки немає. B-5 має явну залежність від приймання WP-19 потоком A.
