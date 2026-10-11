# Модуль `components.ui`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/ui.tsx](../../../../../web/admin/src/components/ui.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `Page`

```typescript
function Page({ title, actions, children, description: pageDescription, }: { title: string; description?: string; actions?: React.ReactNode; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:19](../../../../../web/admin/src/components/ui.tsx#L19).

### Компонент `Section`

```typescript
function Section({ title, actions, children, }: { title: string; actions?: React.ReactNode; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:46](../../../../../web/admin/src/components/ui.tsx#L46).

### Компонент `Loading`

```typescript
function Loading({ what }: { what?: string; }): React.JSX.Element
```

Код: [ui.tsx:66](../../../../../web/admin/src/components/ui.tsx#L66).

### Компонент `ErrorBox`

```typescript
function ErrorBox({ error, title }: { error: unknown; title?: string; }): React.JSX.Element | null
```

Код: [ui.tsx:74](../../../../../web/admin/src/components/ui.tsx#L74).

### Компонент `Status`

```typescript
function Status({ value }: { value: string | null | undefined; }): React.JSX.Element
```

Код: [ui.tsx:155](../../../../../web/admin/src/components/ui.tsx#L155).

### Компонент `JsonView`

```typescript
function JsonView({ value, compact }: { value: unknown; compact?: boolean; }): React.JSX.Element
```

Pretty JSON of API data; secret-looking values are always masked (ТЗ §11).

Код: [ui.tsx:165](../../../../../web/admin/src/components/ui.tsx#L165).

### Компонент `KeyValue`

```typescript
function KeyValue({ rows }: { rows: [string, React.ReactNode][]; }): React.JSX.Element
```

Код: [ui.tsx:173](../../../../../web/admin/src/components/ui.tsx#L173).

### Компонент `Table`

```typescript
function Table<T>({ rows, columns, rowKey, empty, label, loading, error, }: { rows: readonly T[]; columns: readonly import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/components/ui").Column<T>[]; rowKey: (row: T, index: number) => string; empty?: string; label?: string; loading?: boolean; error?: unknown; }): React.JSX.Element | null
```

Код: [ui.tsx:202](../../../../../web/admin/src/components/ui.tsx#L202).

### Компонент `LoadMore`

```typescript
function LoadMore({ hasMore, loading, onClick, }: { hasMore: boolean; loading: boolean; onClick: () => void; }): React.JSX.Element | null
```

Код: [ui.tsx:250](../../../../../web/admin/src/components/ui.tsx#L250).

### Компонент `Tabs`

```typescript
function Tabs<K extends string>({ tabs, active, onChange, }: { tabs: readonly [K, string][]; active: K; onChange: (key: K) => void; }): React.JSX.Element
```

Код: [ui.tsx:267](../../../../../web/admin/src/components/ui.tsx#L267).

### Компонент `Field`

```typescript
function Field({ label, hint, error, children, }: { label: string; hint?: string; error?: string | undefined; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:294](../../../../../web/admin/src/components/ui.tsx#L294).

### Компонент `ActionDialog`

```typescript
function ActionDialog({ title, onClose, children, }: { title: string; onClose: () => void; children: React.ReactNode; }): React.ReactPortal
```

Native modal: focus stays inside it and table rows keep their compact layout.

Код: [ui.tsx:370](../../../../../web/admin/src/components/ui.tsx#L370).

### Компонент `ReasonAction`

```typescript
function ReasonAction({ label, confirmLabel, onConfirm, busy, danger, requireReason, modal, impact, }: { label: string; confirmLabel?: string; onConfirm: (reason: string) => void; busy?: boolean; danger?: boolean; requireReason?: boolean; modal?: boolean; impact?: React.ReactNode; }): React.JSX.Element
```

A button that asks for a reason (audit) before running a destructive or auditable action.

Код: [ui.tsx:408](../../../../../web/admin/src/components/ui.tsx#L408).

### Компонент `Notice`

```typescript
function Notice({ tone, children }: { tone?: "info" | "ok" | "warn"; children: React.ReactNode; }): React.JSX.Element
```

Код: [ui.tsx:484](../../../../../web/admin/src/components/ui.tsx#L484).

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

Код: [ui.tsx:186](../../../../../web/admin/src/components/ui.tsx#L186).
