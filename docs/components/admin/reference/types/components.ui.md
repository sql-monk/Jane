# Модуль `components.ui`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/ui.tsx](../../../../../web/admin/src/components/ui.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `Page`

```typescript
function Page({ title, actions, children, }: { title: string; actions?: React.ReactNode; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:8](../../../../../web/admin/src/components/ui.tsx#L8).

### Компонент `Section`

```typescript
function Section({ title, actions, children, }: { title: string; actions?: React.ReactNode; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:33](../../../../../web/admin/src/components/ui.tsx#L33).

### Компонент `Loading`

```typescript
function Loading({ what }: { what?: string; }): React.JSX.Element
```

Код: [ui.tsx:53](../../../../../web/admin/src/components/ui.tsx#L53).

### Компонент `ErrorBox`

```typescript
function ErrorBox({ error, title }: { error: unknown; title?: string; }): React.JSX.Element | null
```

Код: [ui.tsx:61](../../../../../web/admin/src/components/ui.tsx#L61).

### Компонент `Status`

```typescript
function Status({ value }: { value: string | null | undefined; }): React.JSX.Element
```

Код: [ui.tsx:127](../../../../../web/admin/src/components/ui.tsx#L127).

### Компонент `JsonView`

```typescript
function JsonView({ value, compact }: { value: unknown; compact?: boolean; }): React.JSX.Element
```

Pretty JSON of API data; secret-looking values are always masked (ТЗ §11).

Код: [ui.tsx:133](../../../../../web/admin/src/components/ui.tsx#L133).

### Компонент `KeyValue`

```typescript
function KeyValue({ rows }: { rows: [string, React.ReactNode][]; }): React.JSX.Element
```

Код: [ui.tsx:141](../../../../../web/admin/src/components/ui.tsx#L141).

### Компонент `Table`

```typescript
function Table<T>({ rows, columns, rowKey, empty, label, }: { rows: readonly T[]; columns: readonly import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/components/ui").Column<T>[]; rowKey: (row: T, index: number) => string; empty?: string; label?: string; }): React.JSX.Element
```

Код: [ui.tsx:170](../../../../../web/admin/src/components/ui.tsx#L170).

### Компонент `LoadMore`

```typescript
function LoadMore({ hasMore, loading, onClick, }: { hasMore: boolean; loading: boolean; onClick: () => void; }): React.JSX.Element | null
```

Код: [ui.tsx:212](../../../../../web/admin/src/components/ui.tsx#L212).

### Компонент `Tabs`

```typescript
function Tabs<K extends string>({ tabs, active, onChange, }: { tabs: readonly [K, string][]; active: K; onChange: (key: K) => void; }): React.JSX.Element
```

Код: [ui.tsx:229](../../../../../web/admin/src/components/ui.tsx#L229).

### Компонент `Field`

```typescript
function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:256](../../../../../web/admin/src/components/ui.tsx#L256).

### Компонент `ActionDialog`

```typescript
function ActionDialog({ title, onClose, children, }: { title: string; onClose: () => void; children: React.ReactNode; }): React.ReactPortal
```

Native modal: focus stays inside it and table rows keep their compact layout.

Код: [ui.tsx:267](../../../../../web/admin/src/components/ui.tsx#L267).

### Компонент `ReasonAction`

```typescript
function ReasonAction({ label, confirmLabel, onConfirm, busy, danger, requireReason, modal, }: { label: string; confirmLabel?: string; onConfirm: (reason: string) => void; busy?: boolean; danger?: boolean; requireReason?: boolean; modal?: boolean; }): React.JSX.Element
```

A button that asks for a reason (audit) before running a destructive or auditable action.

Код: [ui.tsx:305](../../../../../web/admin/src/components/ui.tsx#L305).

### Компонент `Notice`

```typescript
function Notice({ tone, children }: { tone?: "info" | "ok" | "warn"; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:378](../../../../../web/admin/src/components/ui.tsx#L378).

## Інтерфейси

### Інтерфейс `Column`

```typescript
interface Column<T>
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `header` | `string` | так | читання й запис |  |
| `cell` | `(row: T) => ReactNode` | так | читання й запис |  |
| `className` | `string` | ні | читання й запис |  |

Код: [ui.tsx:154](../../../../../web/admin/src/components/ui.tsx#L154).
