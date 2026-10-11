# Модуль `lib.pickers`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/pickers.ts](../../../../../web/admin/src/lib/pickers.ts). Не редагуйте вручну.

## Функції

### Функція `useSourceOptions`

```typescript
function useSourceOptions(): { options: { value: string; label: string; description: string; }[]; items: { source_id: string; kind: string; title: string; description?: string; locator: { url?: string; telegram_username?: string; telegram_channel_id?: string; }; collector_rules?: { package_id: string; version: string; digest?: string; }; limits?: { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: { amount: number; currency: string; period: "total" | "run" | "day" | "week" | "month"; }; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; forward_unknown_to_llm?: boolean; expected_entity_types?: string[]; change_policy?: { llm_versions?: "manual_approval" | "auto_after_checks" | "forbidden"; }; connections?: { [x: string]: string; }; labels?: { [x: string]: string; }; readonly created_at?: string; readonly updated_at?: string; }[]; isLoading: boolean; error: Error | null; hasMore: boolean; loadMore: () => undefined; loadingMore: boolean; refetch: () => undefined; }
```

Код: [pickers.ts:5](../../../../../web/admin/src/lib/pickers.ts#L5).

### Функція `useTaskOptions`

```typescript
function useTaskOptions(sourceId?: string | undefined): { options: { value: string; label: string; description: string; }[]; items: { task_id: string; title: string; source_id: string; enabled: boolean; schedule?: { type: "manual" | "once" | "cron" | "interval"; at?: string; cron?: string; interval_seconds?: number; timezone?: string; start_at?: string; end_at?: string; enabled?: boolean; overlap?: "skip" | "queue" | "allow"; }; next_run_at?: string; package_stages?: { stage_id: string; package: { package_id: string; version: string; digest?: string; }; }[]; last_run?: { run_id?: string; status?: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; finished_at?: string; }; }[]; isLoading: boolean; error: Error | null; hasMore: boolean; loadMore: () => undefined; loadingMore: boolean; refetch: () => undefined; }
```

Код: [pickers.ts:22](../../../../../web/admin/src/lib/pickers.ts#L22).
