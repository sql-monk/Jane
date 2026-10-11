# Новий сервіс

Як створити сервіс Jane з шаблону [templates/service](../../templates/service/README.md) і довести його до готовності: контракт, API, ліміти, автентифікація, тести, Dockerfile.

## Зміст

- [Створення](#створення)
- [Що містить шаблон](#що-містить-шаблон)
- [Наступні кроки](#наступні-кроки)
- [Перевірка](#перевірка)

## Створення

```powershell
just new-service <ім'я>
```

Ім'я — малі латинські слова через дефіс (`price-monitor`); інше ім'я відхиляється. Рецепт:

1. копіює `templates/service` у `services/<ім'я>`, пропускаючи кеші й `.venv`;
2. замінює назви в шляхах і файлах: `jane-template-service` → `jane-<ім'я>`, `jane_template_service` → `jane_<ім'я_з_підкресленнями>`, `JANE_TEMPLATE_SERVICE_` → `JANE_<ІМ'Я>_`, `Template Service` → назву з великих літер;
3. виконує `uv lock` (новий каталог `services/*` стає членом workspace автоматично);
4. друкує наступні команди: `just test <ім'я>` і `uv run --package jane-<ім'я> python -m jane_<ім'я>`.

Каталог, що вже існує, не перезаписується. Перевірено копіювання функцією `new_service` з `scripts/dev.py` у тимчасовий каталог (ім'я `demo-svc` → пакет `jane_demo_svc`, префікс `JANE_DEMO_SVC_`); сам рецепт у репозиторії не запускався, бо змінює `services/` і `uv.lock`.

## Що містить шаблон

```text
services/<ім'я>/
├── pyproject.toml            # залежність jane-kit (workspace), скрипт jane-<ім'я>
├── Dockerfile                # збирання з кореня репозиторію, uv sync --frozen, користувач без прав, HEALTHCHECK
├── README.md                 # розділи README сервісу: запуск, тести, конфігурація, ліміти, приклад виклику
├── CLAUDE.md                 # три рядки для агента: запуск, тести, контракт
├── src/jane_<ім'я>/
│   ├── __main__.py           # python -m jane_<ім'я>: Settings() і jane_kit.service.run
│   ├── settings.py           # Settings(JaneSettings) з префіксом, ServiceLimits(Limits), resolve_service_limits
│   └── app.py                # build_app: create_app, JobRunner, ідемпотентність, приклад /v1/examples/jobs
└── tests/
    ├── test_app.py           # unit-тести застосунку
    └── test_contract.py      # контрактні тести: common.yaml і contracts/openapi/<ім'я>.v1.yaml
```

Шаблон уже дає `/v1/health`, `/v1/info`, `/metrics`, `/v1/jobs/{job_id}` і скасування, JSON-журнали, Problem, `Idempotency-Key` і таблицю scopes. Як працює кожна з цих частин — [jane-kit: інтеграція](../components/jane-kit/integration.md).

## Наступні кроки

1. **Контракт.** Опишіть API в `contracts/openapi/<ім'я>.v1.yaml` за конвенціями ([контракти](../components/contracts/integration.md#конвенції-api)) і пройдіть [процес зміни контракту](contracts.md). Поки файлу немає, `test_contract.py` пропускає перевірку API сервісу.
2. **API.** Замініть приклад `POST /v1/examples/jobs` і модель `ExampleJobRequest` в `app.py` на операції контракту.
3. **Scopes.** Замініть рядки `AUTH_SCOPES` на scopes операцій контракту (`x-jane-scope`); для нового API додайте таблицю в `jane_kit.auth_scopes`. Маршрут без рядка не дасть сервісу стартувати.
4. **Ліміти.** Додайте групи в `ServiceLimits` з безпечними типовими значеннями; поля, що є в `limits.schema.json`, оголошуйте через `contract_field` ([ліміти](../components/jane-kit/configuration.md#ліміти)).
5. **Кілька екземплярів.** Замініть `InMemoryIdempotencyStore` і типове сховище `JobRunner` на спільні сховища у власній базі сервісу ([сховища](../components/jane-kit/integration.md#сховища-для-кількох-екземплярів)).
6. **Залежності сервісу** — перевірки в `app.state.health.add(...)`.
7. **Тести.** Unit-тести без маркера, контрактні — `contract`, з dev-стеком — `integration` ([тести](testing.md)).
8. **Dev-стек.** Додайте сервіс у `infra/compose.yaml` і порт у `PORT_VARS` `scripts/dev.py`, якщо він має запускатися через `just up` (ці файли змінює їхній власник за процесом WP).
9. **Документація.** README сервісу й комплект `docs/components/<модуль>/` ([документація](documentation.md)).

## Перевірка

```powershell
just test <ім'я>
uv run --package jane-<ім'я> python -m jane_<ім'я>
```

Для самого шаблону (перевірено):

```powershell
just test template-service
```

```text
=========================== short test summary info ===========================
SKIPPED [1] templates\service\tests\test_contract.py:61: service contract not in contracts/openapi yet
======================= 10 passed, 1 skipped in 10.33s ========================
```

Перед злиттям — `just check`.
