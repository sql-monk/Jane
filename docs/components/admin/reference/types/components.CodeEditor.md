# Модуль `components.CodeEditor`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/CodeEditor.tsx](../../../../../web/admin/src/components/CodeEditor.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `CodeEditor`

```typescript
function CodeEditor({ value, onChange, language, label, readOnly, minHeight, }: { value: string; onChange?: (value: string) => void; language: import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/components/CodeEditor").EditorLanguage; label: string; readOnly?: boolean; minHeight?: string; }): React.JSX.Element
```

CodeMirror 6 editor. Uncontrolled inside, synchronised from `value` when it changes from outside (e.g. another file is opened). `label` becomes the accessible name of the editing surface.

Код: [CodeEditor.tsx:68](../../../../../web/admin/src/components/CodeEditor.tsx#L68).

## Функції

### Функція `languageOfPath`

```typescript
function languageOfPath(path: string): import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/components/CodeEditor").EditorLanguage
```

Код: [CodeEditor.tsx:58](../../../../../web/admin/src/components/CodeEditor.tsx#L58).

## Типи

### Тип `EditorLanguage`

```typescript
type EditorLanguage = "python" | "json" | "text";
```

Код: [CodeEditor.tsx:50](../../../../../web/admin/src/components/CodeEditor.tsx#L50).
