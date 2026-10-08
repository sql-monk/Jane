# Матриця приймання: 13 критеріїв ТЗ §12

Стан інтеграційної гілки `codex/jane-integration` на 2026-10-09. Процедури й межі сценаріїв —
[scenarios.md](scenarios.md), код — [`tests/e2e/`](../../tests/e2e), UI —
[`web/admin/e2e/`](../../web/admin/e2e). Зведено за дорученням B-5; історія перевірок лишається у звітах WP.

## Фінальна ревізія

Потік A заповнює цей блок після фінального CI на зведеній ревізії:

- SHA: `<SHA>`.
- CI: `<CI run>`.
- Підсумок e2e: `<рядок e2e>`.

Наведені нижче докази підтверджують інтегровані інкременти на вказаних SHA. Цей блок фіксує окреме
остаточне приймання M3; до його заповнення не приписуємо попередні прогони новішій ревізії.

## Як читати докази

- **Р** — реальні сервіси Jane та інфраструктура: PostgreSQL, SQL Server, MongoDB, MinIO, Docker, Caddy.
- **З** — замінник зовнішньої системи: провайдер LLM `fake`, записаний Telegram backend, пошук `static`,
  SeaweedFS замість AWS S3. Сервіс Jane, що звертається до замінника, працює реально.
- **Т** — тимчасовий замінник компонента Jane; у поточних доказах після WP-13t таких замінників немає.
  Пакети оркестрованих сценаріїв публікуються в реальному registry, адресуються версією й дайджестом.
  `package-host` лише утримує зовнішній blob `download_url` у R-04 (**З**), архівів пакетів не віддає.
- Матеріал, який сторонній клієнт формує з testsite і подає безпосередньо виконавцю, — вхід прямого
  виклику (S-M2-05a, частина R-04). Він перевіряє автономність виконавця; поведінку Web Collector ним не доводимо.

Останній завершений повний e2e, що включає WP-13s:
[CI 37853683903](https://github.com/sql-monk/Jane/actions/runs/37853683903) на `cdf261a`, усі 12 job success;
рядок [job e2e](https://github.com/sql-monk/Jane/actions/runs/37853683903/job/113574852651):
`75 passed in 1486.98s (0:24:46)`, без skip/xfail, `JANE_E2E_REQUIRED=1`.
У таблиці **CI 37853683903 / PASSED** означає явний рядок відповідного тесту в цьому job.
WP-13s інтегровано злиттям `86cdece`; пізніші виправлення мають окремі докази у
[журналі потоку B](../delivery/M3/stream-b.md).

## Критерії 1–13

| № | Спостережувана вимога | Сценарії / рядок e2e | Актуальний стан і доказ | Перевірка |
|---|---|---|---|---|
| 1 | Колектор та екстрактор автономні, доступні сторонньому клієнту | S-M1-01/02/04, S-M2-02; `test_s_m1_04_collector_and_extractor_used_by_a_third_party_app PASSED` | Реалізовано; CI 37853683903 / PASSED. Прямі API й CLI без оркестратора | Р; Telegram — З |
| 2 | Ланцюжок з розгалуженням, екстракцією й збереженням | S-M1-01/03, S-M2-11; `test_s_m2_11_conditional_branches_and_llm_on_problem_results PASSED` | Реалізовано; CI 37853683903 / PASSED. Умови `when`, лише проблемні результати в LLM, валідація виходу та trace | Р; LLM — З |
| 3 | Зміна сховища конфігурацією без зміни коду колектора/екстрактора | S-M1-05, S-M2-08; `test_s_m2_08_all_storage_adapters_via_task_revision PASSED` | Реалізовано; CI 37853683903 / PASSED. Те саме завдання працює з усіма шістьма адаптерами | Р; AWS S3 — З |
| 4 | Підготовка екстрактора через LLM для нового джерела | S-M2-06; `test_s_m2_06_name_only_sample_distinguishes_material_types PASSED`, `test_s_m2_06_name_and_crawl_hints_to_extractor_source_task_and_entities PASSED` | Реалізовано; CI 37853683903 / обидва PASSED. Вибірка, пропозиції, пакет, тести й виконання прийнятого завдання | Р; LLM і пошук — З |
| 5 | Повний збір товарів і перевірка цін — окремі завдання | S-M2-04; `test_s_m2_04_catalog_and_scheduled_price_check_are_separate_tasks PASSED` | Реалізовано; CI 37853683903 / PASSED. Ціну змінює штатний testsite, історія спостережень збережена | Р |
| 6 | Вдосконалення на проблемних прикладах, тести й відкат | S-M2-07, R-07; `test_s_m2_07_improvement_activation_rollback_and_forbidden_auto_changes PASSED` | Реалізовано; CI 37853683903 / PASSED, усі п'ять R-07 PASSED. UI: S-M2-10, межі нижче | Р; LLM — З |
| 7 | Форк незмінний після оновлення батька, перенесення змін явне | S-M2-01, S-M2-10; `test_registry_packages_runtime_and_fork PASSED` | Реалізовано; CI 37853683903 / PASSED; UI fork/upstream, diff, активація й відкат підтверджені WP-12d | Р; LLM-пакет — З провайдера |
| 8 | Збої, повторна доставка, кілька екземплярів без дублювання | S-M1-01/02/06, R-01…R-08; `test_r_01_lease_lost_during_active_call_taken_over_with_409_without_spent_attempt PASSED` | Реалізовано; CI 37853683903 / усі R-01…R-08 PASSED. R-02/R-06 охоплюють усі 8 сервісів; R-04 — усіх виконавців, включно з completions/onboarding/improvement | Р; зовнішні LLM/Telegram/blob — З |
| 9 | Пакети різних типів, фіксовані версії та незалежні форки | S-M2-01; `test_storage_fork_pinned_in_a_task_runs_that_fork PASSED`, `test_llm_package_from_registry_runs_in_tasks_and_its_fork_stays_pinned PASSED`, `test_collector_rules_fork_pinned_in_a_source_keeps_its_rules PASSED` | Реалізовано; CI 37853683903 / PASSED. Реальний registry, завантаження й перевірка дайджестів виконавцями | Р; LLM — З |
| 10 | Рекурсія, Sitemap та інші стратегії окремо й разом | S-M1-04, S-M2-03; `test_s_m2_03_each_strategy` (recursive, sitemap, feeds, categories, search, api, template — 7 PASSED), `test_s_m2_03_strategy_combinations` (3 PASSED) | Реалізовано; CI 37853683903 / 10 S-M2-03 PASSED; очікувані URL штатного testsite | Р |
| 11 | Невідома сторінка потрапляє в LLM лише з увімкненим прапорцем | S-M1-03, S-M2-05a/05; `test_s_m2_05_unknown_pages_reach_llm_only_after_the_flag_is_enabled PASSED` | Реалізовано; CI 37853683903 / PASSED. Окремий injection-сценарій PASSED доводить маршрутизацію даних; стійкість реального провайдера до ін'єкції не підтверджує | Р; LLM — З |
| 12 | RAW і сутності зберігає кожен початковий адаптер | S-M1-01, S-M2-08; `test_s_m2_08_all_storage_adapters_via_task_revision PASSED` | Реалізовано; CI 37853683903 / PASSED. files, PostgreSQL, SQL Server, MongoDB, MinIO, S3; читання через storage API | Р; AWS S3 — З |
| 13 | Ліміти змінюються без коду; профіль підтримуваного середовища виміряний | S-M2-09, R-08; `test_s_m2_09_platform_and_task_page_limits_apply_without_rebuild PASSED`; limits harness L1–L8 | Реалізовано; CI 37853683903 / PASSED. `ci` прийнято наживо за рішенням людини 2026-10-08; найсвіжіший завершений limits job: CI 37853683903, `verdict: warn` (деталі нижче) | Р; LLM/Telegram/S3 у harness — З; інші профілі — кандидати |

## R-04: повтор під час активної роботи

У [CI 37853683903](https://github.com/sql-monk/Jane/actions/runs/37853683903/job/113574852651) усі перелічені
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

[WP-12d, остаточна таблиця](../delivery/WP-12.md): **24 повністю / 1 частково / 1 навмисний мок** із 26
сценаріїв. Частково — №10 (уточнення, пропозиції й прийняття onboarding у UI); наскрізний backend-цикл
окремо проходить S-M2-06. Навмисний мок — №18: відповідь несправного сервісу з секретом, яку справний
сервіс не повертає. Перехоплення цієї відповіді явно позначене.

WP-12d інтегровано `bf69429`. [CI 37850908072](https://github.com/sql-monk/Jane/actions/runs/37850908072)
на `d5d8efc`: `web-mock-e2e` — `29 passed (35.0s), 14 skipped` (real-тести тут виключені).
Останній адресний real-контроль через Caddy на backend `69ab303`: `1 passed (33.6s), exit 0`,
`reprocessing one stored material takes only RAW of the task's source`; `test.fail` знято у `b6777fb`.
Повний real-прогін на зведеній ревізії з B2 — B-7; підсумок і SHA записуються в
[журналі потоку B](../delivery/M3/stream-b.md). Попередні локальні прогони та їхні межі — у WP-12.

## Критерій 13: рішення щодо профілів

Рішення людини **2026-10-08** — [WP-14](../delivery/WP-14.md): `dev-laptop` ×3 не входить до фінального M3.

| Профіль | Стан | Доказ / межа |
|---|---|---|
| `ci` | **Прийнято наживо** | [CI 37811082079](https://github.com/sql-monk/Jane/actions/runs/37811082079) на `d37c522`: `pass`; найсвіжіший завершений [limits job CI 37853683903](https://github.com/sql-monk/Jane/actions/runs/37853683903/job/113574852621) на `cdf261a`: `verdict: warn`, попередження L2 (два збори на один хост). Job success; `warn` зберігаємо як попередження, не називаємо `pass` |
| `dev-laptop` | Кандидат, **не перевірено на реальному середовищі** | Живе вимірювання виключено рішенням людини; значення довідкові |
| `single-node` | Кандидат, **не перевірено на реальному середовищі** | Немає порогів harness і живих прогонів |

Артефакт новішого limits job: `limits-ci-37853683903-1`, каталог вимірювання `.jane/limits/ci-20261008T223500Z`.
CI 37853683903 завершився success: 12/12 job, e2e `75 passed in 1486.98s (0:24:46)`; фінальний gate новішої зведеної ревізії лишається потоку A.

## Не перевірено на реальних сервісах

- Реальні LLM-провайдери: мережа, модель, оплата й стійкість до prompt injection; приймання використовує `fake`.
- AWS S3: перевірено сумісний API SeaweedFS (**З**); MinIO працює як реальна окрема інфраструктура.
- OIDC/JWT з реальним IdP: перевірки конфігурації/токенів не замінюють інтеграцію з живим IdP.
- Telegram: [WP-04](../delivery/WP-04.md) вручну перевірив реальні канали, історію, нове повідомлення й редагування,
  інкрементальний курсор та replay. Автоматичний e2e використовує записаний backend (**З**); реальні flood-wait,
  медіа, kill посеред роботи й кілька екземплярів на живому Telegram не перевірені.
- Профілі `dev-laptop` і `single-node`: **не перевірено на реальному середовищі**, статус кандидатів наведено вище.
