# DOC-02 — Структура й шаблони

Стан: review. Власність зареєстрована в `.claude/wp-paths.json`, окремий ключ documentation_packages; числові WP та markers не змінені.

## Результати

Створено індекс docs, спільний стиль, шість шаблонів, матрицю вимог і статус пакетів. Модульні чернетки явно позначені як неприйняті. Прийнятий README та jane-documentation залишаються еталоном.

## Реальний вивід

```text
DOC-02 scaffold: 87 pages; module drafts explicitly unaccepted
```

## Незалежне рев’ю

Початкову структуру перевіряє archive_review. Фінальна навігація перевіряється в DOC10/11 після наповнення.

## Фактичний перегляд

Edge 155.0.4283.45, Mermaid 11.12.0, marked 17.0.5, highlight.js 11.11.1, Playwright 1.62.1. Реальний browser render та screenshots переглянуто: таблиці читаються, код має кольорове підсвічування, SVG діаграм створені. Українські fragments декодуються перед перевіркою DOM-якорів.

```powershell
node .jane/doc-preview/preview.mjs
```

```text
documentation-style.md: error=null, diagrams=1, codeBlocks=2, tables=1, headingAnchors=true
README.md: error=null, diagrams=4, codeBlocks=7, tables=6, headingAnchors=true
```

Локальні докази: `.jane/doc-preview/render-evidence.json`, `0.png`, `1.png`. Відтворювана заміна прототипу — `scripts/docs/render.mjs` у DOC-03. Шість шаблонів доповнені повними полями module/type/member; матриця охоплює R01–R34, створено матрицю застосовності діаграм. Повторне незалежне рев’ю очікується.
