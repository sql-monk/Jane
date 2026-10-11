# components/ui

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.ui.Page](#admincomponentsuipage)
- [admin.components.ui.Section](#admincomponentsuisection)
- [admin.components.ui.Loading](#admincomponentsuiloading)
- [admin.components.ui.ErrorBox](#admincomponentsuierrorbox)
- [admin.components.ui.Status](#admincomponentsuistatus)
- [admin.components.ui.JsonView](#admincomponentsuijsonview)
- [admin.components.ui.KeyValue](#admincomponentsuikeyvalue)
- [admin.components.ui.Column](#admincomponentsuicolumn)
- [admin.components.ui.Column.header](#admincomponentsuicolumnheader)
- [admin.components.ui.Column.cell](#admincomponentsuicolumncell)
- [admin.components.ui.Column.className](#admincomponentsuicolumnclassname)
- [admin.components.ui.Table](#admincomponentsuitable)
- [admin.components.ui.LoadMore](#admincomponentsuiloadmore)
- [admin.components.ui.Tabs](#admincomponentsuitabs)
- [admin.components.ui.Field](#admincomponentsuifield)
- [admin.components.ui.ActionDialog](#admincomponentsuiactiondialog)
- [admin.components.ui.ReasonAction](#admincomponentsuireasonaction)
- [admin.components.ui.Notice](#admincomponentsuinotice)

## admin.components.ui.Page

**Функція.** Код: [web/admin/src/components/ui.tsx:8](../../../../../../web/admin/src/components/ui.tsx#L8).

```typescript
function Page({ title, actions, children, }: { title: string; actions?: ReactNode; children: ReactNode; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ title: string; actions?: ReactNode; children: ReactNode; }` | `—` | required |

Результат: `any`.

## admin.components.ui.Section

**Функція.** Код: [web/admin/src/components/ui.tsx:33](../../../../../../web/admin/src/components/ui.tsx#L33).

```typescript
function Section({ title, actions, children, }: { title: string; actions?: ReactNode; children: ReactNode; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ title: string; actions?: ReactNode; children: ReactNode; }` | `—` | required |

Результат: `any`.

## admin.components.ui.Loading

**Функція.** Код: [web/admin/src/components/ui.tsx:53](../../../../../../web/admin/src/components/ui.tsx#L53).

```typescript
function Loading({ what }: { what?: string; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ what?: string; }` | `—` | required |

Результат: `any`.

## admin.components.ui.ErrorBox

**Функція.** Код: [web/admin/src/components/ui.tsx:61](../../../../../../web/admin/src/components/ui.tsx#L61).

```typescript
function ErrorBox({ error, title }: { error: unknown; title?: string; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ error: unknown; title?: string; }` | `—` | required |

Результат: `any`.

## admin.components.ui.Status

**Функція.** Код: [web/admin/src/components/ui.tsx:127](../../../../../../web/admin/src/components/ui.tsx#L127).

```typescript
function Status({ value }: { value: string | null | undefined; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ value: string \| null \| undefined; }` | `—` | required |

Результат: `any`.

## admin.components.ui.JsonView

**Функція.** Код: [web/admin/src/components/ui.tsx:133](../../../../../../web/admin/src/components/ui.tsx#L133).

```typescript
function JsonView({ value, compact }: { value: unknown; compact?: boolean; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ value: unknown; compact?: boolean; }` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
Pretty JSON of API data; secret-looking values are always masked (ТЗ §11).
```

## admin.components.ui.KeyValue

**Функція.** Код: [web/admin/src/components/ui.tsx:141](../../../../../../web/admin/src/components/ui.tsx#L141).

```typescript
function KeyValue({ rows }: { rows: Array<[string, ReactNode]>; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ rows: Array<[string, ReactNode]>; }` | `—` | required |

Результат: `any`.

## admin.components.ui.Column

**Інтерфейс.** Код: [web/admin/src/components/ui.tsx:154](../../../../../../web/admin/src/components/ui.tsx#L154).

```typescript
interface Column<T> {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [header](components.ui.md#admincomponentsuicolumnheader) | Поле | ні |
| [cell](components.ui.md#admincomponentsuicolumncell) | Поле | ні |
| [className](components.ui.md#admincomponentsuicolumnclassname) | Поле | ні |

## admin.components.ui.Column.header

**Поле.** Код: [web/admin/src/components/ui.tsx:155](../../../../../../web/admin/src/components/ui.tsx#L155).

```typescript
header: string
```

Доступ: читання — так; запис — так.

## admin.components.ui.Column.cell

**Поле.** Код: [web/admin/src/components/ui.tsx:156](../../../../../../web/admin/src/components/ui.tsx#L156).

```typescript
cell: (row: T) => ReactNode
```

Сигнатури виклику:

```typescript
cell(row: T): ReactNode
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `row` | `T` | `—` | required |

Результат: `ReactNode`.

Доступ: читання — так; запис — так.

## admin.components.ui.Column.className

**Поле.** Код: [web/admin/src/components/ui.tsx:157](../../../../../../web/admin/src/components/ui.tsx#L157).

```typescript
className?: string | undefined
```

Доступ: читання — так; запис — так.

## admin.components.ui.Table

**Функція.** Код: [web/admin/src/components/ui.tsx:170](../../../../../../web/admin/src/components/ui.tsx#L170).

```typescript
function Table<T>({ rows, columns, rowKey, empty, label, }: { rows: readonly T[]; columns: ReadonlyArray<Column<T>>; rowKey: (row: T, index: number) => string; empty?: string; label?: string; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ rows: readonly T[]; columns: ReadonlyArray<Column<T>>; rowKey: (row: T, index: number) => string; empty?: string; label?: string; }` | `—` | required |

Результат: `any`.

## admin.components.ui.LoadMore

**Функція.** Код: [web/admin/src/components/ui.tsx:212](../../../../../../web/admin/src/components/ui.tsx#L212).

```typescript
function LoadMore({ hasMore, loading, onClick, }: { hasMore: boolean; loading: boolean; onClick: () => void; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ hasMore: boolean; loading: boolean; onClick: () => void; }` | `—` | required |

Результат: `any`.

## admin.components.ui.Tabs

**Функція.** Код: [web/admin/src/components/ui.tsx:229](../../../../../../web/admin/src/components/ui.tsx#L229).

```typescript
function Tabs<K extends string>({ tabs, active, onChange, }: { tabs: ReadonlyArray<[K, string]>; active: K; onChange: (key: K) => void; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ tabs: ReadonlyArray<[K, string]>; active: K; onChange: (key: K) => void; }` | `—` | required |

Результат: `any`.

## admin.components.ui.Field

**Функція.** Код: [web/admin/src/components/ui.tsx:256](../../../../../../web/admin/src/components/ui.tsx#L256).

```typescript
function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ label: string; hint?: string; children: ReactNode; }` | `—` | required |

Результат: `any`.

## admin.components.ui.ActionDialog

**Функція.** Код: [web/admin/src/components/ui.tsx:267](../../../../../../web/admin/src/components/ui.tsx#L267).

```typescript
function ActionDialog({ title, onClose, children, }: { title: string; onClose: () => void; children: ReactNode; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ title: string; onClose: () => void; children: ReactNode; }` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
Native modal: focus stays inside it and table rows keep their compact layout.
```

## admin.components.ui.ReasonAction

**Функція.** Код: [web/admin/src/components/ui.tsx:305](../../../../../../web/admin/src/components/ui.tsx#L305).

```typescript
function ReasonAction({ label, confirmLabel, onConfirm, busy, danger, requireReason, modal, }: { label: string; confirmLabel?: string; onConfirm: (reason: string) => void; busy?: boolean; danger?: boolean; requireReason?: boolean; modal?: boolean; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ label: string; confirmLabel?: string; onConfirm: (reason: string) => void; busy?: boolean; danger?: boolean; requireReason?: boolean; modal?: boolean; }` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
A button that asks for a reason (audit) before running a destructive or auditable action.
```

## admin.components.ui.Notice

**Функція.** Код: [web/admin/src/components/ui.tsx:378](../../../../../../web/admin/src/components/ui.tsx#L378).

```typescript
function Notice({ tone, children }: { tone?: "info" | "ok" | "warn"; children: ReactNode; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ tone?: "info" \| "ok" \| "warn"; children: ReactNode; }` | `—` | required |

Результат: `any`.
