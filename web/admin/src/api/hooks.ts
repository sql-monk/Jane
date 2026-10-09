import { useInfiniteQuery, useQuery, type QueryKey } from "@tanstack/react-query";
import type { Client } from "openapi-fetch";
import { useConfig } from "../app/context";
import { unwrap } from "./client";
import type { Job } from "./types";

export const TERMINAL_JOB_STATUSES = new Set(["succeeded", "failed", "cancelled"]);

/** Delay before the n-th poll: initial * multiplier^n, capped (config.polling). */
export function pollDelay(
  attempt: number,
  polling: { initial_ms: number; max_ms: number; multiplier: number },
): number {
  return Math.min(polling.max_ms, Math.round(polling.initial_ms * Math.pow(polling.multiplier, attempt)));
}

interface Page<T> {
  items: T[];
  next_cursor?: string | null;
}

/**
 * Cursor pagination (`?limit=&cursor=` -> `{items, next_cursor}`), page size from config. `refetchWhile` - poll the
 * loaded pages with the job backoff (config.polling) while it holds for the items, e.g. while a listed job runs.
 */
export function useCursorList<T>(
  key: QueryKey,
  fetchPage: (cursor: string | undefined, limit: number) => Promise<Page<T>>,
  refetchWhile?: (items: T[]) => boolean,
) {
  const { page_size, polling } = useConfig();
  const query = useInfiniteQuery({
    queryKey: [...key, page_size],
    initialPageParam: undefined as string | undefined,
    queryFn: ({ pageParam }) => fetchPage(pageParam, page_size),
    getNextPageParam: (last) => last.next_cursor ?? undefined,
    refetchInterval: (q) => {
      const items = q.state.data?.pages.flatMap((p) => p.items) ?? [];
      return refetchWhile && !q.state.error && refetchWhile(items)
        ? pollDelay(q.state.dataUpdateCount, polling)
        : false;
    },
  });
  const items = query.data?.pages.flatMap((p) => p.items) ?? [];
  return {
    items,
    isLoading: query.isLoading,
    error: query.error,
    hasMore: Boolean(query.hasNextPage),
    loadMore: () => void query.fetchNextPage(),
    loadingMore: query.isFetchingNextPage,
    refetch: () => void query.refetch(),
  };
}

// Every Jane API mounts the same Job path items (common.yaml#/components/pathItems/Job).
interface JobPaths {
  "/v1/jobs/{job_id}": {
    parameters: { query?: never; header?: never; path?: never; cookie?: never };
    get: {
      parameters: { query?: never; header?: never; path: { job_id: string }; cookie?: never };
      requestBody?: never;
      responses: { 200: { headers: { [name: string]: unknown }; content: { "application/json": Job } } };
    };
  };
}

/** Polls a job with backoff until it reaches a terminal state. */
export function useJob(
  service: string,
  client: Client<JobPaths> | Client<never>,
  jobId: string | null | undefined,
) {
  const { polling } = useConfig();
  const typed = client as Client<JobPaths>;
  return useQuery({
    queryKey: ["job", service, jobId],
    enabled: Boolean(jobId),
    queryFn: () => unwrap(typed.GET("/v1/jobs/{job_id}", { params: { path: { job_id: jobId as string } } })),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data && TERMINAL_JOB_STATUSES.has(data.status)) return false;
      if (query.state.error) return false;
      return pollDelay(query.state.dataUpdateCount, polling);
    },
  });
}
