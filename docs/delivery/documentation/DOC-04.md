# DOC-04 — Огляд та архітектура

Стан: авторська робота для незалежного review; приймання залежностей і фактичного рендеру координує власник плану. Дата: 2026-10-11. Основа коду: `91876d1c369e91838cee9204658cc92a248adf95`.

## Межі роботи

Власність: `docs/overview/`, `docs/architecture/`, нові `docs/adr/`, `docs/diagrams/platform/` і цей звіт. Застосовано `jane-documentation`; старі архівні описи й діаграми як основу не читано.

## Результат

- [Огляд](../../overview/README.md): призначення, типи модулів, сценарії, можливості й межі.
- [Терміни](../../overview/glossary.md): дані, пакети, завдання, invocation, jobs і доставка.
- [Архітектура](../../architecture/README.md): автономність, контракти, власність даних, async, надійність, безпека, deployment, ліміти та карта репозиторію.
- [Відповідність ТЗ](../../architecture/conformance.md): окремі записи про SQLite multi-host, sandbox-доступи, прийняту технологію Registry і memory-стан.
- [Вісім ADR](../../adr/README.md): нові тексти з посиланнями на перевірені джерела; `0005-authentication.md` збережено як актуальний шлях.
- [Вісім діаграм](../../diagrams/platform/README.md): контекст, компоненти, залежності, dataflow, ER документів, sequence, state і deployment. Джерела inline; індекс посилається на єдині копії.

## Джерела фактів

ТЗ §4–§13; OpenAPI й JSON Schema; settings, state, engine, executors, content, auth, secrets, storage merge; Compose, PostgreSQL provisioning і profiles; точки входу Python та React.

Сервісні виклики відділено від логічного потоку даних. ER показує документи контрактів, а не спільні таблиці; вкладені поля пояснено. Не заявлено безумовне exactly-once або підтримку довільного multi-host SQLite.

## Реальний вивід перевірок

Команди виконані з кореня Jane після виправлення якоря заголовка «Зв’язки документів» і звірки Registry blob backend. Нижче фактичний вивід останнього запуску; exit code `0`.

```powershell
python -X utf8 scripts/docs/check.py --paths docs/overview docs/architecture docs/adr docs/diagrams/platform docs/delivery/documentation/DOC-04.md --json
python -X utf8 scripts/docs/ownership.py --doc DOC-04 --paths docs/overview docs/architecture docs/adr docs/diagrams/platform docs/delivery/documentation/DOC-04.md
```

```json
{
  "files": 21,
  "links": 333,
  "diagrams": 8,
  "code_blocks": 9,
  "errors": []
}
```

```text
DOC ownership: 28 paths (committed/staged/unstaged/untracked), 0 violations; scoped
```

Ownership є scoped-перевіркою. Її 28 шляхів включають попередні архівні видалення ADR у спільному checkout; вона не є прийманням усього checkout або підтвердженням авторства цих видалень.

## Рендер

Статичний checker перевірив структуру, мови блоків і посилання. Фактичне відображення восьми Mermaid та сторінок у світлій/темній темі перевіряє координатор через DOC-03 renderer; до цього автор не заявляє render gate пройденим.

## Неперевірене

Runtime-сценарії, зовнішні сервіси, навантаження профілів і довільний multi-host транспорт у DOC-04 не запускалися. Текст описує поточні джерела, а відповідні обмеження наведені безпосередньо в архітектурі.

## Запити до інших власників

- DOC-03: парсинг і фактичний світлий/темний рендер восьми Mermaid-блоків та сторінок.
- DOC-10: остаточна навігація після наповнення модулів.
- DOC-11: незалежне review фактів, семантики діаграм і критеріїв DOC-04.

## Незалежне рев’ю

Автор не приймає власний пакет. DOC-02 на момент початку авторства перебував у review до render gate; DOC-03 розроблявся паралельно. Цей звіт не позначає їх завершеними.
