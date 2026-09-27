# jane.llm-event-extractor

Пакет типу `llm` (виконавець — сервіс `llm`, WP-10). Витягує події з повідомлень: інструкції —
`prompts/instructions.md` (довірений канал), вміст матеріалу підставляється в `prompts/input.md` і
передається моделі лише як недовірені дані. Вихід — `schemas/output.schema.json`, сутності `event`
з ключем `message` (= `material_id`).

Тести: `concert` (success) і `prompt-injection-is-data` (ін'єкція у вмісті, очікується `empty`).
Запуск без запису: `POST /v1/test-runs` сервісу `llm`.
