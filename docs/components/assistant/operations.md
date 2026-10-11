# Assistant: експлуатація

Розрізняйте власний стан сесій/jobs, стан сусідніх сервісів і зовнішні API. Здоровий процес без налаштованих сусідів не підтверджує готовність onboarding.

[Спостереження](#спостереження) · [Оновлення](#оновлення) · [Резервування](#резервування) · [Відновлення](#відновлення) · [Типові проблеми](#типові-проблеми)

## Спостереження

Health перевіряє власний state; info.capabilities.neighbours показує налаштовані клієнти, не поточну гарантовану доступність кожного endpoint. `GET /v1/onboarding-sessions` і `/v1/improvement-runs` дають cursor списки; job detail показує progress/result/error. Log trace_id веде до виклику сусіда. `/metrics` дає технічні метрики; дані cost/usage залишаються в LLM gateway.

Сесія `proposals_ready` може очікувати acceptance після succeeded job. `insufficient_sample` означає нестачу доказів coverage; не підвищуйте confidence штучно без матеріалів. `forward_unknown_to_llm=false` має залишати матеріал без зовнішнього аналізу.

## Оновлення

Завершіть або скасуйте активні jobs, збережіть own state, operator settings і secret refs. Після оновлення запустіть з тим самим state_dsn/state_schema, звірте schemas доступність, neighbours і session lists. PostgreSQL open створює sessions DDL та Jane Kit jobs/idempotency migrations. Memory sessions не відновлюються після перезапуску.

Декілька екземплярів потребують спільної own schema й унікального instance_id. Lease/heartbeat визначає втрату власника; запити selection/acceptance із застарілою CAS version потребують повторного читання сесії, а не форсованого overwrite.

## Резервування

Зупиніть активні onboarding/improvement jobs перед consistent backup state_schema. PostgreSQL client tools з PGHOST/PGUSER/PGPASSWORD:

```powershell
pg_dump --format=custom --file=assistant.backup --schema=jane_assistant --dbname=assistant_db
```

Збережіть також search_static_file, contracts source revision, default storage bindings і secrets окремо. Registry пакети, Orchestrator task/source і Storage матеріали резервуються їхніми власниками; copy sessions не відновлює їх автоматично.

## Відновлення

Створіть окрему цільову базу й відновіть власну схему:

```powershell
pg_restore --dbname=assistant_restore --no-owner assistant.backup
```

Встановіть новий DSN, відновіть secrets/neighbor URLs, запустіть один екземпляр. Перевірте session lists/detail, job history і capabilities; звірте proposal package refs із Registry, активовані source/task із Orchestrator та material_ref зі Storage. Прострочений job lease після аварії може завершитися failed; не оголошуйте тривалий job успішним лише за restored row.

Власний PostgreSQL backup/restore у цьому модульному пакеті не виконувався. Координатор має [platform backup/restore evidence](../../delivery/documentation/DOC-08.md); full external LLM/Telegram onboarding не перевірено.

## Типові проблеми

| Симптом | Перевірка | Дія |
|---|---|---|
| `upstream_unavailable` | info.neighbours, URL/token ref, job.error.detail | Налаштуйте потрібного сусіда й перевірте його API |
| Невідомий `cheap`/`strong` model | LLM aliases | Створіть aliases або змініть llm_model_* |
| `needs_disambiguation` | candidates session | Явно виберіть candidate_id |
| `insufficient_sample` | Confidence, types, budgets, collector progress | Дайте різні матеріали/бюджет або звузьте query |
| Generation не проходить tests | Diagnostics runtime/schema | Перегляньте пропозицію; sandbox не вимикайте |
| Activation відхилено | onboarding_allow_activation, tests, orchestrator_url | Узгодьте політику й готовність Orchestrator |
| ContentRef denied | blob_roots/download hosts, sha256/size | Налаштуйте дозволений transport і валідний content |
| Після рестарту нема sessions | Відсутній state_dsn | Використайте PostgreSQL для потрібної durability |
| Concurrent session change | CAS version / поточний state | Перечитайте перед acceptance/selection |

[Конфігурація](configuration.md), [інтеграція](integration.md).
