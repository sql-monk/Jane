# Інструменти документації

Генератор читає Python AST, TypeScript compiler API та OpenAPI. Він не імпортує production-модулі й не читає значення секретних змінних середовища.

## Підготовка

У корені Jane:

```powershell
uv sync --all-packages
npm ci --prefix scripts/docs --ignore-scripts --no-audit --no-fund
```

Версії npm-залежностей зафіксовані у `scripts/docs/package-lock.json`. Для перегляду потрібен Chromium або встановлений Edge; Windows-приклад використовує його абсолютний шлях.

## Генерація й перевірки

```powershell
just docs-gen
just docs-check
uv run --all-packages python scripts/docs/ownership.py --all
```

`docs-check` звіряє згенеровані сторінки з кодом, перевіряє Markdown і пари PNG. Генерація пише лише `reference/*/generated/` та JSON-індекси; ручні сторінки залишаються окремо. Архів виключений з активних Markdown-перевірок.

| Засіб | Що перевіряє |
|---|---|
| `generate.py --check` | Декларації, члени, перевантаження, API, налаштування та drift |
| `check.py` | Мови блоків, структуру, HTML, links і автоматичні якорі |
| `diagrams.py` | XML-моделі, editable shapes, зв’язки, RGBA, два PNG та hashes |
| `ownership.py --all` | Committed, staged, unstaged, untracked та затверджені архівні видалення |
| `tests/test_tooling.py` | Навмисні дефекти генерації, навігації й власності |

## Draw.io та PNG

Редагуй `.drawio` у Draw.io, потім експортуй обидві теми:

```powershell
just docs-export --browser-executable "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
just docs-render --paths README.md docs/development/documentation-style.md --both-themes --browser-executable "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
```

На Linux можна використати встановлений Chromium Playwright без `--browser-executable`. Експорт використовує mxGraph, перевіряє непорожні та прозорі пікселі й зберігає hashes у `docs/diagrams/manifest.json`. Геометрія та текст спільні для обох тем; кольори адаптуються під відповідне тло. Запуск preview автоматично підставляє темний PNG у темній темі.

## Межі автоматизації

Повнота декларацій і повнота пояснень перевіряються окремо. `symbols.json` містить `explanation_gaps`: відсутній docstring, приклад використання або потребу описати залежні винятки. Реальні приклади взяті з tests/call sites із посиланням на контекст. Цей список потрібно закрити авторськими поясненнями перед повним прийманням MSDN-довідника.

Статична перевірка PNG не підтверджує читабельність усіх схем; після зміни графіки відкрий preview та переглянь її на обох фонах. Команди й результати конкретного запуску записуються у [звітах](../delivery/documentation/status.md).
