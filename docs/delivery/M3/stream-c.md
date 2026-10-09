# Потік C до M3 (2026-10-09)

Доручення: [HANDOFF-2026-10-09-stream-c.md](../HANDOFF-2026-10-09-stream-c.md).
Власний checkout: `C:\repos\Jane\.claude\worktrees\integ-c`, detached HEAD, без `.jane-wp`.

## Поточний стан — C-6/C-4 завершено; C-5 очікує e2e

- C-6: [cleanup-plan.md](cleanup-plan.md) — лише план, жодних видалень. Зріз `19d58a1`: 29 remote refs,
  70 worktree, чужий wp13f має 3 незакомічені документи. Кандидати після M3: 23 remote / 61 clean checkout /
  95 local refs; сумнівні refs, dirty wp13f, main та координатори збережені.
- C-4 завершено для B-11 `97ea4c4`; підсумковий статичний зріз `d37c522..19d58a1` — без нових
  блокерів M3. C-N4 закрито real-receipt 16+1; sessionStorage дозволений ADR, C-N6 уточнює storage-критерій.
- C-5: [CI 37863992541](https://github.com/sql-monk/Jane/actions/runs/37863992541) на `8d7683b`: **in_progress / очікує**;
  limits **pass**, stack та решта завершених job success. Підсумок e2e ще не отримано.
- Нового CI, тестів, Docker або видалень C не виконував. Змінюються лише три власні документи;
  status.md/матриця — потоку A, main потік C не змінює.

### Завершені C-1/C-2

- B2 прийнято потоком A: `5fd7acd`, маркер `merge: accept B2`. CI 37857870977 — 13/13 success,
  e2e 75 passed, без skipped. Власний auth-прогін C — 37 passed; JWKS-мутант виявлено тестом.
- C-2 відтворено з чистого `b3b1101`: встановлення, production build адмінки, вісім сервісів через proxy,
  перевірка ключа (401/200), demo й recorded Telegram — успішно. Вхід через браузер неперевірений:
  доступний браузерний міст не зміг приєднати webview; HTTP адмінки — 200.
- Обидва власні Docker-проєкти, тимчасовий review-worktree і чистий клон прибрано.
  Нових блокерів у виконаних сценаріях немає. Уточнено застаріле твердження про SDK-архів у examples/README.
- Повний локальний check/e2e та новий CI не запускались. Фінальні CI, матриця й status.md — потоку A;
  main і чужі worktree потік C не змінював. Докладний протокол — [final-review-delta.md](final-review-delta.md).

## C-1 — історичний зріз до B2

- `git fetch origin` виконано двічі. Переглянута інтеграційна ревізія: `041e20d`; початковий зріз — `76a03f7`.
- Прочитано handoff, `CLAUDE.md`, правила власності, план WP-13/WP-14/M3, перше фінальне рев'ю,
  журнал потоку B і кінець `status.md`.
- **C-1: завершено.** Переглянуто дельти `08b4110`, `03a31fa`, `0507ef9`, `86cdece`, `cdf261a`,
  `69ab303`, `bf69429`, а також додані під час проходу B-5/B-6 (`8726647`, `a706c54`) і WP-06c (`041e20d`).
  Підсумок: [final-review-delta.md](final-review-delta.md). **Нових блокерів M3 не знайдено.**
- Переглянуто реалізацію ContentRef-політики, egress Web Collector, захист секретних файлів,
  source-фільтр повторної обробки, durable RAW references, зміни SDK/keep-alive та CI.
- **Примітка, відоме обмеження B1:** TOCTOU проміжних каталогів уже описано в
  [01h-content-policy.md](01h-content-policy.md), рядки 222–223. Захищено останній компонент
  (`O_NOFOLLOW`/inode); runtime/llm монтують RAW лише для читання. За прямим уточненням людини
  окремий repro не потрібен і не запускався; це не новий блокер M3.
- `uv sync --all-packages --locked` завершено з exit 0 у власному checkout.
- Read-only `docker compose -p jane-m3c-doc-review config --services` повернув exit 1:
  `no configuration file provided: not found`. Документальні команди backup/restore уточнено через
  container ID саме свого compose-проєкту; коміт `dee854d` поверх `041e20d`. Сам backup не повторювався.
- Неблокувальне зауваження WP-12: fallback RAW для samples без observation_id або з кількома копіями
  обирає перший збіг; після M3 варто узгодити його з omission бекенду. Деталі — C-W2 у рев'ю.
- **C-2: очікує B2.** У прочитаній історії немає `merge: accept B2`; чистий клон і стеки не запускалися.
- Повні `just check`/`just e2e` і новий CI не запускались. Інші worktree, `main`, `status.md`,
  `docs/acceptance/**` та код сервісів не змінювались; Docker-ресурси не створювались і не прибирались.
- **Опубліковано в `origin/codex/jane-integration`: `22ce98e`.** Власний коміт рев'ю/журналу — `70a429e`,
  виправлення backup-документа — `dee854d`. Синхронізація `22ce98e` підхопила документальні коміти A
  (`f45f52a`, `cf8570c`) без конфліктів; їхні зміни status.md потік C самостійно не редагував.
  Push: `cf8570c..22ce98e HEAD -> codex/jane-integration`.
- Підсумкова власна дельта від origin перед push — рівно три файли: цей журнал, final-review-delta.md,
  backup-restore.md; `git diff --check origin/codex/jane-integration HEAD` — exit 0 без виводу.
  `check-diff main` не застосовний до цього detached coordinator checkout без `.jane-wp`:
  `WP unknown: pass --wp NN or create .jane-wp`; власність перевірено за фактичним переліком трьох документів.
- Після публікації в історії досі немає accepted B2. **Роботу C зупинено за умовою handoff після C-1.**
  Наступна дія — C-2 після B2; фінальний запис журналу додається окремим документальним комітом.

Журнал створено на прямий запит людини під час рев'ю й оновлено після C-1. Фінальне приймання M3,
CI, «Фінальна ревізія» матриці та status.md лишаються потоку A; у main потік C не зливав.

## Друга черга — початковий зріз C-3 / C-2 (2026-10-09)

- Прочитано [HANDOFF-2026-10-09-stream-c-2.md](../HANDOFF-2026-10-09-stream-c-2.md) з origin після fetch.
  Integration — `abbc46c`; B2 — `origin/wp/01g2-service-auth` `5c36792`, код `7b41bf4`.
- CI [37857870977](https://github.com/sql-monk/Jane/actions/runs/37857870977): завершені job success,
  включно зі stack/limits; e2e ще in_progress на момент початку C-3.
- Прочитано виправлення r1: cooldown від останньої спроби JWKS, негативні path/method тести,
  перенесення authenticate в test helper, SecretStr токена виконавця, actor fallback у README registry.
- Створено власний тимчасовий detached worktree `.jane/m3c-b2-review` на `5c36792`;
  виконано один auth-набір і один адресний JWKS-мутант із відновленням файла байт у байт.
- На цьому початковому зрізі B2 ще не було злито; подальший фактичний результат наведено нижче.

### C-3: виправлення r1 підтверджено

`origin/wp/01g2-service-auth` `5c36792` має лише документальну дельту після коду `7b41bf4`.
Переглянуто пункти 2–5: негативні path/HEAD/OPTIONS тести, authenticate лише у test helper,
SecretStr розв'язаного токена, попередження про actor=human за відсутності claim.

```text
uv run --all-packages python -m pytest libs/jane-kit/tests/test_auth.py -q
37 passed, 1 warning in 369.67s (0:06:09)
exit 0

JWKS mutant: omit self._attempted_at = now
> assert idp.requests == 1
E assert 20 == 1
FAILED libs/jane-kit/tests/test_auth.py::test_jwks_outage_asks_the_idp_once_per_cooldown
1 failed, 36 deselected in 1.81s
mutant pytest exit: 1
auth.py restored byte-for-byte: True

CI 37857870977: 13/13 jobs success; SHA 7b41bf4c6733f65a32340841a4f7dd7f61bad914
75 passed in 1403.48s (0:23:23)
e2e bad outcome lines: 0
```

Warning auth-набору — Duplicate Operation ID у локальному GET/HEAD fixture, не skip.
Логи власного прогону/мутанта та CI збережено в ignored `.jane/m3c-auth-original.txt`,
`.jane/m3c-auth-mutant.txt`, `.jane/m3c-ci-e2e.txt`. Мутант виконано лише в тимчасовому checkout;
він не потрапляє у злиття. `merge-tree` проти `abbc46c` — без конфліктів.

### Синхронізація з потоком A

Під час адресного прогону інший координатор A відновив роботу й опублікував B2: **`5fd7acd`**,
`merge: accept B2 / WP-01g service authentication (security review r1 fixes verified by stream A, CI 37857870977)`.
Перед власним merge потік C виконав fetch і fast-forward до цієї ревізії; merge B2 повернув
`Already up to date.` — повторного злиття C не створював. Оновлений handoff C-2 повертає власність B2
потоку A; докази A — [01g-auth-coordinator.md](01g-auth-coordinator.md).
Свій адресний результат вище збережено як фактично виконану перевірку, додаткові післязлиттєві набори
повторно потоком C не запускаються. Чинна наступна робота C — відтворення C-2 на прийнятому B2.

### C-2: відтворення завершено, браузерна межа явно зафіксована

- Тимчасовий review-worktree `.jane/m3c-b2-review` видалено після `git diff --exit-code` = 0;
  `owned review checkout exists: False`. Чужі worktree не прибиралися.
- Чистий окремий клон поза репозиторієм: `b3b1101`, каталог
  `C:\Users\aleks\AppData\Local\Temp\jane-m3c-clean-20261009-e09161a4`; до встановлення й перед видаленням
  `git status --porcelain` порожній. Клон видалено після прибирання стеків.
- `uv sync --all-packages` — exit 0. Dev infrastructure `just up` — exit 0;
  старт усіх восьми застосунків і proxy — exit 0. Власні проєкти:
  `jane-m3c-dev-e09161a4`, `jane-m3c-examples-e09161a4`.
- Адмінка: документовані install/build з `web/admin` — exit 0; Node 24, pnpm 11.27.1.
  `just env --format json` повернув `auth.admin_api_key`; значення ключа у звіт не потрапляло.
- Вісім сервісів через proxy: `/v1/health` → 200; `/v1/info` без ключа → 401, з ключем → 200.
  Адмінка `/` → 200 із посиланнями на production assets. Вхід через UI **не перевірено**:
  прихований browser tab завершився timeout, видимий — `Timed out waiting for Browser webview to attach`.
  Це обмеження інструмента, без доказу дефекту продукту; окремий UI-набір не запускався.
- `stack.py up --profile dev-laptop --telegram`, `jane_examples.py demo`, `telegram`, `stack.py down` — exit 0.
  Demo: `ok: true`, 23 RAW, 16 сутностей; price-check за розкладом — 4 матеріали, partial-оновлення версії 2
  зі збереженням title каталогу. Telegram: історія 3 матеріали, зміни 2, у підсумку 5 RAW і 3 події,
  `lecture_version: 2`, `ok: true`; backend записаний (**З**), реальний Telegram не перевірявся.
- `just down -v` — exit 0; `stack.py down` — exit 0, `leftovers: {}`. Фільтри compose labels для обох
  власних проєктів повернули порожні списки контейнерів, мереж і томів. `Owned clean clone exists: False`;
  review-worktree також відсутній. Чужі worktree й Docker-проєкти не прибиралися.
- Backup/restore лише звірено статично: dump/restore не залежать від API auth, перевірка API після restore
  уже вимагає ключ нового стеку. Повторної репетиції не було.
- Документальна знахідка C-W3 виправлена в `examples/README.md`: SDK уже використовує канонічний
  `ZIP_STORED`, твердження про deflate й інший digest застаріло. Жодних змін коду або контрактів C не вносив.
- Витяги фактичного виводу й таблиця «документ → команда → результат» — у final-review-delta.md.
  Логи та безсекретний summary збережено в ignored `.jane/m3c-c2-*.txt/json`; файл із ключем видалено.
  Це функціональне відтворення, не вимірювання продуктивності dev-laptop і не фінальне приймання M3.

## Третя черга — C-4, дельта 2 (2026-10-09)

- `git fetch origin`, чистий `git status --short`, fast-forward власного integ-c до `3a4e29c`.
  Прочитано [HANDOFF-2026-10-09-stream-c-3.md](../HANDOFF-2026-10-09-stream-c-3.md) зі свіжого origin.
- База B2 `3ec9358`; набори 61 файлів branch/merge однакові. 58/61 blobs дорівнюють перевіреному
  `7b41bf4`; увесь код, тести й конфігурація серед них. Три документальні відмінності — передача автора,
  збережені C-W1 і WP-06c README. Executor/sandbox/docker_sandbox/ContentReader/CI дорівнюють першому
  батькові B2; RAW ro/should-fix/scopes/сервісні токени/ключі стеку збережено. Нових блокерів немає.
- WP-06d зберіг кінцеві assertions мережевої спроби і додав очікування job result для HTTP 202;
  sync/async не можуть пройти без failed/sandbox_violation/socket event. Probe справжній; Docker-тест із
  контрольним доступним сервером незмінний. C-N5 пояснює межу API-класифікації й isolation-доказу.
- Другий fetch не змінив origin `3a4e29c`. B-11 відсутній, підготовлені гілки потоку B не приймаються
  замість злитого результату. C-N4 очікує фактичного real-admin N passed із входом за ключем.
- Незалежний статичний підсумок `d37c522..3a4e29c`: нових блокерів M3 немає; M3 не оголошено прийнятим.
  Жодного pytest/lint/typecheck/CI dispatch, Docker або тимчасового worktree у цьому проході.
- Наступна дія після B-11: доповнити «Дельта 2» лише перевіркою злитої адмінки/шаблону/ADR/беклогу й
  real-admin receipt. B2/WP-06d повторно не перевіряти. Status.md, фінальна матриця/CI й main — не власність C.

## Четверта черга — C-5/C-6 і завершення C-4 (2026-10-09)

Доручення: [HANDOFF-2026-10-09-stream-c-4.md](../HANDOFF-2026-10-09-stream-c-4.md).

### C-5: CI 37863992541

Точний SHA: **`8d7683bb6c9b2a8b7e19d660e6df8495e3b81b31`**; workflow — **in_progress / очікує**.
Спостерігається вже запущений прогін; workflow_dispatch/rerun потік C не виконував.

| Job | Висновок | Доказ |
|---|---|---|
| lint | **success** | [job 113606225585](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113606225585) |
| web | **success** | [job 113606448563](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113606448563) |
| unit | **success** | [job 113606448570](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113606448570) |
| web-mock-e2e | **success** | [job 113606448663](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113606448663) |
| isolation | **success** | [job 113607947534](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113607947534) |
| contract | **success** | [job 113607947561](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113607947561) |
| e2e | **in_progress** | [job 113608168969](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113608168969) |
| limits | **success** | [job 113608168989](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113608168989) |
| stack | **success** | [job 113608169010](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113608169010) |
| adapters (minio) | **success** | [job 113608169024](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113608169024) |
| adapters (s3) | **success** | [job 113608169097](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113608169097) |
| adapters (mongodb) | **success** | [job 113608169098](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113608169098) |
| adapters (sqlserver) | **success** | [job 113608169125](https://github.com/sql-monk/Jane/actions/runs/37863992541/job/113608169125) |

**e2e ще виконується; N passed / 0 skipped/xfailed до завершення не заявляються.**

Limits: **pass**, артефакт [limits-ci-37863992541-1](https://github.com/sql-monk/Jane/actions/runs/37863992541/artifacts/11588260101), `ci-20261009T002423Z/summary.md`.
Усі перевірки L1–L8 мають ok, warn/блокерів немає. L1/L2 — 200 сторінок і rate ≈46/45.65 rps при
цілі ≥25 та cap ≤51; L6 — cold start 5/5 без timeout, p95 0.353 s, timeout та OOM→resource_exceeded;
L7 — memory peak 600.2 MiB, 0 OOM-killed containers/restarts; L8 — examples verified=true.

Перемотування main за цим CI поки не підтверджується: чекаємо e2e.

Безсекретні raw докази у власному ignored `.jane/`: `m3c-c5-run.json`, `m3c-c5-limits-summary.md`,
`m3c-c5-artifacts/`; після завершення — `m3c-c5-e2e.txt` і `m3c-c5-e2e-evidence.json`.

### C-6: план прибирання

- [cleanup-plan.md](cleanup-plan.md) створено. Read-only inventory після появи B-11 оновлено на `19d58a1`.
- Remote: 29 refs, 24 ancestor (включно із захищеною integration), 3 лише patch-equivalent, 2 незлиті.
  Local: 109 refs, 98 ancestor; stale upstream локальної wp/01g-service-auth виключено з branch -d.
- Worktree: 70 у заданому каталозі, 64 HEAD ancestor, 6 незлитих; на момент snapshot 68 чистих, 2 dirty:
  чужий wp13f із 3 tracked документами і власний integ-c із новим планом. Координатори захищені.
- Умовні готові групи: 23 remote refs / 61 clean worktree / 95 local refs. Ребазовані/перенесені
  незлиті історії перелічено з причинами; потрібні ignored артефакти зберігаються перед майбутнім remove.
- **Жодного видалення не виконано.** Чужі status читалися з --no-optional-locks; їхні index/файли не змінювалися.

### C-4: B-11

- B-11 `97ea4c4` fetched і fast-forward у власний integ-c; пізніші `86fef32`/`19d58a1` — документи.
- Один статичний прохід по wrapper/fixture/scaffold/ADR/беклогу й сирих receipts. Ніякого повтору
  B2/WP-06d або запуску UI/pytest. [Дельта 2](final-review-delta.md#дельта-2) завершена.
- Сирі receipts: 16 passed + 1 failed на 7eed2e1; після Bearer у трьох GET одного тесту — 1 passed
  на 48af2a1. UI/сервіси/wrapper/fixture й інші 16 сценаріїв незмінні. Не оголошено одним 17 passed прогоном.
- C-N4 закрито: fixture входить за ключем цього stack, backend match/admin_key_consistent=true.
  C-N6 пояснює дозволений ADR sessionStorage; HTML/URL/localStorage не повинні містити ключ.
- Підсумкове незалежне статичне рев’ю d37c522..19d58a1 — без нових блокерів M3; C-W2 після M3.
