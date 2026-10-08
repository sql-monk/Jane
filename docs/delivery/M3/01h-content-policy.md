# WP-01h (M3, B1). Політика читання ContentRef

**Гілка:** `wp/01h-content-ref-policy` · **Ревізія коду:** `aa8c5de` · **База:** `codex/jane-integration` `03a31fa`
(перебазовано з `3c98542` за вказівкою координатора; WP-13r/13t уже в базі) · **Стан:** review

Наскрізне доручення координатора за фінальним рев'ю M3 (блокер): `.jane-wp` немає, шляхи — з доручення.

## Проблема

`file://` у ContentRef читався будь-де (`file:///proc/self/environ` → змінні середовища з DSN і секретами йшли в
LLM-провайдер або в результат), `download_url` — на будь-який хост (SSRF), у handler-runtime ще й із
`follow_redirects=True`, в assistant — без ліміту розміру й тайм-ауту з конфігурації (і `search.py` з тайм-аутом
httpx за замовчуванням). Місця: `services/llm/.../packages.py` `read_content` (вхід `POST /v1/invocations`),
`services/assistant/.../content.py` `material_bytes` (`/v1/unknown-materials`, зразки вдосконалення, вибірка
онбордингу), `services/handler-runtime/.../packages.py` `ContentFetcher._download`.

## Результат

1. **`libs/jane-kit/src/jane_kit/content.py`** — спільний `ContentReader` (взірець — storage після WP-07b, сам storage
   не змінено):
   - `inline` — `utf-8` (типово) або строгий `base64`;
   - `download_url` — лише `http`/`https`, `host[:port]` з allowlist (`hostname` — будь-який порт, `hostname:port` —
     лише цей; **типово `[]` — вимкнено**), без userinfo/фрагмента/пробілів/зворотних скісних, IPv6-літерали
     відхиляються; `follow_redirects=False` (3xx — 502 неповторюваний, навіть на дозволений хост),
     `trust_env=False` (без проксі й `.netrc` із середовища), `Accept-Encoding: identity` і відмова від
     закодованого тіла (без «gzip-бомб»), `Content-Length` і потік обрізаються на ліміті, усе завантаження —
     в межах тайм-ауту (`asyncio.timeout`) плюс тайм-аут з'єднання;
   - `file://` — лише строго всередині налаштованих коренів (**типово немає — вимкнено**): `file://host/…`, query,
     fragment, відносні, NUL, UNC/`\\?\` відхиляються; шлях спершу розв'язується (`..`, symlink), розв'язаний
     шлях перевіряється проти розв'язаних коренів, читається саме він — лише звичайний файл, `O_NOFOLLOW` (де є),
     на POSIX відкритий файл звіряється з перевіреним (`st_dev`/`st_ino`); розмір — до читання й під час;
   - `s3://` без `download_url` — 422 (облікових даних сховища в цих сервісів немає);
   - після читання: `size_bytes` blob (і до читання — проти ліміту) та `sha256`, якщо вказано;
   - помилки — `JaneError`: політика, невалідне посилання, невідповідність `sha256`/`size_bytes` — 422
     `validation_failed`; понад ліміт — 422 `limit_exceeded` (`details.path` — назва ліміту, `details.limit`);
     файла немає, `download_url` дав 404/410 — 404 `not_found`; мережа, тайм-аут, 5xx/408/429, I/O — 502
     `upstream_unavailable` (повторюваний); редирект, інший 4xx, закодоване тіло — 502 неповторюваний. `detail`
     не містить шляхів (ні заданих, ні розв'язаних) і вмісту; називає лише налаштування
     (`JANE_<СЕРВІС>_BLOB_ROOTS` / `_DOWNLOAD_HOST_ALLOWLIST`) і, для завантаження, `host:port`;
   - `parse_host_allowlist` — перевірка налаштування; сервіси викликають її у `field_validator`, тож опечатка
     зупиняє старт.
2. **llm** — `PackageLoader` (`package_archive`) і `LlmHandler` (`material.content`, `entities_ref`, `data_ref`)
   читають через `Settings.content_reader(limits.gateway)`; нові `JANE_LLM_BLOB_ROOTS`,
   `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST`; розміри — `gateway.max_data_part_bytes` / `gateway.max_package_bytes`,
   тайм-аут — `gateway.content_fetch_timeout_ms` (тепер на все завантаження). `read_content` вилучено.
3. **assistant** — `content.MaterialContent` (читач + `limits.content.max_material_bytes`); застосунок ставить його
   для кожного запиту ASGI-проміжною ланкою `MaterialContentScope` (contextvar), тож його успадковують job, які
   запит запускає (unknown materials, вдосконалення, вибірка онбордингу); поза застосунком `material_bytes` читає
   лише inline. Так зроблено, бо `unknown.py` (власність агента R-04 у цій сесії) викликає `material_bytes(material)`
   і його не можна було змінювати; `improvement.py`/`sampling.py` теж не змінено. Нові `JANE_ASSISTANT_BLOB_ROOTS`,
   `JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST`, ліміти `content.*` і `search.*`; `HttpJsonSearchProvider` бере
   тайм-аути з `limits.search` (раніше — 5 с httpx за замовчуванням).
4. **handler-runtime** — `ContentFetcher` — тонка обгортка над `ContentReader`: `file://` — ті самі
   `JANE_HANDLER_RUNTIME_BLOB_ROOTS` (тепер на розв'язаному шляху, лише звичайні файли), `download_url` — новий
   `JANE_HANDLER_RUNTIME_DOWNLOAD_HOST_ALLOWLIST` (типово `[]`), без редиректів і проксі середовища; тайм-аут —
   `timeouts.request_timeout_ms`, розміри — `packages.max_input_bytes` / `packages.max_archive_bytes`.
5. **Compose** (доповнення доручення, знахідка WP-12d — повторна обробка збереженого RAW у базовому стеку падала з
   `validation_failed`):
   - `infra/compose.yaml`: handler-runtime **і llm** монтують том `storage-data` **лише для читання** і мають
     `*_BLOB_ROOTS: '["/var/lib/jane/storage/objects"]'` — лише RAW-об'єкти адаптера файлів, а не його
     `deliveries`, `index`, `entities`, `history`, `locks` на тому ж томі. llm — бо `from_stage` повторної обробки
     може бути LLM-етапом (оркестратор передає збережений Material з persistent `file://` як є,
     `engine._feed_stored`). assistant RAW storage отримує inline (`/v1/objects/{id}/content`) — монтування не
     потрібне;
   - `deploy/profiles/compose.stack.yaml` — **без змін**: оверлей успадковує том і змінні бази (злиття compose за
     цільовим шляхом/ключем), перевірено рендером нижче; зайві рядки лише додали б конфлікт з агентом документації;
   - `tests/e2e/compose.e2e.yaml`: `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST` і `JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST` =
     `["package-host:8080"]` («шлюзи» R-04 WP-13r); корінь runtime звужено до `/var/lib/jane/storage/objects`.
     handler-runtime allowlist у e2e не потрібен (R-04 для runtime — повільний екстрактор, inline). Пакети з
     registry (`http://registry:8000`, WP-13t) llm і runtime беруть власними клієнтами registry, не через
     `ContentReader`/`download_url` — політика їх не зачіпає.

Зміни поведінки, про які варто знати: runtime — blob понад ліміт тепер 422 `limit_exceeded` (було 413
`payload_too_large`; 413 у контракті — про тіло запиту), редиректи `download_url` більше не виконуються;
assistant — `s3://` без `download_url` тепер 422 (було 501), невідповідність `sha256` — `validation_failed`
(було `digest_mismatch`, що в каталозі означає дайджест пакета); усі три — `download_url` типово вимкнено.

## Файли за власниками (`.claude/wp-paths.json`)

| Власник | Файли |
|---|---|
| WP-01 (`libs/jane-kit/**`, `infra/**`) | `libs/jane-kit/src/jane_kit/content.py` (новий), `libs/jane-kit/tests/test_content.py` (новий), `libs/jane-kit/README.md`, `infra/compose.yaml` |
| WP-10 (`services/llm/**`) | `src/jane_llm/{settings,packages,handler,app}.py`, `tests/test_content_policy.py` (новий), `README.md` |
| WP-11 (`services/assistant/**`) | `src/jane_assistant/{settings,content,search,app}.py`, `tests/test_content_policy.py` (новий), `tests/test_improvement.py` (+1 тест), `README.md` |
| WP-06 (`services/handler-runtime/**`) | `src/jane_handler_runtime/{settings,packages,runtime}.py`, `tests/test_content_policy.py` (новий), `README.md` |
| WP-13 (`tests/e2e/**`) | `tests/e2e/compose.e2e.yaml` |
| координатор | `docs/delivery/M3/01h-content-policy.md` (цей звіт) |

Не змінено: `services/llm/.../connections.py`, `providers/fake.py`, `services/assistant/.../unknown.py`,
`services/storage/**`, `deploy/profiles/compose.stack.yaml`. `check-diff main --wp NN` для будь-якого одного WP
показує файли інших власників — очікувано для наскрізного доручення.

## Тести (вимоги доручення → де)

| Випадок | jane-kit | llm | assistant | handler-runtime |
|---|---|---|---|---|
| `file:///proc/self/environ` (без коренів і з коренями) | `test_proc_self_environ_is_refused` | `test_file_uris_are_refused_by_default`, `…only_inside_the_roots` | `test_file_uris_are_refused_by_default`, `…only_inside_the_roots`, `test_improvement.py::test_problem_sample_content_follows_the_content_policy` | `test_file_uris_are_refused_by_default`, `…only_inside_the_roots` |
| шлях поза коренями | `test_paths_outside_the_roots_are_refused` | так | так | так |
| `..` (і `%2E%2E`) | так | так | так | так |
| symlink назовні (файл і каталог) | `test_symlink_out_of_a_root_is_refused` | так* | так* | так* |
| хост поза allowlist (інший порт, 169.254.169.254, userinfo, ftp/file, IPv6, фрагмент) | `test_download_hosts_outside_the_allowlist_are_refused_before_any_request` | так | так | так |
| редирект на інший хост (справжній HTTP; другий хост не отримує запиту) | `test_redirects_are_not_followed`, `test_real_http_ignores_proxy_env_and_redirects` | так | так | так |
| перевищення розміру (потік понад ліміт за заниженого `size_bytes`; `Content-Length`; задекларований `size_bytes`) | `test_download_size_limit_and_statuses`, `test_file_missing_size_and_digest` | `test_download_size_comes_from_gateway_limits` | `test_download_size_comes_from_content_limits` | `test_download_size_comes_from_package_limits` |
| дозволені `file://` і `download_url` — успіх | так | так (вміст дійшов до провайдера) | так (вміст дійшов до LLM) | так (екстрактор `success`) |
| тайм-аут, 404/5xx/403, gzip, base64, sha256 | так | — | тайм-аут пошуку з `limits.search` | — |

\* symlink-гілка сервісних тестів пропускається, якщо ОС не дає створити symlink (Windows без привілею); на цій
машині symlink створюються — пройшли всі. Відмова у сервісах також перевіряє, що провайдер/LLM не викликано і
відповідь не містить вмісту секретного файла.

## Команди перевірки та їхній вивід

Локально (Windows 11, Python 3.12.12), на перебазованій гілці:

```text
$ uv run ruff check .
All checks passed!
$ uv run ruff format --check .
420 files already formatted
$ uv run mypy libs/jane-kit/src libs/jane-kit/tests        (і так само для трьох сервісів)
Success: no issues found in 26 source files
Success: no issues found in 25 source files     # services/llm
Success: no issues found in 35 source files     # services/assistant
Success: no issues found in 24 source files     # services/handler-runtime
$ just test jane-kit
$ uv run --all-packages pytest libs\jane-kit -m not integration and not isolation
============================= 158 passed in 7.11s =============================
$ just test llm
$ uv run --all-packages pytest services\llm -m not integration and not isolation
====================== 62 passed, 39 deselected in 4.86s ======================
$ just test assistant
$ uv run --all-packages pytest services\assistant -m not integration and not isolation
====================== 73 passed, 5 deselected in 17.72s ======================
$ just test handler-runtime
$ uv run --all-packages pytest services\handler-runtime -m not integration and not isolation
===================== 48 passed, 13 deselected in 18.68s ======================
```

Попередній прогін `just test assistant` (до перебазування, паралельно зі збиранням образів Docker) мав одне падіння
`test_search_provider_timeout_comes_from_limits`: межа часу 2.5 с при сервері, що відповідає за 3 с, не витримала
навантаження хоста. Тест переписано без втрати сили: сервер відповідає за 10 с, тест перевіряє значення тайм-аутів
провайдера (`read=0.3`, `connect=5.0` з `limits.search`) і що відмова прийшла раніше за 4.5 с (типові 5 с httpx не
вклались би).

Рендер злитої конфігурації compose (`docker compose … config`, фіктивні значення обов'язкових змінних):

```text
base  handler-runtime volumes=['storage-data:/var/lib/jane/storage:ro'] env={'JANE_HANDLER_RUNTIME_BLOB_ROOTS': '["/var/lib/jane/storage/objects"]'}
base  llm             volumes=['storage-data:/var/lib/jane/storage:ro'] env={'JANE_LLM_BLOB_ROOTS': '["/var/lib/jane/storage/objects"]'}
e2e   handler-runtime volumes=['storage-data:/var/lib/jane/storage:ro'] env={'JANE_HANDLER_RUNTIME_BLOB_ROOTS': '["/var/lib/jane/storage/objects"]'}
e2e   llm             volumes=['storage-data:/var/lib/jane/storage:ro'] env={'JANE_LLM_BLOB_ROOTS': '["/var/lib/jane/storage/objects"]', 'JANE_LLM_DOWNLOAD_HOST_ALLOWLIST': '["package-host:8080"]'}
e2e   assistant       volumes=[] env={'JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST': '["package-host:8080"]'}
stack handler-runtime volumes=['storage-data:/var/lib/jane/storage:ro'] env={'JANE_HANDLER_RUNTIME_BLOB_ROOTS': '["/var/lib/jane/storage/objects"]'}
stack llm             volumes=['storage-data:/var/lib/jane/storage:ro'] env={'JANE_LLM_BLOB_ROOTS': '["/var/lib/jane/storage/objects"]'}
```

Smoke на dev-стеку лише з `infra/compose.yaml` (`just up --project jane-wp01h-smoke storage handler-runtime llm`,
власний проєкт; після перевірки `just down -v --project jane-wp01h-smoke`, контейнерів і томів не лишилось):
storage зберігає сторінку адаптером файлів (`raw-files`), `GET /v1/objects/{id}` повертає Material з persistent
`file:///var/lib/jane/storage/objects/…` без `download_url` — саме те, що оркестратор передає етапу при повторній
обробці; далі прямі виклики `handler.v1` runtime і llm з цим Material:

```text
1 storage store: 200 success
2 stored content: blob file:///var/lib/jane/storage/... False
3 runtime extract stored RAW: 200 success ['phone-alpha']
4 refusals:
  handler-runtime rt-env: 422 validation_failed | file:// content is outside the allowed roots (JANE_HANDLER_RUNTIME_BLOB_ROOTS)
  handler-runtime rt-dotdot: 422 validation_failed | file:// content is outside the allowed roots (JANE_HANDLER_RUNTIME_BLOB_ROOTS)
5 llm invocation on stored RAW: 200 empty
  llm llm-env: 422 validation_failed | file:// content is outside the allowed roots (JANE_LLM_BLOB_ROOTS)
  llm llm-dotdot: 422 validation_failed | file:// content is outside the allowed roots (JANE_LLM_BLOB_ROOTS)
  handler-runtime rt-deliveries: 422 validation_failed | file:// content is outside the allowed roots (JANE_HANDLER_RUNTIME_BLOB_ROOTS)
  llm llm-deliveries: 422 validation_failed | file:// content is outside the allowed roots (JANE_LLM_BLOB_ROOTS)
$ docker exec <runtime|llm> touch /var/lib/jane/storage/objects/x
touch: cannot touch '/var/lib/jane/storage/objects/x': Read-only file system     # обидва, uid 10001
```

(`empty` у llm — фейковий провайдер не знайшов подій на сторінці товару; важливо, що вміст прочитано, 200.)
Повну оркестровану повторну обробку (`/v1/reprocessing` → `succeeded`) на базовому dev-стеку не запускав: у базі
оркестратор без виконавців і без registry з опублікованим пакетом, це довге налаштування. Її покриває CI e2e
(S-M2-07, `tests/e2e/jane_e2e/assistant.py::reprocess` вимагає `succeeded`) на оверлеї, що успадковує ту саму базу
й тепер звужений корінь.

### CI

`git push origin wp/01h-content-ref-policy`, `gh workflow run ci --ref wp/01h-content-ref-policy` → run
[37846393926](https://github.com/sql-monk/Jane/actions/runs/37846393926) (`aa8c5de`, повний, з e2e).

Результат — **success**, усі завдання зелені (дані `gh run view 37846393926`):

```text
completed success aa8c5deae0fa07a4fe3e06bad29e568f6d21ebb2
lint: success          web: success          unit: success          contract: success      isolation: success
stack: success         limits: success       adapters (minio|mongodb|sqlserver|s3): success
e2e: success (2026-10-08T21:30:46Z - 2026-10-08T21:52:39Z)
$ just e2e -v
======================= 71 passed in 1300.73s (0:21:40) ========================
```

Серед них — сценарії, що читають вміст через нову політику: R-04 «шлюзи» `download_url` з `package-host:8080` у
llm (`test_r_04_llm_replay_while_invocation_is_running[sync|async]`), assistant
(`test_r_04_assistant_replay_while_unknown_material_job_is_running`) і storage; повторна обробка збереженого RAW
через `file:///var/lib/jane/storage/objects/…` у handler-runtime зі звуженим коренем
(`test_s_m2_07_improvement_activation_rollback_and_forbidden_auto_changes`,
`test_r_04_orchestrator_replay_while_run_and_reprocessing_are_active`); M1 і R-07 — без регресій. Пропущених тестів
у e2e немає. Запуск від push (`37846387987`) скасовано групою конкурентності на користь цього повного.

## Конфігурація й ліміти

| Параметр | Типово | Де |
|---|---|---|
| `JANE_LLM_BLOB_ROOTS` / `JANE_ASSISTANT_BLOB_ROOTS` / `JANE_HANDLER_RUNTIME_BLOB_ROOTS` | `[]` — `file://` вимкнено | налаштування сервісу (JSON-список); dev/deploy-стек: runtime і llm — `["/var/lib/jane/storage/objects"]` |
| `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST` / `JANE_ASSISTANT_…` / `JANE_HANDLER_RUNTIME_…` | `[]` — завантаження вимкнено | налаштування сервісу; e2e: llm і assistant — `["package-host:8080"]` |
| llm `gateway.max_data_part_bytes` / `max_package_bytes` / `content_fetch_timeout_ms` | 2000000 / 20000000 / 30000 | ліміти llm (без змін значень) |
| assistant `content.max_material_bytes` / `fetch_timeout_ms` / `connect_timeout_ms` | 16777216 / 30000 / 5000 | нові ліміти assistant |
| assistant `search.request_timeout_ms` / `connect_timeout_ms` | 10000 / 5000 | нові ліміти assistant |
| runtime `packages.max_input_bytes` / `max_archive_bytes`, `timeouts.request_timeout_ms` | 67108864 / 52428800, 30000 | ліміти runtime (без змін значень) |

## Відомі обмеження

- TOCTOU для проміжних каталогів шляху: якщо хтось із правом запису в корінь підмінить каталог на symlink між
  розв'язанням і відкриттям, останній компонент захищено (`O_NOFOLLOW` + звірка inode на POSIX), проміжні — ні.
  У стеках корінь — том лише для читання, пише в нього тільки storage.
- Корінь `objects/` дає будь-якому викликачеві `handler.v1` runtime/llm прочитати RAW **будь-якого** джерела з тома
  (за `file://`-посиланням). Межа довіри — автентифікація викликачів (паралельний агент автентифікації); до неї
  ці ендпоінти й так приймають будь-який вміст.
- Рядки `deploy/profiles/compose.stack.yaml` не додано (успадкування з бази); якщо оверлей колись перевизначить
  `volumes`/змінні runtime чи llm повністю, корінь треба буде повторити там.
- Сторонній blob-store з `download_url`, що віддає `Content-Encoding: gzip` або редирект на CDN, буде відхилено
  (502, неповторюваний) — свідомо; потрібен прямий presigned URL.

## Неперевірені інтеграції

- Справжні presigned URL MinIO/S3 через `download_url` — не перевірено на реальному сервісі (жоден сервіс Jane
  їх зараз не видає); перевірено на локальних HTTP-серверах і `MockTransport`.
- Шлях вибірки онбордингу з blob-вмістом матеріалів колектора — окремим тестом не покрито (фейковий колектор
  віддає inline); той самий механізм (`MaterialContentScope` → job) доведено тестами unknown materials і
  вдосконалення.
- Оркестрована повторна обробка на базовому dev-стеку — див. вище (лише прямі виклики; оркестрований шлях — CI e2e).

## Запити до інших власників

| Кому | Що | Навіщо |
|---|---|---|
| WP-07 (storage) / координатор | у базовому стеку storage не має `JANE_STORAGE_CONTENT_FILES_DIR`; якщо етап збереження після `from_stage` отримає persistent `file://` RAW, storage його відхилить | узгодити, чи такий маршрут можливий; інакше лишити як є |
| агент автентифікації | `handler.v1` runtime і llm тепер читають RAW з тома; доступ має обмежуватись автентифікованими викликачами | межа довіри для `file://` з `objects/` |
| WP-13 | `tests/e2e/compose.e2e.yaml`: allowlist llm/assistant, корінь runtime звужено до `objects/` | у вашій власності, зміни мінімальні |
| агент документації | ті самі compose-файли: мої рядки — лише змінні `*_BLOB_ROOTS`/`*_DOWNLOAD_HOST_ALLOWLIST` і том `storage-data:ro` у runtime/llm бази | зведення конфліктів |
