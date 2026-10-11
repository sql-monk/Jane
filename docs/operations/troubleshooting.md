# Типові проблеми

Сторінка зводить симптоми, які оператор бачить на рівні платформи, їхні типові причини й перші кроки діагностики. Збої окремих модулів описано в `operations.md` модулів — [перелік](README.md#експлуатація-модулів). Коди помилок API — [contracts/docs/errors.md](../../contracts/docs/errors.md).

## Зміст

- [Перші кроки](#перші-кроки)
- [Стек і запуск](#стек-і-запуск)
- [Health і залежності](#health-і-залежності)
- [Автентифікація й конфігурація](#автентифікація-й-конфігурація)
- [Виконання завдань](#виконання-завдань)

## Перші кроки

1. Стан контейнерів — `just ps`; шукайте `unhealthy`, `Restarting`, `Exited`.
2. Health сервісу — `GET /v1/health`: поле `checks` показує, яка залежність не відповідає.
3. Журнал сервісу — `just logs <сервіс> --tail 200`; помилки старту пишуться до першого запиту.
4. Помилка API — тіло `application/problem+json`: стабільний `code`, `retryable` і `trace_id`. За `trace_id` знайдіть записи журналів усіх сервісів ланцюжка — [трасування](monitoring.md#трасування).

## Стек і запуск

| Симптом | Причина | Що робити |
|---|---|---|
| `docker compose` повідомляє `` run `just up` or set JANE_… `` | compose викликано напряму без облікових даних із файлу стеку | запускайте через `just up`/`just down`; для прямого виклику передайте змінні з `.jane/stack-<проєкт>.json` |
| `` no stack for project …; run `just up` first `` | `just env`/`just ps`/`just logs` для проєкту без файлу стеку | перевірте `--project` або `JANE_COMPOSE_PROJECT`; файл видаляє `just down -v` |
| Після `just up` змінився порт сервісу | `JANE_PORT_<СЕРВІС>` не задано в середовищі цього виклику, контейнер перестворено | задавайте фіксовані порти для кожного `just up` або читайте адреси з `just env` |
| `` `docker compose up` failed (…); see `just logs` `` | контейнер не став `healthy` за `--wait-timeout` | `just logs <сервіс>`; збільшіть `--wait-timeout` або `JANE_UP_WAIT_TIMEOUT` для першої збірки |
| Сервіс не стартує після оновлення колектора | Telegram Collector: `StateFileTooNew` — файл стану новіший за код | оновіть усі екземпляри, що ділять каталог стану, — [оновлення](upgrades.md#кілька-екземплярів-під-час-оновлення) |
| Зміна змінної середовища не діє | змінну сервіс ігнорує: помилка в назві або бракує `LIMITS__` для ліміту | `GET /v1/info` → `limits`; правила назв — [ліміти](limits.md#ліміти-сервісу-файл-і-змінні-середовища) |
| Зміна файлу профілю не змінила лімітів Orchestrator | документ платформи створюється з файлу лише на першому старті | `PUT /v1/limits/platform` — [ліміти платформи](limits.md#ліміти-платформи-в-orchestrator) |

## Health і залежності

| Симптом | Причина | Що робити |
|---|---|---|
| `503`, `"database"`/`"metadata_store"`/`"state"` — `down`, `timeout after 2.0s` | недоступна база сервісу | перевірте `postgres` у `just ps`; після відновлення бази сервіс повертається до `ok` без перезапуску (перевірено для Orchestrator і Registry) |
| Registry: `"blob_store"` — `down` | недоступний MinIO/S3 або неправильні ключі | `just logs minio`; `JANE_REGISTRY_S3_*` |
| Handler Runtime: `"sandbox"` — `down` | немає доступу до Docker-сокета або образу пісочниці | `JANE_DOCKER_SOCKET`, `JANE_DOCKER_GID` (група сокета в контейнері), образ `jane-handler-runtime build-image` |
| Assistant повертає `upstream_unavailable` | не налаштовано або недоступний обов'язковий сусід (LLM gateway, Registry, колектор, Handler Runtime) | `JANE_ASSISTANT_*_URL`, health сусіда |
| Пісочниці лишилися після аварійної зупинки Handler Runtime | контейнери `jane-sbx-*` вбитого процесу; автоматичного прибирання під час старту немає | знайдіть їх за міткою `io.jane.handler-runtime.sandbox=1` і видаліть `docker rm -f` |

## Автентифікація й конфігурація

| Симптом | Причина | Що робити |
|---|---|---|
| `401 unauthenticated` | немає токена, токен не той або сервіс у режимі `api_key` чекає інший ключ | ключ оператора — `JANE_STACK_AUTH_ADMIN_API_KEY` у `just env`; `GET /v1/health` працює без токена |
| `403 forbidden` з `required_scopes` | у ключа немає scope операції | scopes викликача в `JANE_<СЕРВІС>_API_KEYS` — [scopes](security.md#scopes) |
| Сервіс не стартує, `AuthConfigError` | `api_key` без ключів, `jwt` без JWKS/issuer/audience, нерозв'язне `secret_ref` | виправте конфігурацію автентифікації; сервіс навмисно не стартує |
| Сервіс не стартує, `LimitError` | невідомий шлях ліміту, `null` у профілі, стеля нижчого рівня вища за успадковану | перевірте файл профілю (`deploy/profiles/check.py` для профілів репозиторію) |
| `422 secret_ref_not_allowed` при збереженні підключення | `env:` без префікса `JANE_SECRET_` або `file:` поза `/run/secrets` | [секрети](security.md#секрети-й-підключення) |
| `422 secret_detected` | значення, схоже на секрет, у `params` підключення або у файлах пакета | перенесіть значення в `secret_refs` |
| Підключення до сховища відхилено | хоста немає в `JANE_STORAGE_CONNECTION_HOST_ALLOWLIST` | додайте `host:port` |

## Виконання завдань

| Симптом | Причина | Що робити |
|---|---|---|
| `409 idempotency_in_progress` | запит із тим самим `Idempotency-Key` ще виконується (можливо, на іншому екземплярі) | повторіть пізніше з тим самим ключем; відповідь прийде з `Idempotency-Replayed: true` |
| `422 idempotency_key_reused` | той самий ключ з іншим тілом запиту | новий ключ для нового запиту |
| `limit_exceeded` | запит перевищує ефективний ліміт або стелю (розмір матеріалу, кількість URL тощо) | `GET /v1/limits/effective`; зміна лімітів — [ліміти](limits.md) |
| `429 budget_exhausted` від LLM gateway | вичерпано бюджет рівня платформи, джерела або завдання | бюджети й облік витрат — [LLM gateway](../components/llm/operations.md) |
| Запуски не стартують за розкладом | Orchestrator у режимі `JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false` або без воркерів | `docker inspect` змінних середовища — [запуск](running.md#orchestrator-без-планувальника-й-воркерів) |
| Колектор призупинив збір (`paused_by_backpressure`) | споживач не підтверджує матеріали, досягнуто `queue.max_unacked_materials` | це очікувана поведінка; перевірте споживача (Orchestrator, воркери) |
| Росте `jane_orchestrator_leases_reclaimed_total` | воркери або виконавці зникають посеред виклику | журнали виконавців, OOM і перезапуски контейнерів; елемент після `max_lease_reclaims` перехоплень завершується з помилкою |
