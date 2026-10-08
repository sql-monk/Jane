# Потік C, друга черга (2026-10-09)

**Уточнення людини 2026-10-09:** B2 залишається на потоці A; C виконує відтворення після злиття.
Розділ C-3 нижче переданий назад A і потоком C **не виконується**. Чинне доручення C — C-2.
Докази перевірки A: [01g-auth-coordinator.md](M3/01g-auth-coordinator.md).

C-1 прийнято до відома: [final-review-delta.md](M3/final-review-delta.md) — нових блокерів M3 немає, C-W1 виправлено
(`dee854d`), C-W2/C-N1–C-N3 — після M3. Дякую.

Координатор потоку A зупинився (передача — [HANDOFF-2026-10-09-stream-a.md](HANDOFF-2026-10-09-stream-a.md)).
Щоб розблокувати B-7/B-8 (потік B) і твій C-2, **перевірку й злиття B2 передано тобі (C-3)**. Ти не автор B2;
незалежне рев'ю безпеки B2 (раунд 1) вже проведено — твоя роль: перевірити виправлення після раунду 1 і злити.
Правила, мінімум перевірок і спосіб злиття з `integ-c` — як у [HANDOFF-2026-10-09-stream-c.md](HANDOFF-2026-10-09-stream-c.md).

## C-3. Перевірити й злити B2 (почати зараз)

Повний контекст — [HANDOFF-2026-10-09-stream-a.md](HANDOFF-2026-10-09-stream-a.md) §3.2. Коротко:

- Гілка **`origin/wp/01g2-service-auth`**, HEAD `5c36792` (документація), код `7b41bf4`, база `3ec9358`. Стара
  `origin/wp/01g-service-auth` (`0a5b56b`) — до rebase, **не використовувати**. Звіт: `docs/delivery/M3/01g-auth.md`
  (розділи «Виправлення після рев'ю 1», «Передача»).
- Зауваження рев'ю безпеки r1 (усе інше рецензент визнав коректним):
  1. **блокер:** JWKS — поки немає жодного успішного завантаження, кожен анонімний запит із підробленим `kid`
     звертався до IdP (репро: IdP 503, cooldown 10, 20 запитів → 20 завантажень; черга під lock по 5 с);
  2. тести нормалізації шляхів (`//v1/x`, `/V1/x`, `/v1/%74x`, `/v1/health/../x`, `/v1/health/`, `/v1/health%2f` → 401;
     HEAD з GET; OPTIONS поза таблицею → 403);
  3. застарілий `authenticate()` в orchestrator прибрати/перенести в тести;
  4. `ExecutorConfig.token` → `SecretStr`;
  5. README registry: відсутній `actor` → `human` для сервісного JWT.

Кроки (мінімум):
1. CI **[37857870977](https://github.com/sql-monk/Jane/actions/runs/37857870977)** на `7b41bf4`: на момент запису
   success усі job, крім `e2e` (ще йшов); `limits` і `stack` — success. Дочекайся e2e: рядок `N passed`, 0 skipped.
   Якщо червоне — з'ясуй причину й повідом людині (виправлення — у новій гілці від `5c36792`, один CI).
2. Перевір виправлення сам (без раунду 2): `git diff 0a5b56b origin/wp/01g2-service-auth --
   libs/jane-kit/src/jane_kit/auth.py libs/jane-kit/tests/test_auth.py services/orchestrator services/registry/README.md`;
   у тимчасовому detached worktree від `origin/wp/01g2-service-auth` (прибери після) запусти
   `uv run --all-packages python -m pytest libs/jane-kit/tests/test_auth.py -q`; **мутант**: прибери в `auth.py`
   запам'ятовування часу невдалої спроби JWKS (або умову cooldown для порожнього кешу) — новий тест «IdP 503,
   N запитів → 1 завантаження» має впасти; відновити файл байт у байт. Переконайся, що п. 2–5 зроблено.
3. Злиття з `integ-c` поверх свіжого `origin/codex/jane-integration`:
   `git merge --no-ff origin/wp/01g2-service-auth -m "merge: accept B2 / WP-01g service authentication (security review r1 fixes verified by stream C, CI 37857870977)"`
   — рядок **`merge: accept B2`** обов'язковий (за ним стартують B-7/B-8 потоку B). Очікувані конфлікти:
   `services/handler-runtime/README.md` і, можливо, `executor.py`/settings з WP-06c `041e20d`; README/settings
   llm/orchestrator/web-collector/telegram з should-fix; compose-файли (B1); `.github/workflows/ci.yml`. Зберігай
   обидві сторони. Після злиття: ruff змінених пакетів; `pytest libs/jane-kit/tests/test_auth.py
   libs/jane-kit/tests/test_content.py`; `just test handler-runtime` і `just test orchestrator` без Docker-маркерів.
   Push `HEAD:codex/jane-integration`. Якщо розв'язання конфліктів у **коді** нетривіальне — запуш той самий HEAD у
   тимчасову гілку `wp/m3c-b2-merge-check` і `gh workflow run ci --ref wp/m3c-b2-merge-check` (один прогін).
4. Запиши в `M3/stream-c.md`: вердикт перевірки виправлень (з виводом мутанта), SHA злиття, CI.

## C-2. Відтворення з чистого клону (після C-3)

Без змін — як у [HANDOFF-2026-10-09-stream-c.md](HANDOFF-2026-10-09-stream-c.md) §3, C-2.

## Межі

`status.md`, «Фінальна ревізія» в матриці й фінальний CI — потоку A (наступник прочитає твій журнал). `web/admin/**`
і `templates/service/**` зараз змінює потік B (B-7) — не чіпай. C-W2 лишається після M3.
