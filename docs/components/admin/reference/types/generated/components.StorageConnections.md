# components/StorageConnections

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.StorageConnections.storageName](#admincomponentsstorageconnectionsstoragename)
- [admin.components.StorageConnections.useStorageConnections](#admincomponentsstorageconnectionsusestorageconnections)

## admin.components.StorageConnections.storageName

**Функція.** Код: [web/admin/src/components/StorageConnections.tsx:6](../../../../../../web/admin/src/components/StorageConnections.tsx#L6).

```typescript
function storageName(connection: Pick<StorageConnection, "connection_id" | "kind" | "title">): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `connection` | `Pick<{ connection_id: components["schemas"]["Slug"]; kind: components["schemas"]["ConnectionKind"]; title?: string; params?: { [key: string]: string \| number \| boolean \| unknown[] \| Record<string, unknown>; }; secret_refs?: { [key: string]: components["schemas"]["SecretRef"]; }; labels?: components["schemas"]["Labels"]; }, "connection_id" \| "kind" \| "title">` | `—` | required |

Результат: `string`.

## admin.components.StorageConnections.useStorageConnections

**Функція.** Код: [web/admin/src/components/StorageConnections.tsx:10](../../../../../../web/admin/src/components/StorageConnections.tsx#L10).

```typescript
function useStorageConnections(): { items: any; isLoading: any; error: any; hasMore: boolean; loadMore: () => undefined; loadingMore: any; refetch: () => undefined; }
```

Результат: `{ items: any; isLoading: any; error: any; hasMore: boolean; loadMore: () => undefined; loadingMore: any; refetch: () => undefined; }`.
