# components/JsonEditor

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.JsonEditor.JsonCheck](#admincomponentsjsoneditorjsoncheck)
- [admin.components.JsonEditor.JsonCheck.value](#admincomponentsjsoneditorjsoncheckvalue)
- [admin.components.JsonEditor.JsonCheck.parseError](#admincomponentsjsoneditorjsoncheckparseerror)
- [admin.components.JsonEditor.JsonCheck.issues](#admincomponentsjsoneditorjsoncheckissues)
- [admin.components.JsonEditor.JsonCheck.ok](#admincomponentsjsoneditorjsoncheckok)
- [admin.components.JsonEditor.checkJson](#admincomponentsjsoneditorcheckjson)
- [admin.components.JsonEditor.JsonEditor](#admincomponentsjsoneditorjsoneditor)
- [admin.components.JsonEditor.toJsonText](#admincomponentsjsoneditortojsontext)

## admin.components.JsonEditor.JsonCheck

**Інтерфейс.** Код: [web/admin/src/components/JsonEditor.tsx:5](../../../../../../web/admin/src/components/JsonEditor.tsx#L5).

```typescript
interface JsonCheck {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [value](components.JsonEditor.md#admincomponentsjsoneditorjsoncheckvalue) | Поле | ні |
| [parseError](components.JsonEditor.md#admincomponentsjsoneditorjsoncheckparseerror) | Поле | ні |
| [issues](components.JsonEditor.md#admincomponentsjsoneditorjsoncheckissues) | Поле | ні |
| [ok](components.JsonEditor.md#admincomponentsjsoneditorjsoncheckok) | Поле | ні |

## admin.components.JsonEditor.JsonCheck.value

**Поле.** Код: [web/admin/src/components/JsonEditor.tsx:6](../../../../../../web/admin/src/components/JsonEditor.tsx#L6).

```typescript
value: unknown
```

Доступ: читання — так; запис — так.

## admin.components.JsonEditor.JsonCheck.parseError

**Поле.** Код: [web/admin/src/components/JsonEditor.tsx:7](../../../../../../web/admin/src/components/JsonEditor.tsx#L7).

```typescript
parseError: string | null
```

Доступ: читання — так; запис — так.

## admin.components.JsonEditor.JsonCheck.issues

**Поле.** Код: [web/admin/src/components/JsonEditor.tsx:8](../../../../../../web/admin/src/components/JsonEditor.tsx#L8).

```typescript
issues: SchemaIssue[]
```

Доступ: читання — так; запис — так.

## admin.components.JsonEditor.JsonCheck.ok

**Поле.** Код: [web/admin/src/components/JsonEditor.tsx:9](../../../../../../web/admin/src/components/JsonEditor.tsx#L9).

```typescript
ok: boolean
```

Доступ: читання — так; запис — так.

## admin.components.JsonEditor.checkJson

**Функція.** Код: [web/admin/src/components/JsonEditor.tsx:12](../../../../../../web/admin/src/components/JsonEditor.tsx#L12).

```typescript
function checkJson(text: string, schema?: SchemaRef): JsonCheck
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `string` | `—` | required |
| `schema` | `string \| undefined` | `—` | required |

Результат: `JsonCheck`.

## admin.components.JsonEditor.JsonEditor

**Функція.** Код: [web/admin/src/components/JsonEditor.tsx:29](../../../../../../web/admin/src/components/JsonEditor.tsx#L29).

```typescript
function JsonEditor({ text, onChange, schema, label, minHeight, }: { text: string; onChange: (text: string) => void; schema?: SchemaRef; label: string; minHeight?: string; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ text: string; onChange: (text: string) => void; schema?: SchemaRef; label: string; minHeight?: string; }` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
JSON editor validated against a contract JSON Schema (early feedback; the service validates again).
```

## admin.components.JsonEditor.toJsonText

**Функція.** Код: [web/admin/src/components/JsonEditor.tsx:73](../../../../../../web/admin/src/components/JsonEditor.tsx#L73).

```typescript
function toJsonText(value: unknown): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `unknown` | `—` | required |

Результат: `string`.
