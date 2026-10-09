# Матриця приймання: 13 критеріїв ТЗ §12

Стан інтеграційної гілки `codex/jane-integration` на 2026-10-09. Процедури й межі сценаріїв —
[scenarios.md](scenarios.md), код — [`tests/e2e/`](../../tests/e2e), UI —
[`web/admin/e2e/`](../../web/admin/e2e). Зведено за дорученням B-5; історія перевірок лишається у звітах WP.
Блок «Фінальна ревізія» фіксує прийнятий M3; нові докази наведено окремо в розділі «Після M3».

## Фінальна ревізія

**M3 прийнято 2026-10-09** на зведеній ревізії з B2, WP-06d і B-11.

- SHA коду: `77c58905de860c68dfceaf2beadf7496afc3f95d`.
- [Фінальний CI 37865985595](https://github.com/sql-monk/Jane/actions/runs/37865985595) — **13/13 job success**.
- [Job e2e](https://github.com/sql-monk/Jane/actions/runs/37865985595/job/113614524271):
  `75 passed in 1453.72s (0:24:13)`, 75 явних PASSED, 0 skipped/xfailed/failed, `JANE_E2E_REQUIRED=1`.
- [Limits](https://github.com/sql-monk/Jane/actions/runs/37865985595/job/113614524251): профіль `ci`,
  **verdict: warn** лише L1 single-gap jitter `0.013882637023925781 s < 0.015 s`; решта L1–L8 — ok.
- Real-адмінка B-11: 16 passed / 1 failed у повному прогоні на `7eed2e1`; після виправлення Bearer
  одного тесту — 1 passed на `48af2a1`. Сукупно всі 17 real-сценаріїв підтверджено; межі наведено нижче.
- [Незалежне фінальне рев'ю C-4](../delivery/M3/final-review-delta.md#дельта-2)
  `d37c522..19d58a1`: нових блокерів M3 немає. B1/B2 закрито.
- [C-2: чистий клон після B2](../delivery/M3/final-review-delta.md#відтворення-після-b2), `b3b1101`:
  8 healthy сервісів; health 200, info без ключа 401 / із ключем 200; admin assets 200;
  demo ok:true, 23 RAW / 16 сутностей і 4 оновлення цін; записаний Telegram ok:true, 5 RAW / 3 події.
  Власні стеки прибрано. Браузерну межу C-N4 закрито real-входом B-11.

Після перевіреного SHA змінено лише документи: **код ідентичний `77c58905de860c68dfceaf2beadf7496afc3f95d`**.
Прийнятий стан із цими документами — тег `codex/m3-2026-10-09`; fast-forward у `main` виконує людина.
[Команди й вивід фінального gate](../delivery/M3/final-gate.md). Позначення замінників і відомі межі
збережено; реальні LLM/IdP/AWS та неперевірені профілі не оголошено перевіреними.

## Після M3

Оновлення WP-20/WP-21 і прийнятий B-2 на 2026-10-09 доповнюють історичний стан M3.
[CI 37905643300](https://github.com/sql-monk/Jane/actions/runs/37905643300) гілки
`wp/21-post-m3-followups` на `f69854e429cedf71a6eedfb03897f7518a0da9c5` — **completed / success**;
[job e2e](https://github.com/sql-monk/Jane/actions/runs/37905643300/job/113740900134):
`77 passed in 1435.40s (0:23:55)`, `JANE_E2E_REQUIRED=1`. R-03 і S-M3-01/02 мають явні рядки **PASSED**.

| Сценарій / критерії ТЗ §12 | Додатковий спостережуваний доказ | Стан і джерело |
|---|---|---|
| S-M2-10 / 4, 6, 7 (UI) | R26 і B-2: примітка людини, точні RAW приклади групи й ручні id запуску, retry timestamps, фільтри вдосконалення | WP-20: **25 повністю / 0 частково / 1 навмисний мок із 26**, історичний real18; B-2: **4 нові @hybrid пройшли локально**, структурний real-набір — **22**, повний інтеграційний CI очікується після B-5; [WP-20](../delivery/WP-20.md#команди-перевірки-та-їхній-вивід), [B-2 accepted](../delivery/post-m3/stream-b.md#b-2-accepted), подробиці нижче |
| R-03 / 8 | `attempt_history` і `available_at` доводять причинність повторів: `claimed` → `retry_scheduled` → наступне `claimed` → `completed`; затримки 3000/6000 мс, взяття не раніше `available_at`, та сама історія в trace | CI 37905643300 / `test_r_03_partition_to_storage_isolated_retry_waits_for_backoff_without_duplicates PASSED`; [межі перевірки](scenarios.md#надійність) |
| S-M3-01 / 6 | `stored_materials.object_ids` вибирає рівно два задані RAW-спостереження в заданому порядку; RAW не дублюються, історія результату посилається на вибране спостереження; відсутній id → `not_found` | CI 37905643300 / `test_s_m3_01_reprocessing_takes_exactly_the_given_stored_objects PASSED`; Р, [сценарій](scenarios.md#s-m3-01-повторна-обробка-точно-вибраних-raw) |
| S-M3-02 / 1, 12 | JSON-RAW Telegram відновлює початковий `material.content`; повторна обробка у `format.raw: original` зберігає `text/plain` з байтами, розміром і `sha256` матеріалу колектора | CI 37905643300 / `test_s_m3_02_telegram_json_raw_is_restored_and_reprocessed_with_its_sha256 PASSED`; Р, Telegram backend — З; [сценарій і тимчасові обходи](scenarios.md#s-m3-02-telegram-json-raw-відновлення-й-той-самий-sha256) |

У S-M3-02 ще збережено очікування `connections_synced` перед прямим записом і пряме HTTP-читання
`text/plain` поза ContractClient — явні межі [WP-21](../delivery/WP-21.md#рішення); їх усунення — окремий B-5 після WP-19.
За [спільними правилами після M3](../delivery/post-m3/README.md#спільні-правила-для-всіх-потоків)
`dev-laptop` і `single-node` **виключено з обсягу повністю**; історичні позначки M3 нижче не є відкритою роботою.

## Як читати докази

- **Р** — реальні сервіси Jane та інфраструктура: PostgreSQL, SQL Server, MongoDB, MinIO, Docker, Caddy.
- **З** — замінник зовнішньої системи: провайдер LLM `fake`, записаний Telegram backend, пошук `static`,
  SeaweedFS замість AWS S3. Сервіс Jane, що звертається до замінника, працює реально.
- **Т** — тимчасовий замінник компонента Jane; у поточних доказах після WP-13t таких замінників немає.
  Пакети оркестрованих сценаріїв публікуються в реальному registry, адресуються версією й дайджестом.
  `package-host` лише утримує зовнішній blob `download_url` у R-04 (**З**), архівів пакетів не віддає.
- Матеріал, який сторонній клієнт формує з testsite і подає безпосередньо виконавцю, — вхід прямого
  виклику (S-M2-05a, частина R-04). Він перевіряє автономність виконавця; поведінку Web Collector ним не доводимо.

Фінальний повний e2e на зведеній ревізії з усіма прийнятими інкрементами:
[CI 37865985595](https://github.com/sql-monk/Jane/actions/runs/37865985595) на `77c5890`, усі 13 job success;
рядок [job e2e](https://github.com/sql-monk/Jane/actions/runs/37865985595/job/113614524271):
`75 passed in 1453.72s (0:24:13)`, без skip/xfail, `JANE_E2E_REQUIRED=1`.
У таблиці **CI 37865985595 / PASSED** означає явний рядок відповідного тесту в цьому job.
WP-13s інтегровано злиттям `86cdece`; пізніші виправлення мають окремі докази у
[журналі потоку B](../delivery/M3/stream-b.md).

## Критерії 1–13

| № | Спостережувана вимога | Сценарії / рядок e2e | Актуальний стан і доказ | Перевірка |
|---|---|---|---|---|
| 1 | Колектор та екстрактор автономні, доступні сторонньому клієнту | S-M1-01/02/04, S-M2-02; `test_s_m1_04_collector_and_extractor_used_by_a_third_party_app PASSED` | Реалізовано; CI 37865985595 / PASSED. Прямі API й CLI без оркестратора | Р; Telegram — З |
| 2 | Ланцюжок з розгалуженням, екстракцією й збереженням | S-M1-01/03, S-M2-11; `test_s_m2_11_conditional_branches_and_llm_on_problem_results PASSED` | Реалізовано; CI 37865985595 / PASSED. Умови `when`, лише проблемні результати в LLM, валідація виходу та trace | Р; LLM — З |
| 3 | Зміна сховища конфігурацією без зміни коду колектора/екстрактора | S-M1-05, S-M2-08; `test_s_m2_08_all_storage_adapters_via_task_revision PASSED` | Реалізовано; CI 37865985595 / PASSED. Те саме завдання працює з усіма шістьма адаптерами | Р; AWS S3 — З |
| 4 | Підготовка екстрактора через LLM для нового джерела | S-M2-06, S-M2-10 (R26 UI); `test_s_m2_06_name_only_sample_distinguishes_material_types PASSED`, `test_s_m2_06_name_and_crawl_hints_to_extractor_source_task_and_entities PASSED` | Реалізовано; CI 37865985595 / обидва PASSED. Вибірка, пропозиції, пакет, тести й виконання прийнятого завдання; після M3 WP-20 підтвердив цей цикл і в UI | Р; LLM і пошук — З |
| 5 | Повний збір товарів і перевірка цін — окремі завдання | S-M2-04; `test_s_m2_04_catalog_and_scheduled_price_check_are_separate_tasks PASSED` | Реалізовано; CI 37865985595 / PASSED. Ціну змінює штатний testsite, історія спостережень збережена | Р |
| 6 | Вдосконалення на проблемних прикладах, тести й відкат | S-M2-07, R-07; `test_s_m2_07_improvement_activation_rollback_and_forbidden_auto_changes PASSED` | Реалізовано; CI 37865985595 / PASSED, усі п'ять R-07 PASSED. UI: S-M2-10, межі нижче | Р; LLM — З |
| 7 | Форк незмінний після оновлення батька, перенесення змін явне | S-M2-01, S-M2-10; `test_registry_packages_runtime_and_fork PASSED` | Реалізовано; CI 37865985595 / PASSED; UI fork/upstream, diff, активація й відкат підтверджені WP-12d | Р; LLM-пакет — З провайдера |
| 8 | Збої, повторна доставка, кілька екземплярів без дублювання | S-M1-01/02/06, R-01…R-08; `test_r_01_lease_lost_during_active_call_taken_over_with_409_without_spent_attempt PASSED` | Реалізовано; CI 37865985595 / усі R-01…R-08 PASSED. R-02/R-06 охоплюють усі 8 сервісів; R-04 — усіх виконавців, включно з completions/onboarding/improvement | Р; зовнішні LLM/Telegram/blob — З |
| 9 | Пакети різних типів, фіксовані версії та незалежні форки | S-M2-01; `test_storage_fork_pinned_in_a_task_runs_that_fork PASSED`, `test_llm_package_from_registry_runs_in_tasks_and_its_fork_stays_pinned PASSED`, `test_collector_rules_fork_pinned_in_a_source_keeps_its_rules PASSED` | Реалізовано; CI 37865985595 / PASSED. Реальний registry, завантаження й перевірка дайджестів виконавцями | Р; LLM — З |
| 10 | Рекурсія, Sitemap та інші стратегії окремо й разом | S-M1-04, S-M2-03; `test_s_m2_03_each_strategy` (recursive, sitemap, feeds, categories, search, api, template — 7 PASSED), `test_s_m2_03_strategy_combinations` (3 PASSED) | Реалізовано; CI 37865985595 / 10 S-M2-03 PASSED; очікувані URL штатного testsite | Р |
| 11 | Невідома сторінка потрапляє в LLM лише з увімкненим прапорцем | S-M1-03, S-M2-05a/05; `test_s_m2_05_unknown_pages_reach_llm_only_after_the_flag_is_enabled PASSED` | Реалізовано; CI 37865985595 / PASSED. Окремий injection-сценарій PASSED доводить маршрутизацію даних; стійкість реального провайдера до ін'єкції не підтверджує | Р; LLM — З |
| 12 | RAW і сутності зберігає кожен початковий адаптер | S-M1-01, S-M2-08; `test_s_m2_08_all_storage_adapters_via_task_revision PASSED` | Реалізовано; CI 37865985595 / PASSED. files, PostgreSQL, SQL Server, MongoDB, MinIO, S3; читання через storage API | Р; AWS S3 — З |
| 13 | Ліміти змінюються без коду; профіль підтримуваного середовища виміряний | S-M2-09, R-08; `test_s_m2_09_platform_and_task_page_limits_apply_without_rebuild PASSED`; limits harness L1–L8 | Реалізовано; CI 37865985595 / PASSED. `ci` прийнято наживо за рішенням людини 2026-10-08; найсвіжіший завершений limits job: CI 37865985595, `verdict: warn` (деталі нижче) | Р; LLM/Telegram/S3 у harness — З; інші профілі — кандидати |

## R-04: повтор під час активної роботи

У [CI 37865985595](https://github.com/sql-monk/Jane/actions/runs/37865985595/job/113614524271) усі перелічені
рядки — **PASSED**. API сервісів реальні. Повтор не збільшує кількість матеріалів, пісочниць, RAW,
версій, запусків чи витрати LLM. Async повертає ту саму job; sync — 409, потім збережений результат;
інше тіло з тим самим ключем — 422. Деталі активного вікна — [сценарії](scenarios.md#надійність).

| Виконавець | Тест / режим |
|---|---|
| Web Collector | `test_r_04_web_replay_while_collection_is_running` у `test_r04_idempotency.py` |
| Telegram Collector | `test_r_04_telegram_replay_while_collection_is_running` |
| handler-runtime | `test_r_04_runtime_replay_while_invocation_is_running[sync/async]` |
| storage | `test_r_04_storage_replay_while_write_is_running` (sync) |
| llm | `test_r_04_llm_replay_while_invocation_is_running[sync/async]`; WP-13s: `test_r_04_llm_completion_replay_while_provider_call_is_running[sync/async]` |
| registry | `test_r_04_registry_replay_while_port_job_and_publication_are_running` |
| assistant | `test_r_04_assistant_replay_while_unknown_material_job_is_running`; WP-13s: `test_r_04_assistant_replay_while_onboarding_job_is_running`, `test_r_04_assistant_replay_while_improvement_job_is_running` |
| orchestrator | `test_r_04_orchestrator_replay_while_run_and_reprocessing_are_active` |

Рядки, крім Web Collector, — у [`test_r04_active_replays.py`](../../tests/e2e/test_r04_active_replays.py).
Для sync completions 409 заданий загальною конвенцією, але явно відсутній у відповіді OpenAPI цього endpoint:
тест перевіряє тіло Problem напряму; запит WP-00 збережено в [беклозі](../delivery/M3/open-requests.md).
R-07 має окрему межу: активна пісочниця кандидата в мить kill не підтверджена; критерії рестарту й
одиничного опублікування підтверджені, точний момент виконання кандидата — ні.

## S-M2-10: адмінка на реальному API

Історичний результат [WP-20](../delivery/WP-20.md#запити-до-інших-власників): **25 повністю / 0 частково / 1 навмисний мок**
із 26 сценаріїв. №10 став повним після R26: real `hybrid-assistant-onboarding` перевіряє уточнення,
пропозиції з покриттям, вартістю й ризиками, прийняття та відновлення після reload; backend-цикл — S-M2-06.
Навмисний мок — №18: відповідь несправного сервісу з секретом, яку справний сервіс не повертає.
Перехоплення цієї відповіді явно позначене. Історичний стан WP-12d/M3 — 24/1/1.

У WP-20 real-набір містив **18 сценаріїв** (було 17): повний прогін на `3a3251c` — `18 passed (4.6m)`,
exit 0. На `df7f252` підтверджено всі 18: 16 незмінених — у повному прогоні, дві змінені специфікації —
в адресних контролях; нові assertions додано, код UI та інші 16 сценаріїв тотожні. Точні команди,
вивід і межі — [WP-20](../delivery/WP-20.md#команди-перевірки-та-їхній-вивід).

WP-20 також додав 9 `@mock`-сценаріїв №27–35 у `post-m3.spec.ts`. Його історична
[таблиця покриття](../delivery/WP-20.md#неперевірені-інтеграції) фіксувала 5 повністю real і 4 частково
(№30–33), а в №29 окремо лишалися фільтри `package_id` / `status`. Прийнятий
[B-2](../delivery/post-m3/stream-b.md#b-2-accepted), `ffc691423ea16463c1665af177ff7164cca8ee67`,
закрив ці межі чотирма новими `@hybrid` у
[`hybrid-post-m3.spec.ts`](../../web/admin/e2e/hybrid-post-m3.spec.ts) через Caddy та реальні API:

| Межа WP-20 | Новий спостережуваний доказ B-2 |
|---|---|
| №30: примітка людини; №31: RAW приклади групи | `PATCH {note}`, реальний list readback і reload; кнопка групи передає точний `stored_materials.object_ids`, повторно обробляється лише вибраний приклад |
| №33: ручні id зі сторінки запуску | окремі `object_ids` і `observation_ids`, точне тіло POST, успішний reprocessing run; контрольний RAW виключено |
| №29: фільтри вдосконалення | два реальні jobs різних пакетів, правильні `package_id` / `status` у query; чужий пакет і невідповідний статус відсутні |
| №32: повтор і час доступності | реальний LLM gateway із зовнішнім `fake` провайдером `error: unavailable`: `retry_scheduled`, затримка 1000 мс, `available_at`, наступний claim не раніше цього часу; точні timestamps і код у UI |

Локально нові 4 сценарії дали `4 passed (3.3m)`, exit 0. Windows Edge teardown завис після
чотирьох `ok`: завершено лише власний worker, після чого Playwright надрукував підсумок і завершився
з кодом 0. Це явне обмеження локального runner; штатне завершення браузера не підтверджено.
Власний стек прибрано, контейнерів / томів / мереж проєкту залишилося 0; незалежний wp-reviewer
прийняв B-2 у раунді 1. Повний локальний real22 не запускався: **22 — структурний розмір набору**,
а `18 passed` лишається історичним доказом WP-20.

[Branch CI 37914973286](https://github.com/sql-monk/Jane/actions/runs/37914973286) на `ffc6914` —
**completed / success** (read-only перевірка 2026-10-09); він не є доказом повного real22.
Повний інтеграційний CI потоку ще очікується після B-5.

Нижче збережено попередні докази M3 для історії.

WP-12d інтегровано `bf69429`; B-11 (B-7/B-8/B-9) — `97ea4c4`. Real-набір працював через Caddy з усіма
8 API на зведеній ревізії з B2 і WP-06d. Ключ входу взято зі стек-файлу цього самого compose-проєкту.
Докази й незалежна звірка — [журнал B, четверта черга](../delivery/M3/stream-b.md#четверта-черга),
[C-4, дельта 2](../delivery/M3/final-review-delta.md#дельта-2).

- Повний real-прогін на `7eed2e18799ad8ae36c40ca48b8b004f9943fdb3`: `16 passed (4.1m), 1 failed`.
  Відмова одного тесту registry — прямі GET без Bearer після прийнятого B2, HTTP 401.
- Після додавання Bearer до трьох GET цього тесту, на `48af2a1bdf075a27f1568fbc2d5ca088ec03d65d`:
  адресний контроль `1 passed (26.9s), exit 0`. Усі попередні assertions збережено й додано перевірки HTTP 200.
- Сукупно підтверджено всі 17 real-сценаріїв. Код UI/сервісів, wrapper, fixture й інші 16 тестів між
  ревізіями тотожні; пізніше форматування не змінює виразів. Це два докази 16 + 1, повний прогін лишається 16/1.

Браузерний вхід за стековим ключем цим підтверджено, C-N4 закрито. Dev-ключ не міститься в HTML, URL чи
localStorage; sessionStorage дозволений чинним ADR-0005 (C-N6). Після WP-20 покриття — 25/0/1 із 26.
Навмисні виключення real-тестів із `web-mock-e2e` не є skip у обов'язковому сервісному e2e.

## Критерій 13: рішення щодо профілів

Рішення людини **2026-10-08** — [WP-14](../delivery/WP-14.md): `dev-laptop` ×3 не входить до фінального M3.

| Профіль | Стан | Доказ / межа |
|---|---|---|
| `ci` | **Прийнято наживо** | [CI 37811082079](https://github.com/sql-monk/Jane/actions/runs/37811082079) на `d37c522`: `pass`; фінальний [limits job CI 37865985595](https://github.com/sql-monk/Jane/actions/runs/37865985595/job/113614524251) на `77c5890`: `verdict: warn`, лише L1 single-gap jitter 0.013882637023925781 s < 0.015 s; решта L1–L8 — ok. Job success; `warn` зберігаємо як попередження, не називаємо `pass` |
| `dev-laptop` | Кандидат, **не перевірено на реальному середовищі** | Живе вимірювання виключено рішенням людини; значення довідкові |
| `single-node` | Кандидат, **не перевірено на реальному середовищі** | Немає порогів harness і живих прогонів |

Артефакт новішого limits job: `limits-ci-37865985595-1`, каталог вимірювання `.jane/limits/ci-20261009T004740Z`.
CI 37865985595 завершився success: 13/13 job, e2e `75 passed in 1453.72s (0:24:13)`; фінальний gate M3 закрито.

## Не перевірено на реальних сервісах

- Реальні LLM-провайдери: мережа, модель, оплата й стійкість до prompt injection; приймання використовує `fake`.
- AWS S3: перевірено сумісний API SeaweedFS (**З**); MinIO працює як реальна окрема інфраструктура.
- OIDC/JWT з реальним IdP: перевірки конфігурації/токенів не замінюють інтеграцію з живим IdP.
- Telegram: [WP-04](../delivery/WP-04.md) вручну перевірив реальні канали, історію, нове повідомлення й редагування,
  інкрементальний курсор та replay. Автоматичний e2e використовує записаний backend (**З**); реальні flood-wait,
  медіа, kill посеред роботи й кілька екземплярів на живому Telegram не перевірені.
- Профілі `dev-laptop` і `single-node`: **не перевірено на реальному середовищі**, статус кандидатів наведено вище.
