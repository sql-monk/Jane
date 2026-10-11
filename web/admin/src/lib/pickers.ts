import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";

export function useSourceOptions() {
  const api = useApi();
  const list = useCursorList(["source-options"], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/sources", { params: { query: { limit, ...(cursor ? { cursor } : {}) } } }),
    ),
  );
  return {
    ...list,
    options: list.items.map((source) => ({
      value: source.source_id,
      label: source.title || source.source_id,
      description: source.source_id,
    })),
  };
}

export function useTaskOptions(sourceId?: string) {
  const api = useApi();
  const list = useCursorList(["task-options", sourceId], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/tasks", {
        params: {
          query: { limit, ...(cursor ? { cursor } : {}), ...(sourceId ? { source_id: sourceId } : {}) },
        },
      }),
    ),
  );
  return {
    ...list,
    options: list.items.map((task) => ({
      value: task.task_id,
      label: task.title || task.task_id,
      description: task.task_id,
    })),
  };
}
