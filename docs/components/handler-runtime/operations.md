# Експлуатація Handler Runtime

Executor потребує доступного engine, зафіксованого image і власного shared state для кількох екземплярів.

## Контроль і оновлення

GET /v1/health перевіряє sandbox/state, GET /v1/info показує profiles/capabilities/limits. /metrics і журнали пов’язують invocation/trace. Для виконаної помилки читайте failure.kind/retryable/diagnostics, не лише HTTP status.

![Процес оператора Runtime](../../diagrams/handler-runtime/operator-process.light.png)

[Темна тема](../../diagrams/handler-runtime/operator-process.dark.png) · [Draw.io](../../diagrams/handler-runtime/operator-process.drawio)

Новий image звірте з profile, запустіть тестовий пакет, замініть image mapping та перезапустіть сервіс. Digest пакета не змінюється під тим самим номером. Env/caps застосовуються при побудові Runtime; prepared invocation має власні limits.

## Backup й recovery

При state_dsn резервуйте власну PostgreSQL-схему results/jobs/keys; окремо — package архіви, image digest, конфігурацію та secret refs. Transit blob повинен лишатися доступним до завершення й повтору; restore state не відновлює прострочене download_url.

Кеш можна відтворити з Registry/local ZIP. Без PostgreSQL restart губить result/job/replay: після нього той самий ключ може виконатися знову.

Heartbeat поновлює leases. Expired job позначається failed при читанні; in-progress claim можна забрати після lease. Python-код не продовжується із точки зупинки. Cancel працює з labels контейнера на engine executor; після аварії шукайте залишки лише свого стенда.

| Ознака | Дія |
|---|---|
| Timeout | Вхід, алгоритм і wall cap |
| OOM | Розмір/алгоритм/memory cap |
| Sandbox violation | Прибрати заборонену операцію |
| Docker недоступний | Повернути доступ engine |
| 404 invocation | Retention, state backend, правильний executor |
| Digest mismatch | Звірити байти ZIP та identity |

Альтернативний OCI runtime та багатоекземплярне аварійне recovery не перевірено на реальному сервісі в цьому пакеті.
