# B2 / WP-01g: перевірка координатором потоку A

Дата: 2026-10-09. Доручення: [HANDOFF потоку A](../HANDOFF-2026-10-09-stream-a.md), §3.2.
Новий координатор A не був автором B2; незалежне рев'ю безпеки r1 вже проведено.
За прямим уточненням людини B2 залишається на A; потік C виконує відтворення після злиття.

## Перевірена ревізія

- `origin/wp/01g2-service-auth` = `5c367920ff420b776d443eeb572c42a4c820ad20` (документальна вершина).
- Код = `7b41bf4c6733f65a32340841a4f7dd7f61bad914`; виправлення r1 = `fe977e4`.
- Worktree автора `wp01g` чистий. Перевірка й тимчасовий мутант виконані у власному detached
  `a-b2-verify`; чужі checkout не редагувалися. Після мутанта `git diff --exit-code` = 0.
- Переглянуто `git diff 0a5b56b..origin/wp/01g2-service-auth -- libs/jane-kit/src/jane_kit/auth.py
  libs/jane-kit/tests/test_auth.py services/orchestrator` і окрему дельту `fe977e4` для README registry.

## Зауваження r1

| Зауваження | Підтвердження координатора |
|---|---|
| JWKS cooldown при недоступному IdP | `_attempted_at` встановлюється перед завантаженням, зберігається після невдачі; lock і лічильник спроб об'єднують паралельні запити. Порожній кеш у cooldown дає 503/Retry-After, відомі ключі після невдалого оновлення працюють з кешу. Тест із 20 запитами проходить; мутант дає 20 завантажень замість 1. |
| Нормалізація шляхів, HEAD/OPTIONS | Шість варіантів шляхів перевірено на 401; HEAD бере GET scope; OPTIONS поза таблицею дає 403 з дійсним токеном. Усі входять у 37 успішних тестів. |
| Застарілий `authenticate()` orchestrator | Прибрано із продукційного модуля, залишено тестовий помічник у `orch_support.py`; `test_logic.py` імпортує його звідти. |
| Токен виконавця у repr | `ExecutorConfig.token` має тип `SecretStr`; розв'язання secret_ref обгортає значення, executors дістає його лише для заголовка. Тест перевіряє відсутність токена в repr. |
| Відсутній actor registry | README прямо пояснює default `human`, наслідки для сервісного JWT асистента та необхідний claim `actor: llm` або належний api_key. |

## Реальний вивід адресних команд

```text
$ uv run --all-packages python -m pytest libs/jane-kit/tests/test_auth.py -q
37 passed, 1 warning in 5.25s
# warning: Duplicate Operation ID для GET/HEAD маршруту лише тестової фікстури.

$ uv run --all-packages python .jane/verify_jwks_mutant.py
FAILED ...::test_jwks_outage_asks_the_idp_once_per_cooldown
E assert 20 == 1
FAILED ...::test_cached_keys_outlive_a_failed_refresh
E assert 6 == 2
2 failed, 35 deselected in 1.76s
JWKS_MUTANT_EXIT=1
AUTH_RESTORED_BYTE_FOR_BYTE

$ git diff --exit-code
exit 0; без виводу

$ uv run --all-packages python -m pytest services/orchestrator/tests/test_logic.py services/orchestrator/tests/test_executors.py -q
28 passed in 1.59s
```

Мутант прибирає рівно одне присвоєння `self._attempted_at = now`. Скрипт відновлює оригінальні байти
у `finally` і перевіряє їхню тотожність; очікуваний pytest exit 1 означає, що тести ловлять регресію.
Повторний раунд незалежного рев'ю та повні локальні набори не запускалися.

## CI і рішення

[CI 37857870977](https://github.com/sql-monk/Jane/actions/runs/37857870977) на коді `7b41bf4`:
12/13 job success, e2e ще виконується на момент запису. `stack` і `limits` success.
Артефакт `limits-ci-37857870977-1`, `ci-20261008T231735Z/summary.md`: **verdict warn** —
L2 single gap 0.0082674 s < 0.015 s; решта перевірок, включно з memory L6, успішні.
Це branch evidence, фінальний CI M3 після B-7/B-8/C-2 ще потрібний.

Виправлення п'яти зауважень r1 підтверджені. Приймання і злиття B2 чекають завершення e2e.
Код не змінено, конфліктів у попередньому `git merge-tree --write-tree HEAD origin/wp/01g2-service-auth` немає.
JWT з реальним IdP — **не перевірено на реальному сервісі**.
