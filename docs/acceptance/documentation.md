# Відповідність вимогам до документації

Матриця зв'язує вимоги [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) з місцями, де їх виконано. Рядки розділів `docs/operations/`, `docs/adr/`, `docs/acceptance/` та довідок `infra/README.md`, `deploy/profiles/README.md`, `tests/e2e/README.md` заповнено; рядки з позначкою «—» заповнює координатор документації за звітами інших розділів.

Стан: **виконано** — зміст є й звірений із кодом; **частково** — є обмеження, вказане в примітці; **не перевірено** — перевірка не виконувалася; **—** — не заповнено.

## Зміст

- [Попереднє очищення](#попереднє-очищення)
- [Структура документації](#структура-документації)
- [Вимоги до наповнення](#вимоги-до-наповнення)
- [Вимоги до якості](#вимоги-до-якості)
- [Єдиний стиль сторінок](#єдиний-стиль-сторінок)
- [Діаграми Draw.io](#діаграми-drawio)

## Попереднє очищення

| Вимога (§1) | Де виконано | Стан |
|---|---|---|
| Інвентаризація й архів `docs-archive/` | `docs-archive/README.md` | — |
| Старі описи не використовуються як основа | ADR написано заново; архівні ADR використано лише як підказку, що вирішувалось, кожен факт звірено з кодом | виконано для `docs/adr/` |
| Розбіжності з ТЗ зафіксовано | [ADR-0003](../adr/0003-package-registry.md) (ТЗ §13.2), [ADR — відомі розбіжності](../adr/README.md#відомі-розбіжності) | виконано для своїх розділів |
| Навігація веде до нової документації | `docs/README.md` | — |

## Структура документації

| Вимога (§2) | Де виконано | Стан |
|---|---|---|
| `docs/operations/` — експлуатація платформи загалом | [operations/README.md](../operations/README.md) і 9 сторінок | виконано |
| `docs/adr/` — архітектурні рішення | [adr/README.md](../adr/README.md), ADR-0001…0010 | виконано |
| `docs/acceptance/` — відповідність ТЗ і докази | [README.md](README.md), [scenarios.md](scenarios.md), ця сторінка | виконано |
| `docs/diagrams/` — схеми розділів | `docs/diagrams/operations/`, `docs/diagrams/acceptance/` | частково: PNG не експортовано |
| `docs/README.md`, `overview/`, `getting-started/`, `user-guide/`, `architecture/`, `components/`, `reference/`, `development/`, `delivery/` | — | — |

## Вимоги до наповнення

| Вимога (§3) | Де виконано | Стан |
|---|---|---|
| Практичні інструкції: моніторинг | [monitoring.md](../operations/monitoring.md) | виконано |
| Практичні інструкції: оновлення й міграції | [upgrades.md](../operations/upgrades.md) | частково: відкат не виконувався |
| Практичні інструкції: резервування й відновлення | [backup-restore.md](../operations/backup-restore.md) | частково: перевірено для Orchestrator і Registry |
| Практичні інструкції: типові проблеми | [troubleshooting.md](../operations/troubleshooting.md) | виконано |
| Експлуатація платформи загалом, власність даних | [operations/README.md](../operations/README.md#власність-даних) | виконано |
| Експлуатація окремих модулів | `docs/components/<модуль>/operations.md` | — |
| Налаштування: ліміти й спосіб застосування змін | [limits.md](../operations/limits.md), [deploy/profiles/README.md](../../deploy/profiles/README.md) | виконано |
| Запуск на Windows і Linux | [running.md](../operations/running.md), [infra/README.md](../../infra/README.md) | частково: Linux не перевірено вручну, лише через CI |
| Рішення: проблема, варіанти, вибір, наслідки | [adr/](../adr/README.md) | виконано |
| Приймання: вимоги ТЗ, сценарії, критерії, докази | [README.md](README.md), [scenarios.md](scenarios.md) | виконано |
| Структура репозиторію (тести, точки входу) | [tests/e2e/README.md](../../tests/e2e/README.md) для e2e; загальне — `docs/architecture/repository-map.md` | частково |
| Типи модулів, каталог, автономність, композиція, MSDN-довідник, API, пакети, розробка | — | — |

## Вимоги до якості

| Вимога (§4) | Де виконано | Стан |
|---|---|---|
| Українською, ідентифікатори як у коді | усі сторінки своїх розділів | виконано |
| Спільне не дублюється | посилання на [data-ownership.md](../../contracts/docs/data-ownership.md), [errors.md](../../contracts/docs/errors.md), `operations.md` модулів | виконано |
| Приклади перевірено, вказано ревізію | operations: ревізія `48389a3`, 2026-10-11, стек `jane-doc-ops`; приймання — окремі записи про кожен прогін | виконано |
| Обмеження й неперевірене позначено | розділи «Обмеження» та примітки «не перевірялося» на сторінках | виконано |
| Перевірка посилань і повноти | `scripts/docs_check.py` для своїх файлів | частково: посилання на ще не створені сторінки інших розділів |

## Єдиний стиль сторінок

| Вимога (§5) | Де виконано | Стан |
|---|---|---|
| Назва й призначення на початку, зміст для довгих сторінок | усі сторінки своїх розділів | виконано |
| Інструкції: передумови, кроки, результат, прибирання | [running.md](../operations/running.md), [backup-restore.md](../operations/backup-restore.md), [upgrades.md](../operations/upgrades.md) | виконано |
| Чистий Markdown без HTML, відносні посилання | усі сторінки своїх розділів | виконано (`docs_check.py`) |
| Мова кожного блоку коду, команда й вивід окремо | усі сторінки своїх розділів | виконано (`docs_check.py`) |
| Попередження перед командами очищення | `just down -v`, `docker volume rm`, `stack.py down` | виконано |
| Перегляд фактичного рендеру | — | не перевірено |

## Діаграми Draw.io

| Діаграма | Питання | Сторінка | Стан |
|---|---|---|---|
| [data-ownership.drawio](../diagrams/operations/data-ownership.drawio) | хто чим володіє й як це резервувати | [operations/README.md](../operations/README.md#власність-даних) | джерело є, `lint` ok; PNG не експортовано |
| [backup-restore.drawio](../diagrams/operations/backup-restore.drawio) | процес резервування й відновлення | [backup-restore.md](../operations/backup-restore.md) | джерело є, `lint` ok; PNG не експортовано |
| [service-upgrade.drawio](../diagrams/operations/service-upgrade.drawio) | процес оновлення сервісу й відкату | [upgrades.md](../operations/upgrades.md) | джерело є, `lint` ok; PNG не експортовано |
| [criteria-map.drawio](../diagrams/acceptance/criteria-map.drawio) | які наскрізні тести доводять критерії ТЗ §12 | [README.md](README.md) | джерело є, `lint` ok; PNG не експортовано |

Експорт PNG і візуальну перевірку обох тем виконує координатор (`uv run --script scripts/docs_diagrams.py export`).
