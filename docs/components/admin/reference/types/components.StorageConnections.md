# Модуль `components.StorageConnections`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/StorageConnections.tsx](../../../../../web/admin/src/components/StorageConnections.tsx). Не редагуйте вручну.

## Функції

### Функція `storageName`

```typescript
function storageName(connection: Pick<{ connection_id: string; kind: string; title?: string; params?: { [key: string]: string | number | boolean | Record<string, unknown> | unknown[]; }; secret_refs?: { [key: string]: string; }; labels?: { [key: string]: string; }; }, "kind" | "title" | "connection_id">): string
```

Код: [StorageConnections.tsx:6](../../../../../web/admin/src/components/StorageConnections.tsx#L6).

### Функція `useStorageConnections`

```typescript
function useStorageConnections(): { items: { connection_id: string; kind: string; title?: string; params?: { [x: string]: string | number | boolean | { [x: string]: unknown; } | unknown[]; }; secret_refs?: { [x: string]: string; }; labels?: { [x: string]: string; }; }[]; isLoading: boolean; error: Error | null; hasMore: boolean; loadMore: () => undefined; loadingMore: boolean; refetch: () => undefined; }
```

Код: [StorageConnections.tsx:10](../../../../../web/admin/src/components/StorageConnections.tsx#L10).
