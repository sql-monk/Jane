# Модуль `lib.navigation`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/navigation.ts](../../../../../web/admin/src/lib/navigation.ts). Не редагуйте вручну.

## Функції

### Функція `navigationFor`

```typescript
function navigationFor(pathname: string): { to: string; label: string; icon: "overview" | "sources" | "tasks" | "runs" | "materials" | "results" | "problems" | "packages" | "assistant" | "connections" | "llm" | "limits" | "audit" | "search" | "arrow" | "refresh" | "moon" | "sun" | "menu" | "close" | "check" | "plus"; description: string; } | undefined
```

Код: [navigation.ts:104](../../../../../web/admin/src/lib/navigation.ts#L104).

## Константи

### Константа `NAV_GROUPS`

```typescript
const NAV_GROUPS: { label: string; items: { to: string; label: string; icon: "overview" | "sources" | "tasks" | "runs" | "materials" | "results" | "problems" | "packages" | "assistant" | "connections" | "llm" | "limits" | "audit" | "search" | "arrow" | "refresh" | "moon" | "sun" | "menu" | "close" | "check" | "plus"; description: string; }[]; }[]
```

Код: [navigation.ts:3](../../../../../web/admin/src/lib/navigation.ts#L3).
