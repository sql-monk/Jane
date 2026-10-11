# Модуль `pages.PackagesPage`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/pages/PackagesPage.tsx](../../../../../web/admin/src/pages/PackagesPage.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `PackagesPage`

```typescript
function PackagesPage(): React.JSX.Element
```

Код: [PackagesPage.tsx:37](../../../../../web/admin/src/pages/PackagesPage.tsx#L37).

### Компонент `PackagePage`

```typescript
function PackagePage(): React.JSX.Element
```

Код: [PackagesPage.tsx:169](../../../../../web/admin/src/pages/PackagesPage.tsx#L169).

### Компонент `DiffView`

```typescript
function DiffView({ diff }: { diff: { from: { package_id: string; version: string; digest?: string; }; to: { package_id: string; version: string; digest?: string; }; manifest_changes?: { pointer: string; op: "replace" | "add" | "remove"; old?: unknown; new?: unknown; }[]; files: { path: string; status: "added" | "removed" | "modified" | "unchanged"; unified_diff?: string; binary?: boolean; }[]; }; }): React.JSX.Element
```

Код: [PackagesPage.tsx:578](../../../../../web/admin/src/pages/PackagesPage.tsx#L578).
