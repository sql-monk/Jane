# Профілі лімітів WP-14

Документи `PlatformLimits` (`contracts/schemas/common/limits.schema.json#/$defs/PlatformLimits`) для
підтримуваних середовищ, стек, що застосовує профіль, і harness вимірювання. Рішення людини (2026-09-30):
перевіряються `dev-laptop` і `ci`; `single-node` — кандидат.

| Файл | Середовище | Статус |
|---|---|---|
| `dev-laptop.json` | ця машина: Windows 11 + Docker Desktop (6 CPU, 16 ГБ у Docker) | кандидат; вимірювання — фаза 2 |
| `ci.json` | GitHub Actions `ubuntu-latest` (4 vCPU, 16 ГБ), лише testsite і fake LLM | кандидат; вимірювання — фаза 2 |
| `single-node.json` | одна Linux VM з Docker Compose, орієнтир 8 vCPU / 32 ГБ | кандидат, **не перевірено на реальному середовищі** |
| `thresholds.json` | пороги pass/fail harness для `dev-laptop` і `ci` | [опис](../../docs/operations/limits-validation.md) |
| `compose.stack.yaml`, `stack.py` | ізольований ланцюжок сервісів з профілем | перевірено відтворенням прикладів |
| `harness/` | `limits_harness.py`, `metrics.py`, `probe_site.py`, пакет `harness.sandbox-probe` | тести без Docker; вимірювань немає |
| `check.py` | перевірка форми всіх трьох профілів за контрактом | |

Значення профілів — довідкові приклади WP-00 з однією зміною: у `dev-laptop`
`sandbox.wall_time_ms` 30 000 → 60 000 і `timeouts.invocation_timeout_ms` 60 000 → 90 000, бо WP-13 на
Docker Desktop зафіксував 30,7 с старту контейнера пісочниці при 1 с роботи екстрактора (e2e WP-13
працює з 60 с). Решту чисел підтверджує або змінює фаза 2.

## Команди

```text
uv run --all-packages python deploy/profiles/check.py                                  # форма профілів
uv run --all-packages pytest deploy/profiles -q                                         # тести без Docker
uv run --all-packages python deploy/profiles/stack.py up --profile dev-laptop [--project P] [--telegram] [--probe]
uv run --all-packages python deploy/profiles/stack.py env --project P                  # адреси
uv run --all-packages python deploy/profiles/stack.py down --project P                 # + перевірка залишків
uv run --all-packages python deploy/profiles/harness/limits_harness.py plan --profile dev-laptop
uv run --all-packages python deploy/profiles/harness/limits_harness.py run --profile dev-laptop   # вільна машина!
```

`just check` цей каталог не тестує (`testpaths` кореневого `pyproject.toml` належить WP-01); тести запускаються
окремою командою вище, типи — `uv run --all-packages mypy deploy/profiles`.

## Як профіль доходить до сервісів

1. **Оркестратор** читає `JANE_ORCHESTRATOR_LIMITS_FILE` **лише під час першого заповнення** документа лімітів
   у своїй БД. Далі — `GET /v1/limits/platform`, `PUT /v1/limits/platform` з `If-Match: <ETag>` (право
   `orchestrator:admin`), перевірка — `GET /v1/limits/effective?source_id=&task_id=&stage_id=`. Ефективні ліміти
   етапу (platform → source → task → stage, `hard_caps` зверху) оркестратор передає в кожен виклик колектора
   й обробника, тож runtime і storage отримують `sandbox`, `timeouts` тощо з профілю в запиті.
2. **Web Collector і Telegram Collector** приймають увесь профіль як `JANE_*_LIMITS_FILE` (групи, яких не
   моделюють, ігнорують) — це їхні ліміти й для автономних викликів.
3. **storage, handler-runtime, registry, llm, assistant** зараз **не стартують** з повним профілем як
   `LIMITS_FILE` (`LimitError: unknown limit(s)`). Для них профіль діє лише через запити оркестратора, а для
   автономного використання — їхні типові значення з README або окремі змінні `<ПРЕФІКС>_LIMITS__<ГРУПА>__<ПОЛЕ>`.
   Запит власникам — у [звіті WP-14](../../docs/delivery/WP-14.md).

`compose.stack.yaml` робить саме це: монтує профіль у orchestrator і колектори, генерує виконавців оркестратора
(`.jane/executors-<проєкт>.json`) лише для запущених сервісів і налаштовує registry ↔ runtime ↔ колектори.
Нові ліміти діють для **нових** запусків. Обмеження сайту, провайдера й `hard_caps` можуть лише звузити профіль.

Профіль `ci` має довідкову частоту 50 запитів/с на хост — лише для локального testsite в ізольованій мережі.
Для будь-якого реального сайту задайте нижчу межу на рівні джерела; профіль не є дозволом на таку частоту.
