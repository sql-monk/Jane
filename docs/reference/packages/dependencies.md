# Залежності й доступи пакета

Пакет не встановлює нічого під час виконання й не несе секретів. Усе, що йому потрібно ззовні, він оголошує в маніфесті: профіль runtime і Python-бібліотеки, інші пакети, мережевий доступ і підключення. Registry перевіряє ці оголошення під час публікації; виконавець — під час виконання.

## Зміст

- [Профіль runtime](#профіль-runtime)
- [Python-вимоги](#python-вимоги)
- [Залежності від інших пакетів](#залежності-від-інших-пакетів)
- [Мережевий доступ](#мережевий-доступ)
- [Підключення](#підключення)
- [Заборона секретів](#заборона-секретів)

## Профіль runtime

`dependencies.runtime_profile` (наприклад `python-extractor@1`) називає образ пісочниці Handler Runtime: версію Python і точний набір бібліотек. Профіль публікує Handler Runtime — файлом [python-extractor-1.json](../../../services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json) і в `capabilities.runtime_profiles` відповіді `GET /v1/info`. Уривок профілю:

```json
{
  "profile": "python-extractor@1",
  "python": "3.12",
  "libraries": {
    "beautifulsoup4": "4.15.0",
    "lxml": "6.1.3",
    "parsel": "1.12.0",
    "selectolax": "0.3.34"
  },
  "stdlib": true,
  "network": "none"
}
```

Registry не має вбудованого списку профілів: він читає їх із джерел `JANE_REGISTRY_RUNTIME_PROFILES` — файлів або URL `GET <handler-runtime>/v1/info` ([конфігурація Registry](../../components/registry/configuration.md)). Перевірка під час публікації:

| Ситуація | Результат |
|---|---|
| Профіль знайдено | Перевіряються Python-вимоги |
| Профіль невідомий (зокрема джерел не налаштовано) | `422 dependency_not_allowed`, `pointer` `/manifest/dependencies/runtime_profile` |
| Жодне джерело не завантажилося й профілів немає | `502 upstream_unavailable` |
| `dependencies.python` задано без `runtime_profile` | `422 dependency_not_allowed` |

## Python-вимоги

`dependencies.python` — список вимог PEP 508 (`"selectolax>=0.3,<0.4"`). Пакети ніколи не встановлюються з мережі: кожна вимога має задовольнятися бібліотекою профілю. Registry перевіряє за тими самими правилами, що й Handler Runtime ([profiles.py](../../../services/registry/src/jane_registry/profiles.py)):

- вимога з URL (`name @ https://…`) заборонена;
- вимога з маркером середовища, хибним для пісочниці (Linux, Python профілю), пропускається;
- бібліотека має бути в профілі, а її точна версія — задовольняти специфікатор (передрелізи дозволені).

Помилка показує індекс вимоги. Реальна відповідь на вимогу `requests>=2`, якої немає в профілі:

```json
{
  "type": "urn:jane:problem:dependency_not_allowed",
  "title": "Dependency not allowed",
  "status": 422,
  "detail": "dependency not allowed",
  "instance": "/v1/packages/my.price-extractor/versions",
  "code": "dependency_not_allowed",
  "retryable": false,
  "errors": [
    {
      "pointer": "/manifest/dependencies/python/0",
      "message": "requests is not available in runtime profile python-extractor@1"
    }
  ],
  "trace_id": "54a6ad2108e89c4fa7e33a0cbaa48c46"
}
```

## Залежності від інших пакетів

`dependencies.packages[]` — посилання `PackageRef` на інші пакети Registry з точною версією (і, за бажання, `digest`). Під час публікації Registry перевіряє:

- пакет не залежить сам від себе;
- кожна вказана версія вже є в Registry;
- якщо задано `digest`, він збігається з дайджестом цієї версії.

Порушення — `422 validation_failed` з `pointer` `/manifest/dependencies/packages/<i>`. `jane-registry export` завантажує весь ланцюжок залежностей разом із пакетом ([Експорт і сумісність](export-and-compatibility.md)).

## Мережевий доступ

`access.network` типово `none`: під час виконання мережі немає. `allowlist` з `access.hosts` — запит дозволити конкретні хости; виконавець може відмовити, якщо політика платформи цього не дозволяє. Registry це поле лише перевіряє за схемою.

## Підключення

Пакет, якому потрібне сховище чи провайдер, оголошує `required_connections` — логічне ім'я й тип:

```json
{
  "required_connections": [
    {"name": "target", "kind": "postgresql", "purpose": "база для результатів"}
  ]
}
```

Етап завдання зв'язує ім'я `target` з керованим підключенням (`connection_id`), а значення секретів виконавець розв'язує у своєму середовищі. Під час форку підключення не копіюються: їх у пакеті немає. Формат підключень — [connection.schema.json](../../../contracts/schemas/common/connection.schema.json).

## Заборона секретів

Перед збереженням версії Registry сканує кожен файл пакета, включно з маніфестом ([secrets.py](../../../services/registry/src/jane_registry/secrets.py)):

- імена файлів, що за домовленістю містять облікові дані (`.env`, `*.pem`, `id_rsa`, `.netrc`…);
- відомі формати ключів і токенів: приватні ключі, AWS, GitHub, GitLab, Slack, Google, Stripe, ключі LLM-провайдерів, токени Telegram-ботів, JWT, облікові дані в URL;
- значення після `Bearer`/`Basic`/`token` і присвоєння змінним на кшталт `password`, `api_key`;
- рядки з високою ентропією в коді й конфігурації (не в тестових HTML-сторінках).

Знахідка відхиляє публікацію з `422 secret_detected`; відповідь містить шлях файлу, код правила й рядок, але ніколи не саме значення. Реальна відповідь на файл `README.md` з токеном бота:

```json
{
  "type": "urn:jane:problem:secret_detected",
  "title": "Secret detected in package",
  "status": 422,
  "detail": "secret detected in package",
  "instance": "/v1/packages/my.channel-rules/versions",
  "code": "secret_detected",
  "retryable": false,
  "errors": [
    {"pointer": "/files/README.md", "code": "high_entropy_string", "message": "high-entropy string (line 1)"}
  ],
  "trace_id": "5caf0597b81b88df9881b957ad746ce9"
}
```

Файл, більший за `secrets.max_scan_bytes_per_file` (типово 2 MiB), не приймається без сканування: публікація завершується `422 limit_exceeded`.
