# Потік C до M3 (2026-10-09)

Доручення: [HANDOFF-2026-10-09-stream-c.md](../HANDOFF-2026-10-09-stream-c.md).
Власний checkout: `C:\repos\Jane\.claude\worktrees\integ-c`, detached HEAD, без `.jane-wp`.

## Стан — C-1 завершено, C-2 очікує B2

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
