# Платформа з Admin UI

Піднімає всі сервіси Jane в dev-стеку за proxy з адміністративним інтерфейсом. Передумови й підготовка — [початок роботи](README.md); будова стеку — [розгортання](../architecture/deployment.md).

Кроки 1, 3–5 виконано 2026-10-11 на Windows 11, ревізія `48389a3`: стек `just up` без зв'язування сервісів. Збірку Admin UI (крок 2) і зв'язування через `infra/compose.local.yaml` у цій перевірці не виконували — позначено «не перевірено». На Linux не перевірялося.

## Зміст

- [Зв'язування сервісів](#звязування-сервісів)
- [Кроки](#кроки)
- [Перевірка](#перевірка)
- [Прибирання](#прибирання)

## Зв'язування сервісів

`just up` піднімає контейнери з `infra/compose.yaml`, але не повідомляє сервісам адреси одне одного. У такому стеку:

- Orchestrator не має виконавців — `GET /v1/executors` повертає `{"items":[]}`, тож запуски завдань не мають кого викликати;
- Registry не знає профілів Handler Runtime і відхиляє версії екстракторів із `422 dependency_not_allowed`;
- колектори, Handler Runtime і LLM gateway не мають адреси Registry.

Зв'язування додає локальний файл `infra/compose.local.yaml` (поза Git): `just up` автоматично включає його в кожну команду compose. Зразок — [infra/compose.local.example.yaml](../../infra/compose.local.example.yaml): виконавці Orchestrator, адреси Registry, профілі Handler Runtime для Registry і адреси сусідів Assistant. Зразок також збирає Web Collector із Playwright (`--extra render`), а Telegram Collector — із Telethon і реальним обліковим записом (секрети в `.jane/secrets`); приберіть ці частини, якщо вони не потрібні. Не перевірено в цій документації.

Для перевіреного наскрізного сценарію без Admin UI використовуйте `deploy/profiles/stack.py` — [наскрізний сценарій](end-to-end.md).

## Кроки

1. Встановіть залежності workspace:

   ```powershell
   uv sync --all-packages
   ```

2. Зберіть Admin UI — dev-стек віддає готовий каталог `web/admin/dist` через proxy (не перевірено):

   ```powershell
   corepack pnpm --dir web/admin install --frozen-lockfile
   corepack pnpm --dir web/admin build
   ```

   Без `web/admin/dist` proxy працює, але сторінок адмінки не віддає.

3. За потреби створіть `infra/compose.local.yaml` за зразком — див. [зв'язування сервісів](#звязування-сервісів).

4. Запустіть сервіси. PostgreSQL, MinIO і тестовий сайт стартують автоматично як залежності; перший запуск збирає образи (у перевірці — близько 7,5 хвилини):

   ```powershell
   just up --project jane-doc-start proxy storage handler-runtime web-collector telegram-collector orchestrator registry llm assistant
   ```

   Команда чекає health-check контейнерів і друкує адреси. Вивід перевірочного запуску (порти зафіксовано змінними `JANE_PORT_<СЕРВІС>`; без них порти обирає Docker):

   ```text
   project: jane-doc-start   (stack file: .jane/stack-jane-doc-start.json)
     postgres   127.0.0.1:18901
     minio      http://127.0.0.1:18902
     testsite   http://127.0.0.1:18904
     proxy      http://127.0.0.1:18905
     storage    http://127.0.0.1:18906
     handler-runtime http://127.0.0.1:18907
     web-collector http://127.0.0.1:18908
     telegram-collector http://127.0.0.1:18909
     orchestrator http://127.0.0.1:18910
     registry   http://127.0.0.1:18911
     llm        http://127.0.0.1:18912
     assistant  http://127.0.0.1:18913
     auth       api_key (admin key: `just env` -> JANE_STACK_AUTH_ADMIN_API_KEY)
     db-handler-runtime postgresql://127.0.0.1:18901/jane_handler_runtime
     db-orchestrator postgresql://127.0.0.1:18901/jane_orchestrator
     db-registry postgresql://127.0.0.1:18901/jane_registry
     db-llm     postgresql://127.0.0.1:18901/jane_llm
     db-assistant postgresql://127.0.0.1:18901/jane_assistant
     db-storage-results postgresql://127.0.0.1:18901/jane_storage_results
   ```

5. Отримайте адресу proxy та ключ адміністратора:

   ```powershell
   just env --project jane-doc-start
   ```

   Потрібні рядки — `JANE_STACK_PROXY_URL` і `JANE_STACK_AUTH_ADMIN_API_KEY`. Ключ генерується під час першого `just up` і зберігається в `.jane/stack-jane-doc-start.json`; не публікуйте його.

6. Відкрийте `JANE_STACK_PROXY_URL` у браузері й введіть ключ на сторінці входу. Ключ зберігається лише в сесії вкладки (не перевірено в цій документації).

## Перевірка

Стан контейнерів:

```powershell
just ps --project jane-doc-start
```

Очікуваний результат: у стовпці `STATUS` кожного сервісу — `(healthy)`. Уривок перевірочного запуску (стовпці `NAME`, `STATUS`, `PORTS`):

```text
jane-doc-start-assistant-1           Up About a minute (healthy)   127.0.0.1:18913->8000/tcp
jane-doc-start-handler-runtime-1     Up 2 minutes (healthy)        127.0.0.1:18907->8000/tcp
jane-doc-start-orchestrator-1        Up 2 minutes (healthy)        127.0.0.1:18910->8000/tcp
jane-doc-start-proxy-1               Up 2 minutes (healthy)        127.0.0.1:18905->8080/tcp
```

API сервісів доступні через proxy як `<JANE_STACK_PROXY_URL>/api/<сервіс>/v1/...`. `GET /v1/health` відповідає без ключа, інші операції потребують `Authorization: Bearer <ключ>`.

Bash:

```bash
curl -s http://127.0.0.1:18905/api/orchestrator/v1/health
```

```json
{"status":"ok","checks":{"database":{"status":"ok"}}}
```

У перевірочному запуску для кожного з 8 сервісів (`orchestrator`, `registry`, `storage`, `web-collector`, `handler-runtime`, `llm`, `assistant`, `telegram-collector`) `GET /api/<сервіс>/v1/health` повернув `200`, `GET /api/<сервіс>/v1/info` без ключа — `401`, із ключем — `200`.

## Прибирання

Команда нижче зупиняє стек і **видаляє всі його дані**: томи баз і сховищ, локально зібрані образи та файл `.jane/stack-jane-doc-start.json` зі згенерованими паролями й ключами.

```powershell
just down -v --project jane-doc-start
```

Щоб зупинити стек і зберегти дані, виконайте `just down --project jane-doc-start` без `-v`.
