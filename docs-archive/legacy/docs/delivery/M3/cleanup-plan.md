# План прибирання після M3 — потік C

**Лише план. Жодного видалення гілок, worktree, файлів або Docker-ресурсів не виконано.**

Доручення: [HANDOFF-2026-10-09-stream-c-4.md](../HANDOFF-2026-10-09-stream-c-4.md), C-6.
Зріз: `origin/codex/jane-integration` **`19d58a1b2cf1590a5f780871b31ba0b595d9009b`**; інвентар сформовано `2026-10-09T00:29:43.851553+00:00`.
Читаються Git refs/метадані та `git --no-optional-locks -C <wt> status --porcelain=v1 -z --untracked-files=all`.
Опційне оновлення чужих index вимкнено; вміст незакомічених файлів не читався й не змінювався.

Віддалені refs потрібних префіксів: **29**; повністю ancestor: **24** (включно із захищеною integration).
Локальні гілки: **109**, ancestor: **98**.
Worktree під `C:/repos/Jane/.claude/worktrees/`: **70**, чистих **68**, з незакоміченим **2**;
HEAD ancestor — **64**, не ancestor — **6**.

## Умови виконання людиною

Команди нижче — кандидати **після приймання M3**, збереження інтегрованої історії та завершення роботи її власників.
`main`, `origin/codex/jane-integration`, основний checkout `C:/repos/Jane` та `integ-a/b/c` залишити.
Перед виконанням освіжити refs і звірити SHA зі зрізом; для worktree повторити status. Чистота тут означає
лише tracked і неignored untracked: потрібні ignored журнали/артефакти/локальні дані зберегти окремо.
Не застосовувати force, `git branch -D`, `git worktree remove --force` чи prune для обходу відмов.

```powershell
git -C C:/repos/Jane fetch origin
git -C C:/repos/Jane merge-base --is-ancestor 19d58a1b2cf1590a5f780871b31ba0b595d9009b origin/codex/jane-integration
git -C C:/repos/Jane worktree list --porcelain
```

`merge-base --is-ancestor` exit 0 підтверджує входження **всіх комітів**. `git cherry` `-` означає
еквівалентний патч, `+` — еквівалент не знайдено. Він не перевіряє merge-коміти: їх кількість наведена окремо.
Позначка «замінено» за звітом не перетворює `+` на доказ злиття; такі refs не входять до готових команд.

## Віддалені origin/wp/* та origin/codex/*

| Ref | SHA | Входження / патчі | Рішення |
|---|---|---|---|
| `origin/codex/jane-integration` | `19d58a1` | ancestor: так | Залишити: чинна інтеграційна гілка. |
| `origin/wp/00d-auth-decisions` | `c301bbe` | незлито: +1/-0; merges 0 | Підготовлена версія до rebase; фінальний відповідник увійшов у B-11 97ea4c4. Стару історію оцінювати за cherry, автоматичного видалення немає. |
| `origin/wp/00e-auth-decisions-final` | `32509ff` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/01e-testsite-price-fixture` | `8dfae55` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/01f-testsite-injection` | `40dad87` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/01g-service-auth` | `0a5b56b` | незлито: +3/-7; merges 0 | Стара B2 до rebase/r1; замінена wp/01g2-service-auth (5c36792, ancestor). +3/-7: уся стара історія не еквівалентна. |
| `origin/wp/01g2-service-auth` | `5c36792` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/01h-content-ref-policy` | `0a34aa5` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/01i-template-scopes` | `9fa705f` | патчі еквівалентні: +0/-1; ancestor: ні | Підготовлена версія до rebase; фінальний відповідник увійшов у B-11 97ea4c4. Стару історію оцінювати за cherry, автоматичного видалення немає. |
| `origin/wp/01j-template-scopes-final` | `e330062` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/06c-oom-classification` | `4245c2e` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/09c-stable-delivery-body` | `55711cb` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/12d-real-reprocessing` | `4a080e1` | патчі еквівалентні: +0/-6; ancestor: ні | Замінена wp/12d2-real-reprocessing (b6777fb, ancestor). Усі 6 патчів еквівалентні, але старі коміти не ancestor. |
| `origin/wp/12d2-real-reprocessing` | `b6777fb` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/12e-admin-auth-key` | `58c5eec` | патчі еквівалентні: +0/-1; ancestor: ні | Підготовлена версія до rebase; фінальний відповідник увійшов у B-11 97ea4c4. Стару історію оцінювати за cherry, автоматичного видалення немає. |
| `origin/wp/12f-admin-auth-final` | `8145b34` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13j-cross-instance` | `86b87c7` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13k-storage-registry-replicas` | `5c7a1ae` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13l-real-price-fixture` | `678460f` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13m-assistant-orchestrator-replicas` | `cecd73a` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13n-injection-e2e` | `c97fdc6` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13o-r04-storage-runtime` | `26c6250` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13p-r04-restart-replays` | `7133b85` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13q-r02-r04` | `017e61a` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13r-r04-active-replays` | `3a7108f` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13s-r04-completions` | `892a2e1` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/13t-real-registry-fixtures` | `39cafb5` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/14d-docs-entrypoints` | `467bf84` | ancestor: так | Кандидат після M3: усі коміти увійшли. |
| `origin/wp/m3-should-fix` | `8718dd2` | ancestor: так | Кандидат після M3: усі коміти увійшли. |

## Заміни старих гілок

| Попередня | Чинна / доказ | Обмеження |
|---|---|---|
| `origin/wp/01g-service-auth` | `origin/wp/01g2-service-auth`, 5c36792; [01g-auth.md](01g-auth.md) | Нова ancestor; стара +3/-7, залишена окремо від готових команд |
| `origin/wp/12d-real-reprocessing` | `origin/wp/12d2-real-reprocessing`, b6777fb | Нова ancestor, стара має лише -6; історія старих SHA все одно не ancestor |
| локальна `wp/10c-package-cache-identity` | `wp/10d-package-cache`, e6ba69b; [WP-10](../WP-10.md), [WP-13h](../WP-13.md) | Нова ancestor; стару +5 звірити по перенесених шляхах/рішенню власника |
| локальна `wp/05a-timing-tests` | `wp/05b-timing-registry`, `wp/03a-timing-discovery`, `wp/04a-timing-telegram`; звіти [WP-05](../WP-05.md), [WP-03](../WP-03.md), [WP-04](../WP-04.md) | Усі три ancestor; вихідна змішана історія +7 зберігається у wpflaky |
| локальна `wp/02d-flaky-tests` | `wp/02e-stable-process-tests`, `wp/11e-flaky-assistant`; [WP-02](../WP-02.md), [WP-11](../WP-11.md) | Обидві ancestor; вихідна +5 зберігається у wpflaky2 |
| `wp/00d`, `wp/01i`, `wp/12e` | B-11 фінальні refs `wp/00e-auth-decisions-final`, `wp/01j-template-scopes-final`, `wp/12f-admin-auth-final` | Фінальні refs увійшли через 97ea4c4; старі оцінювати за cherry, підготовку не оголошувати ancestor |

Віддалених `origin/wp/10c`, `origin/wp/05a`, `origin/wp/02d` та відповідних перенесених refs у цьому
інвентарі вже немає; наведені вище їхні фактичні **локальні** назви. Команди для неіснуючих remote refs не генеруються.

## Worktree: повний інвентар заданого каталогу

Назви в таблиці доповнюються префіксом `C:/repos/Jane/.claude/worktrees/`. Стан — на момент інвентарю;
наявність локального злиття в `integ-b` не замінює входження в `origin/codex/jane-integration`.

| Worktree | HEAD / гілка | Git status | Входження / рішення |
|---|---|---|---|
| `a-b2-verify` | `5c36792` / `detached` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a00db6af551e37c8b` | `8a5a3a6` / `wp/10-llm` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a0e92a14024286bef` | `af1578e` / `wp/13-assistant-flows` | чистий | незлито: +8/-0; merges 0; Стара окрема історія assistant-flow (+8); автоматично не доведена еквівалентність прийнятим інкрементам. Потрібне рішення власника WP-13. |
| `agent-a0ed3805e1ece0d9d` | `4047d43` / `wp/13-storage-adapters` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a147eba8298cd761d` | `e6e1f02` / `wp/05-registry` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a390efc373f81d058` | `2110470` / `wp/13-reliability` | чистий | незлито: +6/-0; merges 0; Стара окрема історія reliability (+6); патч-еквівалентність не підтверджено. Потрібне рішення власника WP-13. |
| `agent-a3c35004a053f046f` | `0b2e683` / `wp/06-handler-runtime` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a54a9758908f31634` | `6f93348` / `wp/02b-backpressure` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a5ff98b6cf51baeee` | `95de12a` / `wp/09b-queue-concurrency` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a842dd5f8e60fb46d` | `5bf6b60` / `wp/14-limit-profiles-ops` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-a8be96cdc055ee805` | `bd77769` / `wp/12c-full-real-api` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-aa46bc5ce07d9f2c0` | `8c36308` / `wp/13-acceptance` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-ab8874eb8ecc3787e` | `578ff1c` / `wp/07b-secret-policy` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-ac9a12d6355660b48` | `5e30b82` / `wp/13-llm-routing` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-acbff17c5a57a7d93` | `2252672` / `wp/04-telegram-collector` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-acf68e1c95b7987eb` | `8d95946` / `wp/08-storage-adapters` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-ad814036d2e146e0b` | `58de814` / `wp/11c-diverse-sampling` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-ae84ca2f813c20945` | `ea5ee90` / `wp/07-storage-core` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-aebeb1dc1e4d3c10e` | `d5bbfcd` / `wp/03-web-collector-discovery` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `agent-afe39a1e8e9b90553` | `83b5d54` / `wp/00a-api-feed-docs` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `b11-real` | `f80a909` / `codex/jane-b11-real-gate` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `integ-a` | `19d58a1` / `codex/jane-integration` | чистий | ancestor: так; Залишити: координатор. |
| `integ-b` | `86fef32` / `detached` | чистий | ancestor: так; Залишити: координатор. |
| `integ-c` | `aa09b9f` / `detached` | **НЕЗАКОМІЧЕНО 1** | ancestor: так; Залишити: координатор. |
| `wp00d` | `32509ff` / `wp/00e-auth-decisions-final` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01b` | `99e9ddb` / `wp/01b-limits-profile-file` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01c` | `de5b2b9` / `wp/01c-unique-instance-id` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01d` | `e682ab0` / `wp/01d-retry-read-errors` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01e` | `8dfae55` / `wp/01e-testsite-price-fixture` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01f` | `40dad87` / `wp/01f-testsite-injection` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01g` | `5c36792` / `wp/01g-service-auth` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01h` | `0a34aa5` / `wp/01h-content-ref-policy` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp01i` | `e330062` / `wp/01j-template-scopes-final` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp02c` | `b219435` / `wp/02c-shared-host-limit` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp02e` | `eebb9fe` / `wp/02e-stable-process-tests` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp03a` | `6847104` / `wp/03a-timing-discovery` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp04a` | `2f6c38e` / `wp/04a-timing-telegram` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp05b` | `518e1cf` / `wp/05b-timing-registry` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp06a` | `85aa5aa` / `wp/06a-runtime-job-lease` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp06c` | `4245c2e` / `wp/06c-oom-classification` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp06d` | `7fe87b9` / `wp/06d-async-network-test` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp07c` | `dfd0d9c` / `wp/07c-storage-registry-packages` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp09c` | `55711cb` / `wp/09c-stable-delivery-body` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp10c` | `787a863` / `wp/10c-package-cache-identity` | чистий | незлито: +5/-0; merges 0; Зміни передані WP-10d і WP-13h: WP-10.md:356, WP-13.md:2602. +5: перенесення по шляхах не дорівнює входженню всіх комітів. |
| `wp10d` | `e6ba69b` / `wp/10d-package-cache` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp11e` | `11031a8` / `wp/11e-flaky-assistant` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp12d` | `b6777fb` / `wp/12d2-real-reprocessing` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp12e` | `8145b34` / `wp/12f-admin-auth-final` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13d` | `9822cfc` / `wp/13d-reliability` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13e` | `e70c16d` / `wp/13e-price-check` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13f` | `c482382` / `wp/13f-r07-restarts` | **НЕЗАКОМІЧЕНО 3** | незлито: +1/-0; merges 0; Залишити: спершу зберегти зміни; команди remove немає. |
| `wp13g` | `74711e5` / `wp/13g-registry-types` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13h` | `663bfcb` / `wp/13h-llm-cache-e2e` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13i` | `7332d21` / `wp/13i-storage-e2e` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13j` | `86b87c7` / `wp/13j-cross-instance` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13k` | `5c7a1ae` / `wp/13k-storage-registry-replicas` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13l` | `678460f` / `wp/13l-real-price-fixture` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13m` | `cecd73a` / `wp/13m-assistant-orchestrator-replicas` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13n` | `7133b85` / `wp/13p-r04-restart-replays` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13q` | `017e61a` / `wp/13q-r02-r04` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13r` | `3a7108f` / `wp/13r-r04-active-replays` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13s` | `3c98542` / `wp/13s-r04-llm-assistant` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13s2` | `892a2e1` / `wp/13s-r04-completions` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp13t` | `39cafb5` / `wp/13t-real-registry-fixtures` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp14b` | `1c13758` / `wp/14b-profile-followups` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp14c` | `df6aff6` / `wp/14c-rate-jitter-check` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wp14d` | `467bf84` / `wp/14d-docs-entrypoints` | чистий | ancestor: так; Ancestor; кандидат після M3. |
| `wpflaky` | `7869dde` / `wp/05a-timing-tests` | чистий | незлито: +7/-0; merges 0; Змішану роботу розділено у wp/05b, wp/03a, wp/04a; WP-05.md:419, WP-03.md:182, WP-04.md:375. +7: цілу історію не приймати як злито. |
| `wpflaky2` | `4d480d5` / `wp/02d-flaky-tests` | чистий | незлито: +5/-0; merges 0; Розділено по власниках: WP-02e (WP-02.md:909) і WP-11e (WP-11.md:548), обидві ancestor; +5 у змішаній історії залишаються. |
| `wpm3fix` | `8718dd2` / `wp/m3-should-fix` | чистий | ancestor: так; Ancestor; кандидат після M3. |

### Незакомічене — зберегти окремо

`wp13f`: три tracked документи, ще не коміт/архів; цей checkout і гілку **не прибирати**.
Власний integ-c містить документ цього проходу; це активний захищений coordinator checkout.

`C:/repos/Jane/.claude/worktrees/integ-c`, HEAD `aa09b9f`, `detached`:

- `??` `docs/delivery/M3/cleanup-plan.md`

`C:/repos/Jane/.claude/worktrees/wp13f`, HEAD `c482382`, `wp/13f-r07-restarts`:

- ` M` `docs/acceptance/matrix.md`
- ` M` `docs/acceptance/scenarios.md`
- ` M` `docs/delivery/WP-13.md`


Власник wp13f має зберегти його зміни у коміт/окрему копію; C їх не комітив і не змінював.
Документи власного integ-c публікуються окремим комітом потоку C.

## Локальні refs поза готовими командами

| Ref | SHA / патчі | Причина залишити |
|---|---|---|
| `wp/00d-auth-decisions` | `c301bbe`; незлито: +1/-0; merges 0 | Підготовлена версія до rebase; фінальний відповідник увійшов у B-11 97ea4c4. Стару історію оцінювати за cherry, автоматичного видалення немає. Останній окремий коміт: c301bbe docs(auth): record B2 decisions and conditional closures [skip ci] |
| `wp/01g-service-auth` | `5c36792`; ancestor: так | Локальний HEAD ancestor, але upstream origin/wp/01g-service-auth на 0a5b56b не містить його; branch -d може відмовити. Не включено у готові команди. |
| `wp/01i-template-scopes` | `9fa705f`; патчі еквівалентні: +0/-1; ancestor: ні | Підготовлена версія до rebase; фінальний відповідник увійшов у B-11 97ea4c4. Стару історію оцінювати за cherry, автоматичного видалення немає. Останній окремий коміт: 9fa705f fix(scaffold): enforce scopes in service template [skip ci] |
| `wp/02d-flaky-tests` | `4d480d5`; незлито: +5/-0; merges 0 | Розділено по власниках: WP-02e (WP-02.md:909) і WP-11e (WP-11.md:548), обидві ancestor; +5 у змішаній історії залишаються. Останній окремий коміт: 4d480d5 test(web-collector): report the exit code of a service that exits during start |
| `wp/05a-timing-tests` | `7869dde`; незлито: +7/-0; merges 0 | Змішану роботу розділено у wp/05b, wp/03a, wp/04a; WP-05.md:419, WP-03.md:182, WP-04.md:375. +7: цілу історію не приймати як злито. Останній окремий коміт: 7869dde test(discovery, telegram-collector): HTTP and collection timeouts from configuration |
| `wp/10c-package-cache-identity` | `787a863`; незлито: +5/-0; merges 0 | Зміни передані WP-10d і WP-13h: WP-10.md:356, WP-13.md:2602. +5: перенесення по шляхах не дорівнює входженню всіх комітів. Останній окремий коміт: 787a863 fix(llm): keep request archives out of reference lookups |
| `wp/12e-admin-auth-key` | `58c5eec`; патчі еквівалентні: +0/-1; ancestor: ні | Підготовлена версія до rebase; фінальний відповідник увійшов у B-11 97ea4c4. Стару історію оцінювати за cherry, автоматичного видалення немає. Останній окремий коміт: 58c5eec test(admin): read real e2e API key from stack [skip ci] |
| `wp/13-assistant-flows` | `af1578e`; незлито: +8/-0; merges 0 | Стара окрема історія assistant-flow (+8); автоматично не доведена еквівалентність прийнятим інкрементам. Потрібне рішення власника WP-13. Останній окремий коміт: af1578e test(e2e): require representative name-only onboarding sample |
| `wp/13-r04-idempotency` | `dc5248e`; незлито: +1/-0; merges 0 | Окремий старий патч replay (+1). Покриття R-04 в M3 не є доказом еквівалентності цього коміта; залишити для власника WP-13. Останній окремий коміт: dc5248e test(e2e): cover collector and LLM idempotency replay |
| `wp/13-registry-e2e` | `961afd2`; патчі еквівалентні: +0/-1; ancestor: ні | Один патч еквівалентний integration (-1), але старий SHA не ancestor; git branch -d може відмовити. Останній окремий коміт: 961afd2 test(e2e): cover registry package lifecycle |
| `wp/13-reliability` | `2110470`; незлито: +6/-0; merges 0 | Стара окрема історія reliability (+6); патч-еквівалентність не підтверджено. Потрібне рішення власника WP-13. Останній окремий коміт: 2110470 docs: complete reliability acceptance handoff |
| `wp/13f-r07-restarts` | `c482382`; незлито: +1/-0; merges 0 | Незлита стара версія R-07 (+1) і три незакомічені документи. Зберігати checkout та branch; видалення виключено. Останній окремий коміт: c482382 e2e: R-07 accepts every retried extraction rejected with 422 as the known defect |

## Готові команди лише для повністю злитих кандидатів

Це **23 remote refs**, **61 чистих worktree** і **95 локальних refs** за наведеним зрізом.
Повторна перевірка актуального SHA/status і завершення роботи власника перед кожною групою — умова плану.
Команди не виконувалися. Порядок: прибрати непотрібний clean checkout, потім його local branch; remote refs —
коли інтегрована історія збережена. Якщо git відмовляє, залишити об’єкт і з’ясувати зміну стану.

### 1. Чисті worktree, HEAD яких ancestor

```powershell
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/a-b2-verify'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a00db6af551e37c8b'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a0ed3805e1ece0d9d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a147eba8298cd761d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a3c35004a053f046f'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a54a9758908f31634'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a5ff98b6cf51baeee'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a842dd5f8e60fb46d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-a8be96cdc055ee805'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-aa46bc5ce07d9f2c0'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-ab8874eb8ecc3787e'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-ac9a12d6355660b48'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-acbff17c5a57a7d93'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-acf68e1c95b7987eb'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-ad814036d2e146e0b'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-ae84ca2f813c20945'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-aebeb1dc1e4d3c10e'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/agent-afe39a1e8e9b90553'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/b11-real'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp00d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01b'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01c'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01e'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01f'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01g'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01h'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp01i'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp02c'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp02e'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp03a'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp04a'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp05b'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp06a'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp06c'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp06d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp07c'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp09c'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp10d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp11e'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp12d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp12e'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13e'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13g'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13h'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13i'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13j'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13k'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13l'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13m'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13n'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13q'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13r'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13s'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13s2'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp13t'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp14b'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp14c'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wp14d'
git -C C:/repos/Jane worktree remove -- 'C:/repos/Jane/.claude/worktrees/wpm3fix'
```

### 2. Local branch після звільнення checkout

`git branch -d` використовує власну перевірку злиття; виконувати з checkout main після завершення M3.
Патч-еквівалентні та незлиті refs сюди не включені.

```powershell
git -C C:/repos/Jane branch -d -- codex/integration-wp01a-base codex/jane-b11-real-gate codex/jane-stream-b-docs-20261009 worktree-agent-a00db6af551e37c8b worktree-agent-a0e92a14024286bef worktree-agent-a0ed3805e1ece0d9d worktree-agent-a147eba8298cd761d worktree-agent-a390efc373f81d058
git -C C:/repos/Jane branch -d -- worktree-agent-a3c35004a053f046f worktree-agent-a54a9758908f31634 worktree-agent-a5ff98b6cf51baeee worktree-agent-a842dd5f8e60fb46d worktree-agent-a8be96cdc055ee805 worktree-agent-aa46bc5ce07d9f2c0 worktree-agent-ab8874eb8ecc3787e worktree-agent-ac9a12d6355660b48
git -C C:/repos/Jane branch -d -- worktree-agent-acbff17c5a57a7d93 worktree-agent-acf68e1c95b7987eb worktree-agent-ad814036d2e146e0b worktree-agent-ae84ca2f813c20945 worktree-agent-aebeb1dc1e4d3c10e worktree-agent-afe39a1e8e9b90553 wp/00-architecture-contracts wp/00a-api-feed-docs
git -C C:/repos/Jane branch -d -- wp/00e-auth-decisions-final wp/01-scaffold-ci wp/01a-infra-followup wp/01b-limits-profile-file wp/01c-unique-instance-id wp/01d-retry-read-errors wp/01e-testsite-price-fixture wp/01f-testsite-injection
git -C C:/repos/Jane branch -d -- wp/01h-content-ref-policy wp/01j-template-scopes-final wp/02-web-collector-core wp/02a-api-feed-validation wp/02b-backpressure wp/02c-shared-host-limit wp/02e-stable-process-tests wp/03-web-collector-discovery
git -C C:/repos/Jane branch -d -- wp/03a-timing-discovery wp/04-telegram-collector wp/04a-timing-telegram wp/05-registry wp/05b-timing-registry wp/06-handler-runtime wp/06a-runtime-job-lease wp/06c-oom-classification
git -C C:/repos/Jane branch -d -- wp/06d-async-network-test wp/07-storage-core wp/07b-secret-policy wp/07c-storage-registry-packages wp/08-storage-adapters wp/09-orchestrator wp/09b-queue-concurrency wp/09c-stable-delivery-body
git -C C:/repos/Jane branch -d -- wp/10-llm wp/10d-package-cache wp/11-assistant wp/11b-adaptive-sampling wp/11c-diverse-sampling wp/11e-flaky-assistant wp/12-admin wp/12a-generated-api
git -C C:/repos/Jane branch -d -- wp/12b-real-api wp/12c-full-real-api wp/12d-real-reprocessing wp/12d2-real-reprocessing wp/12f-admin-auth-final wp/13-acceptance wp/13-limits-e2e wp/13-llm-routing
git -C C:/repos/Jane branch -d -- wp/13-storage-adapters wp/13d-reliability wp/13e-price-check wp/13g-registry-types wp/13h-llm-cache-e2e wp/13i-storage-e2e wp/13j-cross-instance wp/13k-storage-registry-replicas
git -C C:/repos/Jane branch -d -- wp/13l-real-price-fixture wp/13m-assistant-orchestrator-replicas wp/13n-injection-e2e wp/13o-r04-storage-runtime wp/13p-r04-restart-replays wp/13q-r02-r04 wp/13r-r04-active-replays wp/13s-r04-completions
git -C C:/repos/Jane branch -d -- wp/13s-r04-llm-assistant wp/13t-real-registry-fixtures wp/14-limit-profiles-ops wp/14b-profile-followups wp/14c-rate-jitter-check wp/14d-docs-entrypoints wp/m3-should-fix
```

### 3. Remote refs, які повністю ancestor

```powershell
git -C C:/repos/Jane push origin --delete wp/00e-auth-decisions-final wp/01e-testsite-price-fixture wp/01f-testsite-injection wp/01g2-service-auth wp/01h-content-ref-policy wp/01j-template-scopes-final wp/06c-oom-classification wp/09c-stable-delivery-body
git -C C:/repos/Jane push origin --delete wp/12d2-real-reprocessing wp/12f-admin-auth-final wp/13j-cross-instance wp/13k-storage-registry-replicas wp/13l-real-price-fixture wp/13m-assistant-orchestrator-replicas wp/13n-injection-e2e wp/13o-r04-storage-runtime
git -C C:/repos/Jane push origin --delete wp/13p-r04-restart-replays wp/13q-r02-r04 wp/13r-r04-active-replays wp/13s-r04-completions wp/13t-real-registry-fixtures wp/14d-docs-entrypoints wp/m3-should-fix
```

## Сумнівні та активні — без команд видалення

Незлиті/лише patch-equivalent refs і відповідні worktree перелічено вище з причинами.
Старі WP-13/10c/05a/02d і dirty wp13f залишаються. Координатори й основний checkout захищені. Для старих rebased/перенесених гілок
зберегти потрібну історію або отримати рішення власника; C-6 не оголошує їх злитими за назвою.

Read-only raw інвентар з повними SHA, git status і cherry-результатами збережено у власному integ-c:
`.jane/m3c-c6-inventory.json` (ignored). Тестів/CI/прибирання в C-6 — 0.
