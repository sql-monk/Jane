# Ліміти й профілі

Паралельність, частота запитів, глибина й обсяг обходу, тайм-аути, повтори, черги, пісочниця, бюджети LLM і розміри передачі в Jane задаються конфігурацією, а не кодом (ТЗ §13.1, п. 5). Сторінка пояснює, звідки береться ефективне значення ліміту і як змінити його без перезбирання образів. Готові профілі для середовищ — [deploy/profiles/README.md](../../deploy/profiles/README.md); рішення — [ADR-0009](../adr/0009-limits-and-profiles.md).

## Зміст

- [Модель лімітів](#модель-лімітів)
- [Рівні та успадкування](#рівні-та-успадкування)
- [Ліміти сервісу: файл і змінні середовища](#ліміти-сервісу-файл-і-змінні-середовища)
- [Ліміти платформи в Orchestrator](#ліміти-платформи-в-orchestrator)
- [Ліміти джерела, завдання й етапу](#ліміти-джерела-завдання-й-етапу)
- [Як застосовуються зміни](#як-застосовуються-зміни)
- [Діагностика](#діагностика)

## Модель лімітів

Схема — [limits.schema.json](../../contracts/schemas/common/limits.schema.json). Групи: `concurrency`, `rate`, `crawl`, `timeouts`, `retries`, `queue`, `sandbox`, `llm`, `transfer`, `telegram`. Документ `PlatformLimits` має три поля: `profile` (назва), `defaults` (значення) і `hard_caps` (жорсткі стелі).

Кожен сервіс описує свої ліміти моделлю `Limits` (`jane_kit.config`). Модель не дозволяє поля без типового значення, тому кожен ліміт має безпечне значення за замовчуванням. Крім контрактних, сервіс може мати внутрішні ліміти (наприклад `engine.workers` Orchestrator); вони задаються лише змінними середовища сервісу й не потрапляють у `/v1/info`.

Під час виконання значення можуть лише звужуватися обмеженнями джерела чи зовнішнього сервісу: `Crawl-delay` з `robots.txt`, `Retry-After`, flood-wait Telegram, ліміти провайдера LLM.

## Рівні та успадкування

Рівні від загального до конкретного: `platform` → `source` → `task` → `stage` → `request`.

- Нижчий рівень перекриває вищий для кожного поля окремо (глибоке злиття); відсутнє поле успадковується.
- `null` не є значенням: щоб повернутися до успадкованого значення, поле просто не передають.
- `hard_caps` обмежують результат злиття: ефективне значення = `min(значення, стеля)`. Нижчий рівень може стелю лише зменшити.
- Результат зберігає походження кожного значення: `platform`, `source`, `task`, `stage`, `request` або `hard_cap`.

## Ліміти сервісу: файл і змінні середовища

Шари рівня платформи для одного сервісу, у порядку застосування:

1. типові значення моделі `Limits` сервісу;
2. файл `JANE_<СЕРВІС>_LIMITS_FILE` — документ `PlatformLimits` у JSON, YAML або TOML, наприклад цілий `deploy/profiles/<профіль>.json`;
3. змінні середовища `JANE_<СЕРВІС>_LIMITS__<ГРУПА>__<ПОЛЕ>` (значення) і `JANE_<СЕРВІС>_LIMITS__HARD_CAPS__<ГРУПА>__<ПОЛЕ>` (стеля).

Приклади змінних із репозиторію:

```yaml
# infra/compose.local.example.yaml
JANE_WEB_COLLECTOR_LIMITS__TRANSFER__INLINE_MAX_BYTES: "8388608"
# tests/e2e/compose.e2e.yaml
JANE_LLM_LIMITS__LLM__MAX_REQUESTS_PER_MINUTE: "120"
```

Внутрішні групи сервісу задаються так само, з префіксом `LIMITS__`: наприклад, кількість одночасних job Web Collector — `JANE_WEB_COLLECTOR_LIMITS__JOBS__MAX_CONCURRENT_JOBS` (типово 4). Змінна без `LIMITS__` (`JANE_WEB_COLLECTOR_JOBS__MAX_CONCURRENT_JOBS`) мовчки ігнорується — перевірено 2026-10-11 викликом `resolve_service_limits` (значення лишилося 4). Розбіжність: `infra/compose.local.example.yaml` задає саме такі ігноровані змінні `JANE_WEB_COLLECTOR_JOBS__MAX_CONCURRENT_JOBS` і `JANE_WEB_COLLECTOR_JOBS__JOB_TIMEOUT_MS`. Перелік параметрів кожного сервісу — `configuration.md` модуля.

Правила файлу профілю:

- Профіль спільний для всіх сервісів. Шлях контракту, якого сервіс не моделює (наприклад `sandbox.*` для Web Collector), ігнорується; під час старту сервіс пише в журнал `platform limits profile applied partially` зі списком проігнорованих шляхів.
- Шлях, якого немає ні в контракті, ні в моделі сервісу, — помилка: сервіс не стартує (`LimitError`).
- Змінні середовища приймають шляхи моделі сервісу, не контракту.

## Ліміти платформи в Orchestrator

Orchestrator зберігає документ лімітів платформи у своїй базі й об'єднує його з рівнями джерела, завдання й етапу для кожного запуску. Ефективні ліміти етапу він передає виконавцю в кожному виклику; виконавець застосовує `min(ліміти запиту, власні hard_caps)`.

- **Перший старт.** Документ створюється з файлу `JANE_ORCHESTRATOR_LIMITS_FILE`, а без файлу — з типових значень Orchestrator (профіль `orchestrator-defaults`). Документ перевіряється за схемою.
- **Наступні старти** документ не змінюють: зміна файлу на вже ініціалізовану базу не впливає.
- **Зміна в роботі** — `PUT /v1/limits/platform` (scope `orchestrator:admin`) з `If-Match: <ETag>` з попереднього `GET /v1/limits/platform`. Невідповідний `ETag` дає `412`, невалідний документ — `422`. Зміна діє для нових запусків.
- **Перегляд** — `GET /v1/limits/effective?source_id=…&task_id=…&stage_id=…` повертає ефективні значення й походження кожного.

Уривок відповіді `GET /v1/limits/effective` (приклад із контракту, [effective-limits.json](../../contracts/examples/openapi/effective-limits.json)):

```json
{
  "limits": {
    "rate": {"requests_per_second_per_host": 2},
    "sandbox": {"memory_mb": 512, "wall_time_ms": 20000, "cpu_cores": 1},
    "crawl": {"max_depth": 3}
  },
  "provenance": {
    "rate.requests_per_second_per_host": "source",
    "sandbox.memory_mb": "stage",
    "sandbox.wall_time_ms": "stage",
    "sandbox.cpu_cores": "platform",
    "crawl.max_depth": "stage"
  }
}
```

Внутрішні параметри Orchestrator (`JANE_ORCHESTRATOR_LIMITS__ENGINE__*`, `JANE_ORCHESTRATOR_LIMITS__CLAIMS__*`) у документ платформи не входять і задаються лише змінними середовища.

## Ліміти джерела, завдання й етапу

- **Джерело** — поле `limits` у документі джерела ([source.schema.json](../../contracts/schemas/source.schema.json)).
- **Завдання** — `limits` і `retries` у конфігурації завдання ([task-config.schema.json](../../contracts/schemas/task-config.schema.json)).
- **Етап** — `limits` і `retries` етапу в тій самій конфігурації.
- **Запит** — автономний виклик сервісу без Orchestrator може передати `limits` у тілі (наприклад `CollectionRequest.limits` колектора); сервіс обмежує їх своїми стелями.

Зміна джерела чи завдання через API Orchestrator (`PUT /v1/sources/{source_id}`, `PUT /v1/tasks/{task_id}`) діє з наступного запуску. Це перевіряє наскрізний сценарій S-M2-09: ліміт сторінок рівня платформи, а потім рівня завдання, змінює реальний збір без перезбирання — [приймання](../acceptance/README.md).

## Як застосовуються зміни

| Що змінено | Як застосувати |
|---|---|
| Файл профілю або змінні `JANE_<СЕРВІС>_LIMITS__*` сервісу | перезапуск сервісу (`just up <сервіс>` перестворює контейнер, якщо змінилося середовище) |
| Файл профілю Orchestrator | діє лише на порожню базу; для робочої бази — `PUT /v1/limits/platform` |
| Ліміти платформи в Orchestrator | `PUT /v1/limits/platform`, діє для нових запусків |
| Ліміти джерела, завдання, етапу | нова ревізія документа через API Orchestrator, діє з наступного запуску |
| Ліміти одного автономного запиту | поле `limits` у тілі запиту |

## Діагностика

- `GET /v1/info` сервісу → `limits`: контрактні типові значення, стелі та `profile`.
- `GET /v1/limits/effective` Orchestrator → ефективні значення з походженням.
- Журнал старту сервісу: проігноровані шляхи профілю.
- Відмова через перевищення ліміту — помилка `limit_exceeded` у форматі `application/problem+json` ([errors.md](../../contracts/docs/errors.md)).
- Перевірка, що профіль справді обмежує поведінку, — [перевірка профілів](limits-validation.md).
