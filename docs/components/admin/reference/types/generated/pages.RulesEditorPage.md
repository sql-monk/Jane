# pages/RulesEditorPage

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.pages.RulesEditorPage.STRATEGY_TEMPLATES](#adminpagesruleseditorpagestrategy_templates)
- [admin.pages.RulesEditorPage.STRATEGY_LABELS](#adminpagesruleseditorpagestrategy_labels)
- [admin.pages.RulesEditorPage.StrategiesSummary](#adminpagesruleseditorpagestrategiessummary)
- [admin.pages.RulesEditorPage.RulesEditorPage](#adminpagesruleseditorpageruleseditorpage)

## admin.pages.RulesEditorPage.STRATEGY_TEMPLATES

**Константа.** Код: [web/admin/src/pages/RulesEditorPage.tsx:23](../../../../../../web/admin/src/pages/RulesEditorPage.tsx#L23).

```typescript
STRATEGY_TEMPLATES: Record<string, Json> = {
  seed_list: { type: "seed_list", urls: ["https://example.test/"] },
  recursive: { type: "recursive", seeds: ["https://example.test/"], follow: [{ value: "example.test/**" }] },
  sitemap: { type: "sitemap", use_robots_txt: true },
  feed: { type: "feed", autodiscover: true },
  listing: {
    type: "listing",
    start_urls: ["https://example.test/catalog"],
    next_page: { type: "rel", value: "next" },
  },
  url_template: {
    type: "url_template",
    template: "https://example.test/item/{id}",
    variables: { id: { range: { start: 1, end: 100 } } },
  },
  api_feed: {
    type: "api_feed",
    url: "https://example.test/api/items",
    items_path: "$.items",
    url_path: "$.url",
  },
  llm_explore: { type: "llm_explore", goal: "find product pages" },
}
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Templates for every strategy type of collector-rules.schema.json#/$defs/Strategy (required fields only).
```

## admin.pages.RulesEditorPage.STRATEGY_LABELS

**Константа.** Код: [web/admin/src/pages/RulesEditorPage.tsx:47](../../../../../../web/admin/src/pages/RulesEditorPage.tsx#L47).

```typescript
STRATEGY_LABELS: Record<string, string> = {
  seed_list: "Явний перелік URL",
  recursive: "Рекурсивний обхід посилань",
  sitemap: "Sitemap / Sitemap Index",
  feed: "RSS / Atom",
  listing: "Категорії, пагінація, пошук",
  url_template: "Шаблон URL",
  api_feed: "API / JSON-канал",
  llm_explore: "Дослідження за допомогою LLM",
}
```

Доступ: читання — так; запис — так.

## admin.pages.RulesEditorPage.StrategiesSummary

**Функція.** Код: [web/admin/src/pages/RulesEditorPage.tsx:88](../../../../../../web/admin/src/pages/RulesEditorPage.tsx#L88).

```typescript
function StrategiesSummary({ rules: ref }: { rules: PackageRef; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ rules: PackageRef; }` | `—` | required |

Результат: `JSX.Element`.

### Опис із вихідного коду

```text
Read-only summary of the strategies a source uses (source page).
```

## admin.pages.RulesEditorPage.RulesEditorPage

**Функція.** Код: [web/admin/src/pages/RulesEditorPage.tsx:121](../../../../../../web/admin/src/pages/RulesEditorPage.tsx#L121).

```typescript
function RulesEditorPage(): JSX.Element
```

Результат: `JSX.Element`.
