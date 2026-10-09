# WP-23 / C-4: кандидат безпечного cleanup

Стан: **review, кандидат перевірено автором і заморожено для незалежного R2**.
Реальний cleanup Jane **не виконано**: жодного `-Apply` до `C:/repos/Jane`, видалення
реальних refs/worktree чи зміни людського скрипта немає. CI завершених WP не повторювався;
нових `workflow_dispatch`, Docker-команд, змін `main`, force push — 0.

## Межі й артефакти

Власний checkout: `C:/repos/Jane/.claude/worktrees/wp23d`, гілка
`wp/23d-cleanup-safety`, `.jane-wp = 23`; integration база
`40272ca38941e45a7284fb7635748fba48301358`.
У Git додається лише цей звіт. Скрипт, fixture harness, disposable репозиторії
та raw logs — ignored у власній `.jane/`.

Заморожений кандидат:
`C:/repos/Jane/.claude/worktrees/wp23d/.jane/cleanup-post-m3.ps1`.
**SHA256 `76711FBD434E8ACCE191DD246260B3D8649DE9DE48537DCB8E40DD052ADFCA58`**.
PowerShell parser: **0 errors**.

Людський `C:/repos/Jane/.jane/cleanup-post-m3.ps1` не змінено: actual SHA256
`5D54EC5CAFA78D6BE0D9BC357601190CA7D05BBD3ADEF7F18FA4E014DCE6B78F`
дорівнює початковому. Журнал `stream-c.md`, ownership map і чужі checkout не редагувалися.
Залежності C-4 — WP-19, завершення B та success фінального C CI
`37942655574` на `133bb5a0604ccbc3ce41a820216d4751f301a47b`, 14 jobs — передані
координатором; їхні тести повторно не запускалися.

## Поведінка кандидата

- Захищено `main`, `codex/jane-integration`, refs потоків A/B/C, усі варіанти
  WP-15…23, зокрема WP-19a/b і WP-22*/23*, поточний checkout,
  `integ-a/b/c`, `stream-a/b/c-coord` і locked worktrees. Початковий список
  checked-out branches зберігається до завершення запуску для **local і origin**,
  навіть після дозволеного видалення старого чистого checkout. Перед видаленням
  перечитується live registration; remote guard перевіряє checkout також до/після
  чинного pre-push hook.
- Local delete — `git update-ref -d refs/heads/<branch> <plannedSHA>`:
  перевірено actual tip, Git атомарно звіряє старий SHA. `branch -D` не потрібний.
  Незлита історія спершу отримує immutable `archive/*` на **точний** SHA локально
  й на origin; exact `ls-remote --refs origin refs/tags/<tag>` мусить підтвердити
  SHA. Помилка push/verification лишає branch. Теги не переписуються: create-only
  `update-ref ... <zeroSHA>`, без `tag -f`/force. Колізії з existing tags і розбіжними
  planned local/remote tips отримують окремі `--<fullSHA>`/суфіксні імена.
- Remote delete — звичайний `git push origin --delete <branch>`. Тимчасовий
  Git pre-push guard звіряє **advertised remote SHA** зі збереженим planned SHA;
  штатний серверний compare-and-swap відхиляє зміну після advertisement.
  Чинний hook запускається через `git hook run` із його початковим hooksPath,
  незмінними stdin/args; його відмова зберігається. Override hooksPath діє лише
  для цього push, не записується у config. Немає `--force-with-lease`, force push,
  `--no-verify` або зміни захисних repo hooks. Guard files лишаються в `.jane/cleanup-guards/`.
- Dirty та незлиті worktrees лишаються. Перед дозволеним `git worktree remove -- <path>`
  `.jane/` копіюється в `<Repo>/.jane/archive/worktrees/<name>-<UTC>-<GUID>/.jane`,
  перевіряються кількість файлів і SHA256 кожного файла; попередні архіви не затираються.
  Повторно перевіряються status/HEAD/registration/bounds. Force remove, prune,
  residual delete після відмови Git відсутні.
- Усі цілі recursive remove — resolved absolute **direct child** власного
  `<Repo>/.claude/worktrees`, з exact boundary separator. Reparse points у предках
  і в дереві відхиляються; traversal їх не наслідує. FS delete використовує
  PowerShell `Remove-Item -LiteralPath`, без cmd/batch. Unregistered orphan можна
  прибрати лише коли ім'я `agent-<hex>` і вміст **виключно `web/node_modules`**;
  unknown directories/files і junctions лишаються.
- Будь-яка неочікувана native помилка має команду/exit/reason та `FAILED/KEPT`,
  загальний exit 1. Очікуваний `merge-base` exit 1 означає незлиту історію;
  відсутній remote commit object — явний keep із потребою fetch, а не success.
  Output містить planned actions/SHA/tags/reasons і окремі actual totals.

## Actual preflight і dry-run Jane

Команди виконано з `wp23d`, `login:false`; script default Repo — `C:/repos/Jane`,
Integration — `origin/codex/jane-integration`. Скрипт **не виконує fetch взагалі**;
dry-run не змінює refs/tags/index/worktrees/FS (`git --no-optional-locks`). Якщо
tracking integration не дорівнює live origin tip, preflight зупиняється.
Координатор робить один `git -C C:/repos/Jane fetch origin --prune` перед новим
планом/застосуванням; це окрема mutating команда, а не частина dry-run.

```text
$ pwsh -NoProfile -File .jane/cleanup-post-m3.ps1
preflight: repo=C:\repos\Jane integration=origin/codex/jane-integration
SHA=381b01274182dc3805093f81288413135ab13770 apply=False fetch=0
PLAN worktree: ...\wp13r SHA=3a7108f2fae1d73c0f7787038ef6453dbbd7525a
PLAN worktree: ...\wp13s2 SHA=892a2e14406c9c53f28a1eb45ba2ad169bcd8de3
PLAN worktree: ...\wp13t SHA=39cafb52395e6a15fd86915f04907fb0126627a5
planned totals: worktrees=3 orphans=0 local=103 remote=26 archives=13
Dry run: no fetch, ref/tag/worktree/FS mutations.
actual totals: {"worktreesRemoved":0,"worktreesKept":30,"orphansRemoved":0,"orphansKept":13,"localRemoved":0,"localKept":137,"remoteRemoved":0,"remoteKept":54,"tagsCreated":0,"tagsVerified":0,"failures":0}
dry_run_exit=0
```

**13 із 13 unregistered `agent-*` каталогів залишено**: actual структура містить
`web/admin`, а зразок `agent-a0e92a14024286bef/web/admin` має `src`, `public`,
`scripts`, `package.json`, конфігурацію й README — це не доведені лише node_modules
залишки. Старий інвентар із cleanup-plan не є актуальним дозволом на їхнє видалення.
`wp12d` і `wp12e` лишено через reparse `web/admin/node_modules/ajv`.
Усі активні A/B/C/WP15…23 checkout/refs у dry-run захищено.
13 planned archive names — унікальні теги, це не створені теги.

## Цільові safety fixtures: справжній Git, локальний bare origin

Harness `C:/repos/Jane/.claude/worktrees/wp23d/.jane/test_cleanup_safety.py`
створює **новий UUID root** у власній `.jane/safety-fixtures/`; `apply()` перевіряє,
що Repo належить саме цьому root і називається `repo`. Зовнішні checkout/junction
target у тесті — sibling fixtures у цьому самому root, не реальний Jane. Fixtures
не прибиралися, щоб reviewer міг перевірити refs/файли. Скрипт, що перевіряється,
не підмінено; усі push/update-ref/worktree дії виконані реальним Git. Штучні hooks
імітують сусідній сервер/користувача, а не сам компонент.

Actual авторські passes на замороженому script SHA:

| Перевірка | Доказ |
|---|---|
| Dry-run без мутацій | Повний before/after SHA256 snapshot файлів fixture, включно з `.git`/bare refs, збігся |
| Clean merged remove | Два дозволені старі worktree й known orphan прибрано; `.jane` скопійовано/перевірено; initial checked-out branch лишилась local+origin |
| Dirty/unmerged/bounds/reparse/unknown | Залишилися dirty/unmerged checkout, registered external checkout, junction і unknown orphan; зовнішній sentinel незмінний |
| Protected активні refs | WP15…23, WP19a/b, stream-B, main/integration та checked-out branch збереглися local+origin |
| Immutable collision | Existing tag лишився на початковому SHA; divergent local A/remote B отримали два окремі `--fullSHA` tags exact local+origin |
| Унікальний archive dir | Повторне ім'я worktree створило другий архів, перший evidence файл незмінний |
| Archive push відхилено | Bare `update` hook відмовив тегу; **обидва refs збереглися**, tagsVerified=0, загальний exit=1 |
| Remote race після advertisement | Чинний pre-push отримав оригінальні stdin/args і змінив bare remote tip; сервер відмовив delete через incorrect old value; новий ref лишився |
| Remote race до advertisement | Виробнича `Remove-RemoteGuarded`, завантажена з AST скрипта, виконала actual push після зміни bare tip; guard відхилив advertised SHA |
| Чинний hook відмовив | Exit 47 чинного hook призвів до keep remote і загального exit=1 |
| Новий concurrent checkout | Чинний hook створив checkout; post-hook live перевірка відхилила delete, remote зберігся |
| Native worktree remove failed | Windows sharing lock на ignored файлі спричинив actual Git exit=255; архів збережено, residual файл лишився, загальний exit=1 |

```text
$ python .jane/test_cleanup_safety.py
PASS dry-run exact filesystem/ref snapshot; dirty/unmerged/outside/reparse keep
PASS merged remove; immutable divergent SHA archives local+origin; checked-out/active protections; unique evidence archive; known-only orphan
PASS archive push failure keeps local+remote branch, exit=1
```

У цьому авторському запуску наступна fixture assertion очікувала рядок `[deleted]`,
тоді як actual Git pre-push stdin має `(delete) <zeroSHA> <remoteRef> <remoteSHA>`.
Виправлено лише assertion формату harness; production server CAS уже відхилив
delete правильно. Зелені сценарії не повторювалися: залишок запущено окремим
`test_cleanup_races.py`, що виконує ті самі визначення/кейси основного harness.

```text
$ python .jane/test_cleanup_races.py
PASS original pre-push stdin+args preserved; remote changed after advertised SHA -> server CAS rejects delete
PASS existing hook denial respected; remote branch kept
PASS existing hook creates checkout -> live post-hook protection refuses remote delete
PASS native Git worktree remove sharing violation exit=1; archive retained, no residual recursive delete
PASS actual push advertised SHA changed before handshake -> guard rejects delete, no force
ALL FIXTURES PASSED scriptSHA256=76711FBD434E8ACCE191DD246260B3D8649DE9DE48537DCB8E40DD052ADFCA58
fixture_exit=0
```

Негативні сирі докази, середину шляхів скорочено:

```text
FAILED/KEPT local: wp/01-failure reason=git push origin refs/tags/archive/wp/01-failure:refs/tags/archive/wp/01-failure exit=1 : remote: archive-denied
FAILED/KEPT remote: wp/01-failure reason=git push origin refs/tags/archive/wp/01-failure:refs/tags/archive/wp/01-failure exit=1 : remote: archive-denied
actual totals: ... localRemoved=0 remoteRemoved=0 tagsCreated=1 tagsVerified=0 failures=2
remote: error: cannot lock ref 'refs/heads/wp/01-race': is at <newSHA> but expected <plannedSHA>
! [remote rejected] wp/01-race (incorrect old value provided)
cleanup guard: advertised tip differs from planned SHA: (delete) 0000000000000000000000000000000000000000 refs/heads/wp/01-race <newSHA>
cleanup guard: branch became checked-out
FAILED/KEPT worktree: ...\old-locked reason=git worktree remove -- ...\old-locked exit=255 : error: failed to delete ... Invalid argument
```

Raw logs — у **цьому** checkout `.jane/`:

- `wp23d-preflight.txt`, `wp23d-real-dry-run-final.txt` — parser/hash/actual dry-run.
- `wp23d-fixtures.txt`, `wp23d-fixtures-races.txt` — реальний вивід авторських запусків.
- `wp23d-fixture-dry-no-mutations.txt`, `wp23d-fixture-success.txt`,
  `wp23d-fixture-archive-unique.txt`, `wp23d-fixture-archive-push-failure.txt`,
  `wp23d-fixture-remote-server-race.txt`, `wp23d-fixture-original-hook-denial.txt`,
  `wp23d-fixture-concurrent-checkout.txt`, `wp23d-fixture-native-remove-failure.txt`,
  `wp23d-fixture-advertised-tip-race.txt` — кожен сценарій.
- Success/archive-failure fixtures: `.jane/safety-fixtures/14c5fd730d4342ac97bf9874d7fcb7dc/`.
  Remaining negative fixtures: `.jane/safety-fixtures/3c45d21f8dca4f2b89962d5530243f31/`.

## Виправлення після рев'ю 1

Незалежний reviewer отримав початковий кандидат SHA256
`5999F1FC372C4EC77D4E07613FB382ECF17D03139BC4AED2B094A92EED1DD6C5`;
R1 — **changes_requested**, два static findings, зафіксовані координатором
у journal commit `381b01274182dc3805093f81288413135ab13770`.

1. Planned tags не резервували ім'я для divergent local/remote tips. Додано
   `archiveReservations`: різні planned SHA отримують різні immutable імена
   вже у плані, без runtime collision/зайвого keep. Actual fixture перевірив
   збереження existing tag і exact local/origin SHA обох нових тегів.
2. Remote path після archive мав checkout gap. Додано live reread перед
   `Remove-RemoteGuarded`, а також before/after existing hook у guard.
   Actual fixture створив checkout у чинному hook; delete було відхилено.

Після авторських виправлень кандидат заморожено на SHA256 `76711FBD...ADFCA58`;
під час R2 код не змінюється. Максимум два раунди; після R2 можливі виправлення
перевіряє координатор точним репро, без R3.

## Власність і передача координатору

`check-diff main` показує inherited integration зміни: 175 changed files,
152 outside ownership; це вже прийняті A/B/C інкременти відносно старого main,
а не правки C-4. Task-scoped перевірка від точної бази `40272ca...` до автора
до створення звіту дала 0 changed files / 0 outside ownership; після додавання
звіту перевіряється 1 changed file / 0 outside ownership.

Команди для відтворення reviewer:

```powershell
Set-Location C:/repos/Jane/.claude/worktrees/wp23d
Get-FileHash -LiteralPath .jane/cleanup-post-m3.ps1 -Algorithm SHA256
python .jane/test_cleanup_safety.py
python .Codex/hooks/jane_wp.py check-diff 40272ca38941e45a7284fb7635748fba48301358
```

Застосовує **лише координатор після independent accepted review**, з тихим
репозиторієм: власники не пишуть у refs/checkout/ignored evidence під час cleanup.
Read-checks не можуть блокувати довільного стороннього writer між FS операціями;
цей operational prerequisite потрібний для повного збереження ignored evidence.
Після одного fetch слід перечитати новий actual dry-run; наведені числа — зріз,
не дозвіл на фіксований список за старими SHA. Розбіжність hash кандидата — stop.

```powershell
git -C C:/repos/Jane fetch origin --prune
pwsh -NoProfile -File C:/repos/Jane/.claude/worktrees/wp23d/.jane/cleanup-post-m3.ps1
# Після accepted review та перевірки нового plan — лише координатор:
pwsh -NoProfile -File C:/repos/Jane/.claude/worktrees/wp23d/.jane/cleanup-post-m3.ps1 -Apply
```

Permission denial під час авторського real dry-run не було. Fixture sharing
violation — deliberate native failure evidence, не обхід дозволів. Якщо coordinator
Apply буде відхилено permissions, зберегти exact command/exit/reason і лишити об'єкт;
безпечних fallback deletes/prune для обходу відмов скрипт не має.

Запити до інших власників: відсутні. Реальний `Apply`, публікація/заміна людського
ignored скрипта та cleanup verdict/числа виконання — відповідальність координатора.
