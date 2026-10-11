# lib/dag

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.lib.dag.DagNode](#adminlibdagdagnode)
- [admin.lib.dag.DagNode.id](#adminlibdagdagnodeid)
- [admin.lib.dag.DagNode.kind](#adminlibdagdagnodekind)
- [admin.lib.dag.DagNode.title](#adminlibdagdagnodetitle)
- [admin.lib.dag.DagNode.label](#adminlibdagdagnodelabel)
- [admin.lib.dag.DagNode.layer](#adminlibdagdagnodelayer)
- [admin.lib.dag.DagNode.order](#adminlibdagdagnodeorder)
- [admin.lib.dag.DagEdge](#adminlibdagdagedge)
- [admin.lib.dag.DagEdge.from](#adminlibdagdagedgefrom)
- [admin.lib.dag.DagEdge.to](#adminlibdagdagedgeto)
- [admin.lib.dag.DagEdge.select](#adminlibdagdagedgeselect)
- [admin.lib.dag.DagEdge.conditional](#adminlibdagdagedgeconditional)
- [admin.lib.dag.Dag](#adminlibdagdag)
- [admin.lib.dag.Dag.nodes](#adminlibdagdagnodes)
- [admin.lib.dag.Dag.edges](#adminlibdagdagedges)
- [admin.lib.dag.Dag.issues](#adminlibdagdagissues)
- [admin.lib.dag.stageLabel](#adminlibdagstagelabel)
- [admin.lib.dag.buildDag](#adminlibdagbuilddag)

## admin.lib.dag.DagNode

**Інтерфейс.** Код: [web/admin/src/lib/dag.ts:4](../../../../../../web/admin/src/lib/dag.ts#L4).

```typescript
interface DagNode {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [id](lib.dag.md#adminlibdagdagnodeid) | Поле | ні |
| [kind](lib.dag.md#adminlibdagdagnodekind) | Поле | ні |
| [title](lib.dag.md#adminlibdagdagnodetitle) | Поле | ні |
| [label](lib.dag.md#adminlibdagdagnodelabel) | Поле | ні |
| [layer](lib.dag.md#adminlibdagdagnodelayer) | Поле | ні |
| [order](lib.dag.md#adminlibdagdagnodeorder) | Поле | ні |

## admin.lib.dag.DagNode.id

**Поле.** Код: [web/admin/src/lib/dag.ts:5](../../../../../../web/admin/src/lib/dag.ts#L5).

```typescript
id: string
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagNode.kind

**Поле.** Код: [web/admin/src/lib/dag.ts:6](../../../../../../web/admin/src/lib/dag.ts#L6).

```typescript
kind: "collect" | "handler"
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagNode.title

**Поле.** Код: [web/admin/src/lib/dag.ts:7](../../../../../../web/admin/src/lib/dag.ts#L7).

```typescript
title: string
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagNode.label

**Поле.** Код: [web/admin/src/lib/dag.ts:8](../../../../../../web/admin/src/lib/dag.ts#L8).

```typescript
label: string
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagNode.layer

**Поле.** Код: [web/admin/src/lib/dag.ts:9](../../../../../../web/admin/src/lib/dag.ts#L9).

```typescript
layer: number
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagNode.order

**Поле.** Код: [web/admin/src/lib/dag.ts:10](../../../../../../web/admin/src/lib/dag.ts#L10).

```typescript
order: number
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagEdge

**Інтерфейс.** Код: [web/admin/src/lib/dag.ts:13](../../../../../../web/admin/src/lib/dag.ts#L13).

```typescript
interface DagEdge {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [from](lib.dag.md#adminlibdagdagedgefrom) | Поле | ні |
| [to](lib.dag.md#adminlibdagdagedgeto) | Поле | ні |
| [select](lib.dag.md#adminlibdagdagedgeselect) | Поле | ні |
| [conditional](lib.dag.md#adminlibdagdagedgeconditional) | Поле | ні |

## admin.lib.dag.DagEdge.from

**Поле.** Код: [web/admin/src/lib/dag.ts:14](../../../../../../web/admin/src/lib/dag.ts#L14).

```typescript
from: string
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagEdge.to

**Поле.** Код: [web/admin/src/lib/dag.ts:15](../../../../../../web/admin/src/lib/dag.ts#L15).

```typescript
to: string
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagEdge.select

**Поле.** Код: [web/admin/src/lib/dag.ts:16](../../../../../../web/admin/src/lib/dag.ts#L16).

```typescript
select: string
```

Доступ: читання — так; запис — так.

## admin.lib.dag.DagEdge.conditional

**Поле.** Код: [web/admin/src/lib/dag.ts:17](../../../../../../web/admin/src/lib/dag.ts#L17).

```typescript
conditional: boolean
```

Доступ: читання — так; запис — так.

## admin.lib.dag.Dag

**Інтерфейс.** Код: [web/admin/src/lib/dag.ts:20](../../../../../../web/admin/src/lib/dag.ts#L20).

```typescript
interface Dag {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [nodes](lib.dag.md#adminlibdagdagnodes) | Поле | ні |
| [edges](lib.dag.md#adminlibdagdagedges) | Поле | ні |
| [issues](lib.dag.md#adminlibdagdagissues) | Поле | ні |

## admin.lib.dag.Dag.nodes

**Поле.** Код: [web/admin/src/lib/dag.ts:21](../../../../../../web/admin/src/lib/dag.ts#L21).

```typescript
nodes: DagNode[]
```

Доступ: читання — так; запис — так.

## admin.lib.dag.Dag.edges

**Поле.** Код: [web/admin/src/lib/dag.ts:22](../../../../../../web/admin/src/lib/dag.ts#L22).

```typescript
edges: DagEdge[]
```

Доступ: читання — так; запис — так.

## admin.lib.dag.Dag.issues

**Поле.** Код: [web/admin/src/lib/dag.ts:24](../../../../../../web/admin/src/lib/dag.ts#L24).

```typescript
issues: string[]
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Human-readable structural problems (the orchestrator validation is authoritative).
```

## admin.lib.dag.stageLabel

**Функція.** Код: [web/admin/src/lib/dag.ts:27](../../../../../../web/admin/src/lib/dag.ts#L27).

```typescript
function stageLabel(stage: Stage): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `stage` | `{ stage_id: components["schemas"]["Slug"]; kind: "collect" \| "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" \| "fail_run"; }` | `—` | required |

Результат: `string`.

## admin.lib.dag.buildDag

**Функція.** Код: [web/admin/src/lib/dag.ts:33](../../../../../../web/admin/src/lib/dag.ts#L33).

```typescript
function buildDag(stages: readonly Stage[], options?: { requireCollect?: boolean; }): Dag
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `stages` | `readonly { stage_id: components["schemas"]["Slug"]; kind: "collect" \| "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" \| "fail_run"; }[]` | `—` | required |
| `options` | `{ requireCollect?: boolean; }` | `{}` | required |

Результат: `Dag`.
