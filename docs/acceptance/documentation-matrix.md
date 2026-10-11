# Матриця приймання документації

Кожна вимога має результат, відповідального власника й окремий спосіб перевірки. Під час наповнення DOC-05 загальні індекси уточнюються посиланнями на відповідні сторінки кожного модуля.

| ID / вимога | Власник | Документ | Перевірка / стан |
|---|---|---|---|
| R01: Архівування та SHA | DOC-00/01 | `../../../docs-archive/inventory.json` (плановий результат) | копії, coverage, винятки; accepted |
| R02: Збереження нових артефактів | DOC-01 | [Результат](../../README.md) | SHA та paths; accepted |
| R03: Українська мова та терміни | усі | [Результат](../overview/README.md) | редакторське рев’ю; ready |
| R04: Заголовки й зміст | усі | [Результат](../README.md) | headings і якорі; ready |
| R05: Локальні links/anchors | DOC-03/10 | [Результат](../README.md) | автоматична перевірка; ready |
| R06: Мови всіх блоків коду | DOC-03/усі | [Результат](../development/documentation-style.md) | fences та рендер; review |
| R07: Відсутність сирого HTML | DOC-03/усі | [Результат](../development/documentation-style.md) | статична перевірка; review |
| R08: Типи й каталог модулів | DOC-10 | [Результат](../components/README.md) | повнота11 модулів; ready |
| R09: Призначення та межі | DOC-05-* | [Результат](../components/README.md) | огляд кожного модуля; ready |
| R10: Незалежний запуск | DOC-05-* | [Результат](../components/README.md) | відтворення без full stack; ready |
| R11: Обов’язкові/опційні залежності | DOC-05-* | [Результат](../components/README.md) | код та конфігурація; ready |
| R12: Входи, виходи, помилки, гарантії | DOC-05-* | [Результат](../reference/README.md) | контракти й приклади; ready |
| R13: Стороння інтеграція й заміна | DOC-05-* | [Результат](../components/README.md) | приклад автономного виклику; ready |
| R14: Власність даних | DOC-04/05 | [Результат](../architecture/README.md) | схеми й код доступу; ready |
| R15: Дерево й точки входу | DOC-04 | `../architecture/repository-map.md` (плановий результат) | файли й entrypoints; ready |
| R16: Публічні типи та успадкування | DOC-03/05 | `../reference/symbols.json` (плановий результат) | облік декларацій і reexports; ready |
| R17: Усі публічні члени | DOC-03/05 | `../reference/symbols.json` (плановий результат) | методи/властивості/поля/константи; ready |
| R18: Сигнатури, параметри, результати | DOC-03/05 | [Результат](../reference/README.md) | AST/OpenAPI та приклади; ready |
| R19: Винятки, обмеження й доступність | DOC-05-* | [Результат](../reference/README.md) | код та ручний довідник; ready |
| R20: API й моделі | DOC-03/05 | `../reference/api-operations.json` (плановий результат) | усі OpenAPI operations; ready |
| R21: Налаштування й ліміти | DOC-03/05 | `../reference/configuration.json` (плановий результат) | типи/defaults/ENV; ready |
| R22: Пакети та сумісність | DOC-06 | `../reference/packages/README.md` (плановий результат) | схема/runtime/registry; ready |
| R23: Усі доречні діаграми | DOC-04/05 | [Результат](diagram-matrix.md) | матриця застосовності; review |
| R24: Семантика схем | DOC-04/05 | [Результат](diagram-matrix.md) | код/API/ownership; ready |
| R25: Парсинг Mermaid | DOC-03 | `../development/documentation-tools.md` (плановий результат) | renderer parse; ready |
| R26: Фактичний рендер і підсвічування | DOC-03/11 | `documentation-review.md` (плановий результат) | browser/screenshots; ready |
| R27: Швидкий старт і сценарії | DOC-07 | [Результат](../getting-started/README.md) | перший результат; ready |
| R28: Моніторинг і діагностика | DOC-08 | [Результат](../operations/README.md) | logs/metrics/runbooks; ready |
| R29: Оновлення, міграції, backup/restore | DOC-08 | `../operations/backup-restore.md` (плановий результат) | ізольоване відновлення; ready |
| R30: Розробка й розширення | DOC-09 | [Результат](../development/README.md) | документовані команди; ready |
| R31: ADR та приймання ТЗ | DOC-04/11 | [Результат](../adr/README.md) | source-backed рішення; ready |
| R32: Відтворювана генерація й drift | DOC-03 | `../development/documentation-tools.md` (плановий результат) | повторна генерація/check; ready |
| R33: Ревізія, чесні межі й реальні докази | усі/11 | [Результат](../delivery/documentation/status.md) | звіт окремо static/render/runtime; ready |
| R34: Windows/Linux та зовнішній доступ | DOC-05/07/08/11 | `documentation-review.md` (плановий результат) | окремі результати ОС/провайдерів; ready |
