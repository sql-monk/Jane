# DOC-05-handler-runtime — Handler Runtime

Статус: **review**. Повний ручний комплект створено; приймання потребує незалежного відтворення, загального PNG-експорту/рендеру та зведення runtime evidence координатором.

## Ревізія й власність

Гілка codex/documentation-rebuild-20261011; вихідна ревізія 91876d1c369e91838cee9204658cc92a248adf95. Середовище автора: Windows, PowerShell 7 без профілю, Python із -X utf8. Зміст перевірений за поточними services/handler-runtime, contracts і Settings; архівовані тексти не використано.

Власність: docs/components/handler-runtime без reference/*/generated, docs/diagrams/handler-runtime, цей звіт. Production code, contracts, skills і довідник generated автор не редагував. Ручна документація розміщується окремо, тому повторна генерація її не перезаписує.

## Результати

Створено дев’ять сторінок: README, quickstart, dependencies, configuration, integration, internals, operations, reference/api/README і reference/types/README. Входи/виходи, гарантії, HTTP/Result errors, optional dependencies, власні дані й recovery описані окремо. Public declarations зв’язано з ручними поясненнями модулів/членів та прикладами.

Configuration містить повний перелік власних і успадкованих Settings fields та власних scalar ServiceLimits; shared limits посилаються на Jane Kit. Defaults/constraints прочитано з AST коду, без читання env secrets. Неточний DOC-03 contract_field default повідомлено координатору та ним виправлено.

## Матриця діаграм

| Вид | Редаговане джерело | Питання |
|---|---|---|
| Контекст, компоненти, залежності | [context](../../diagrams/handler-runtime/context.drawio) | Сусіди, автономність, API та own store |
| Розгортання | [context](../../diagrams/handler-runtime/context.drawio) | Реальні process/store залежності; профілі платформи документує DOC-04 |
| Класи | [classes](../../diagrams/handler-runtime/classes.drawio) | Об’єкти, протоколи та wiring |
| ER / власні дані | [data](../../diagrams/handler-runtime/data.drawio) | Власність і логічні зв’язки; не всі стрілки SQL FK |
| Послідовність | [invoke-sequence](../../diagrams/handler-runtime/invoke-sequence.drawio) | API/запис/читання та async відповідь |
| Стани | [states](../../diagrams/handler-runtime/states.drawio) | Реальні переходи або кінцеві Result status |
| Потік, алгоритм | [execution-flow](../../diagrams/handler-runtime/execution-flow.drawio) | Перевірки/доставка та помилкові гілки |
| Процес, сценарій оператора | [operator-process](../../diagrams/handler-runtime/operator-process.drawio) | Оновлення/перевірка/відновлення або activation |

Незастосовних видів немає: змістово пов’язані питання об’єднано в сім схем. Джерела містять mxCell вузли й ребра, а не вкладені flat images. Markdown використовує light PNG та links dark/source. Обидва PNG експортує координатор з того самого джерела; global manifest поза власністю цього пакета.

## Статичні перевірки

Команда scoped Markdown:

```powershell
python -X utf8 scripts/docs/check.py --paths docs/components/registry docs/components/handler-runtime docs/components/orchestrator
```

Перший реальний вивід спільної перевірки трьох доручених компонентів:

```text
Markdown check: 149 files, 3885 links, 0 diagrams, 1866 code blocks, 47 errors
```

42 помилки — ще не експортовані themed PNG; три — звіти, створені після перевірки; дві — regex constraint у plain table, виправлені inline code. Значення diagrams=0 означає відсутність Mermaid fences у Markdown; Draw.io перевіряється окремо. Остаточний scoped результат доповнить координатор після PNG.

Реальний парсинг scripts/docs/diagrams.model усіх власних sources:

```text
XML models: 21 OK
```

Сюди входить сім схем Handler Runtime; перевірено mxfile/model, IDs, geometry і referential edges. Парсинг не є фактичним переглядом PNG.

## Виконання й рендер

Координатор підтвердив tests minimal-package через справжній Docker: 2 passed, 0 failed. Це coordinator-run, а не власний запуск виконавця DOC-05.

Власний offline запуск через uv --offline --no-sync --all-packages уперся у sandbox cache:

```text
failed to persist temporary file: Access is denied. (os error 5)
```

Процес зупинено; Docker, зовнішні мережеві тести й контейнери цим автором не запускались. Фактичний PNG експорт, RGBA/pixel/checksum, сторінки light/dark та visual review очікують coordinator gate. Windows/Linux незалежний quickstart ще не підтверджено; зовнішні backend не перевірено на реальному сервісі.

## Відповідність ТЗ й обмеження

Автономність, versioned API та власність даних узгоджені з ТЗ §4–7. Межі реалізації описано поруч із можливостями; memory state не видається за довговічне масштабування, Result failed не видається за успішне виконання за HTTP 200. Для Registry явні port/fork не активують task, для Runtime заборонена мережа й лише Python extractor/transform, для Orchestrator прямий pipeline виклик ідемпотентного executor не є розподіленою exactly-once гарантією.

## Незалежне рев’ю та запити

Вердикт незалежного рецензента очікується. Координатор має додати результати PNG/Markdown render, runtime reproduction на обох ОС та остаточний scoped checker. Нові контрактні поля або зміна функціональності не потрібні.
