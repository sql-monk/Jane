# Модуль `lib.modules`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/modules.ts](../../../../../web/admin/src/lib/modules.ts). Не редагуйте вручну.

## Функції

### Функція `modules`

```typescript
function modules(config: import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/config").AdminConfig): import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/lib/modules").ModuleDefinition[]
```

Код: [modules.ts:15](../../../../../web/admin/src/lib/modules.ts#L15).

### Функція `fieldLabel`

```typescript
function fieldLabel(path: string): string
```

Код: [modules.ts:290](../../../../../web/admin/src/lib/modules.ts#L290).

### Функція `fieldGroup`

```typescript
function fieldGroup(path: string): string
```

Код: [modules.ts:301](../../../../../web/admin/src/lib/modules.ts#L301).

### Функція `fieldHelp`

```typescript
function fieldHelp(path: string): string | undefined
```

Код: [modules.ts:313](../../../../../web/admin/src/lib/modules.ts#L313).

## Типи

### Тип `ModuleConfiguration`

```typescript
type ModuleConfiguration = components["schemas"]["module-configuration.schema"];
```

Код: [modules.ts:4](../../../../../web/admin/src/lib/modules.ts#L4).

### Тип `ModuleField`

```typescript
type ModuleField = ModuleConfiguration["fields"][number];
```

Код: [modules.ts:5](../../../../../web/admin/src/lib/modules.ts#L5).

### Тип `ModuleTelemetry`

```typescript
type ModuleTelemetry = components["schemas"]["module-telemetry.schema"];
```

Код: [modules.ts:6](../../../../../web/admin/src/lib/modules.ts#L6).

### Тип `ModuleDefinition`

```typescript
type ModuleDefinition = {
  id: string;
  name: string;
  executor: string;
  description: string;
  links: { label: string; to: string }[];
};
```

Код: [modules.ts:7](../../../../../web/admin/src/lib/modules.ts#L7).
