# Модуль `components.JsonEditor`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/JsonEditor.tsx](../../../../../web/admin/src/components/JsonEditor.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `JsonEditor`

```typescript
function JsonEditor({ text, onChange, schema, label, minHeight, }: { text: string; onChange: (text: string) => void; schema?: string; label: string; minHeight?: string; }): React.JSX.Element
```

JSON editor validated against a contract JSON Schema (early feedback; the service validates again).

Код: [JsonEditor.tsx:29](../../../../../web/admin/src/components/JsonEditor.tsx#L29).

## Функції

### Функція `checkJson`

```typescript
function checkJson(text: string, schema?: string | undefined): import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/components/JsonEditor").JsonCheck
```

Код: [JsonEditor.tsx:12](../../../../../web/admin/src/components/JsonEditor.tsx#L12).

### Функція `toJsonText`

```typescript
function toJsonText(value: unknown): string
```

Код: [JsonEditor.tsx:73](../../../../../web/admin/src/components/JsonEditor.tsx#L73).

## Інтерфейси

### Інтерфейс `JsonCheck`

```typescript
interface JsonCheck
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `value` | `unknown` | так | читання й запис |  |
| `parseError` | `string \| null` | так | читання й запис |  |
| `issues` | `SchemaIssue[]` | так | читання й запис |  |
| `ok` | `boolean` | так | читання й запис |  |

Код: [JsonEditor.tsx:5](../../../../../web/admin/src/components/JsonEditor.tsx#L5).
