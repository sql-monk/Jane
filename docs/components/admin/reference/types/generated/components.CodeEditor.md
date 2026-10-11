# components/CodeEditor

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.CodeEditor.EditorLanguage](#admincomponentscodeeditoreditorlanguage)
- [admin.components.CodeEditor.languageOfPath](#admincomponentscodeeditorlanguageofpath)
- [admin.components.CodeEditor.CodeEditor](#admincomponentscodeeditorcodeeditor)

## admin.components.CodeEditor.EditorLanguage

**Тип.** Код: [web/admin/src/components/CodeEditor.tsx:50](../../../../../../web/admin/src/components/CodeEditor.tsx#L50).

```typescript
export type EditorLanguage = "python" | "json" | "text";
```

## admin.components.CodeEditor.languageOfPath

**Функція.** Код: [web/admin/src/components/CodeEditor.tsx:58](../../../../../../web/admin/src/components/CodeEditor.tsx#L58).

```typescript
function languageOfPath(path: string): EditorLanguage
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `string` | `—` | required |

Результат: `EditorLanguage`.

## admin.components.CodeEditor.CodeEditor

**Функція.** Код: [web/admin/src/components/CodeEditor.tsx:68](../../../../../../web/admin/src/components/CodeEditor.tsx#L68).

```typescript
function CodeEditor({ value, onChange, language, label, readOnly, minHeight, }: { value: string; onChange?: (value: string) => void; language: EditorLanguage; label: string; readOnly?: boolean; minHeight?: string; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ value: string; onChange?: (value: string) => void; language: EditorLanguage; label: string; readOnly?: boolean; minHeight?: string; }` | `—` | required |

Результат: `JSX.Element`.

### Опис із вихідного коду

```text
CodeMirror 6 editor. Uncontrolled inside, synchronised from `value` when it changes from outside
(e.g. another file is opened). `label` becomes the accessible name of the editing surface.
```
