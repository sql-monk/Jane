# Контракти: експлуатація

Як змінювати контракт без поломки споживачів, як ці зміни перевіряє CI і що робити з типовими помилками інструментів. Моніторингу й резервування модуль не потребує: контракти — файли в Git, їхня історія — історія репозиторію.

## Зміст

- [Зміна контракту](#зміна-контракту)
- [Несумісна зміна](#несумісна-зміна)
- [Перевірки в CI](#перевірки-в-ci)
- [Оновлення закріплених інструментів](#оновлення-закріплених-інструментів)
- [Типові проблеми](#типові-проблеми)

## Зміна контракту

![Процес зміни контракту з перевірками та поверненнями на виправлення](../../diagrams/contracts/contract-change.light.png#gh-light-mode-only)
![Процес зміни контракту з перевірками та поверненнями на виправлення](../../diagrams/contracts/contract-change.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/contracts/contract-change.light.png), [темне](../../diagrams/contracts/contract-change.dark.png); джерело — [contract-change.drawio](../../diagrams/contracts/contract-change.drawio).

Контракти змінює координатор; виконавець WP, якому бракує поля чи операції, описує потребу в розділі «Запити до інших власників» свого звіту, а не змінює `contracts/` сам ([процес WP](../../development/wp-process.md)).

1. **Оцініть сумісність.** Сумісно: нове необов'язкове поле, нова операція, нове значення в розширюваному переліку відповіді. Несумісно: видалення, звуження, нове обов'язкове поле чи параметр запиту — див. [несумісна зміна](#несумісна-зміна).
2. **Змініть файли.** OpenAPI — `contracts/openapi/<api>.v1.yaml`, спільне — `common.yaml`, дані — `contracts/schemas/`. Новий ліміт — нове поле `limits.schema.json`, типове значення — у профілях `deploy/profiles/`.
3. **Оновіть приклади.** Кожна операція має приклад запиту й кожної успішної відповіді; для нового обмеження схеми додайте невалідний приклад у `contracts/examples/invalid/`. Новий scope операції — `x-jane-scope` і рядок у `jane_kit.auth_scopes`.
4. **Оновіть документи** `contracts/docs/` (наприклад, новий код помилки — `errors.md` і `KNOWN_CODES` у jane-kit).
5. **Перевірте:**

   ```powershell
   just contracts-check
   just contracts-compat
   just contract
   ```

   Очікувано: `All contract checks passed.`, `0 breaking`, тести `contract` без падінь. `just contracts-compat` порівнює з `main`; з іншою базою — `just contracts-compat origin/main`.

6. **Перевірте споживачів.** Перелік — [API та їхні реалізації](README.md#api-та-їхні-реалізації). Перегенеруйте клієнтів (`just contracts-gen`, `pnpm gen:api` в Admin UI) і запустіть `just check`.
7. **Рев'ю.** Субагент `contract-guardian` перевіряє сумісність відносно `main`, валідність контрактів і прикладів та чи всі споживачі оновлені або перелічені; у звіті WP перелічіть споживачів.

## Несумісна зміна

- Нова версія API — `/v2` паралельно з `/v1`; `/v1` працює, доки є споживачі.
- Альтернатива — узгоджене оновлення всіх споживачів в одному злитті; `compat.py` все одно покаже `BREAKING`, тож таку зміну приймає лише координатор свідомо.
- Документи конфігурації (`TaskConfig`, `CollectorRules`, `Limits`…) строгі: перейменування поля ламає збережені конфігурації — потрібна міграція даних у сервісі-власнику.

## Перевірки в CI

| Job | Що робить для контрактів |
|---|---|
| `lint` | `just lint`: ruff і лінтер контрактів без Redocly |
| `contract` | `just contract` з `JANE_CONTRACTS_REDOCLY=1`: лінтер із обов'язковим Redocly, самоперевірка `compat.py`, тести `contract` |
| `contracts-compat` | `just contracts-compat <base> --oasdiff`: база — гілка PR, попередній стан `main` для push у `main`, інакше merge-base з `main` |

Повний конвеєр — [CI](../../development/ci.md).

## Оновлення закріплених інструментів

- **oasdiff.** Образ закріплено тегом і digest у `OASDIFF_IMAGE` (`contracts/tools/compat.py`). Щоб перейти на новий реліз: прочитати digest (`docker buildx imagetools inspect tufin/oasdiff:<tag>`), перевірити `JANE_OASDIFF_IMAGE=<tag>@<digest>` командою `just contracts-compat main --oasdiff` (очікувано `0 breaking` на незміненому дереві), потім змінити константу. Бінарний `oasdiff` у `PATH` має пріоритет і не закріплюється.
- **Redocly і Prism.** Версії закріплено в `check_contracts.py` (`@redocly/cli@2.54.3`) і в командах документації (`@stoplight/prism-cli@5.16.0`).
- **Залежності скриптів** — у заголовках PEP 723 самих скриптів.

Оновлення oasdiff і Redocly в межах цієї документації не виконувались.

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| `POST must declare Idempotency-Key header or x-jane-no-idempotency-key` | Нова POST-операція без ключа | Додати параметр `common.yaml#/components/parameters/IdempotencyKey` або обґрунтоване розширення |
| `success response needs at least one example` | Нова відповідь без прикладу | Додати `examples` або `$ref` на `examples/openapi/*.json` |
| `expected to be REJECTED ... but it is valid` | Невалідний приклад проходить схему | Обмеження в схемі не діє — виправити схему або приклад |
| `depends on integration contract orchestrator.v1.yaml` | Автономний API послався на контракт Orchestrator/Assistant | Перенести спільне в `common.yaml` або `schemas/` |
| `BREAKING ... became required` у `compat.py` | Нове обов'язкове поле запиту | Зробити поле необов'язковим або винести в `/v2` |
| `[skip] Redocly lint` локально, а CI падає на Redocly | Локально немає Node.js | `just contracts-check --redocly` з Node.js 24 |
| `oasdiff: skipped (neither oasdiff nor docker found)` | Немає oasdiff і Docker | Встановити Docker; власна перевірка `compat.py` все одно виконується |
| Мок повертає не той приклад | Типово — перший приклад найменшого `2xx` | Заголовок `Prefer: example=<name>` або `Prefer: code=<status>` |
