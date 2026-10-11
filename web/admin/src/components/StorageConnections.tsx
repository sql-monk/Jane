import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { StorageConnection } from "../api/types";

export function storageName(connection: Pick<StorageConnection, "connection_id" | "kind" | "title">) {
  return connection.title ? `${connection.title} (${connection.connection_id})` : connection.connection_id;
}

export function useStorageConnections() {
  const api = useApi();
  return useCursorList(["storage-connections"], (cursor, limit) =>
    unwrap(
      api.storage.GET("/v1/connections", { params: { query: { limit, ...(cursor ? { cursor } : {}) } } }),
    ),
  );
}
