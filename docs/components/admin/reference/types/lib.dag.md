# Модуль `lib.dag`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/dag.ts](../../../../../web/admin/src/lib/dag.ts). Не редагуйте вручну.

## Функції

### Функція `stageLabel`

```typescript
function stageLabel(stage: { stage_id: string; kind: "handler" | "collect"; title?: string; collector?: { collector: string; rules?: { package_id: string; version: string; digest?: string; }; mode?: "full" | "incremental"; }; handler?: { package_id: string; version: string; digest?: string; }; params?: Record<string, unknown>; connections?: { [key: string]: string; }; inputs?: { from: string; select?: "problems" | "output" | "input_material" | "unmatched_materials"; when?: { all: (any | { any: (any | any | { not: any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { not: any | { any: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { any: ({ all: (any | any | { not: any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { not: { all: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { not: { all: (any | { any: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { any: ({ all: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; }[]; bindings?: { source_ids?: string[]; sections?: string[]; url_patterns?: { type?: "glob" | "regex"; value: string; }[]; media_types?: string[]; content_kinds?: string[]; }[]; limits?: { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: { amount: number; currency: string; period: "total" | "run" | "day" | "week" | "month"; }; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; retries?: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; on_failure?: "continue" | "fail_run"; }): string
```

Код: [dag.ts:27](../../../../../web/admin/src/lib/dag.ts#L27).

### Функція `buildDag`

```typescript
function buildDag(stages: readonly { stage_id: string; kind: "handler" | "collect"; title?: string; collector?: { collector: string; rules?: { package_id: string; version: string; digest?: string; }; mode?: "full" | "incremental"; }; handler?: { package_id: string; version: string; digest?: string; }; params?: Record<string, unknown>; connections?: { [key: string]: string; }; inputs?: { from: string; select?: "problems" | "output" | "input_material" | "unmatched_materials"; when?: { all: (any | { any: (any | any | { not: any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { not: any | { any: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { any: ({ all: (any | any | { not: any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { not: { all: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { not: { all: (any | { any: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | { any: ({ all: (any | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; })[]; } | any | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; } | { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; }[]; bindings?: { source_ids?: string[]; sections?: string[]; url_patterns?: { type?: "glob" | "regex"; value: string; }[]; media_types?: string[]; content_kinds?: string[]; }[]; limits?: { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: { amount: number; currency: string; period: "total" | "run" | "day" | "week" | "month"; }; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; retries?: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; on_failure?: "continue" | "fail_run"; }[]): import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/lib/dag").Dag
```

Код: [dag.ts:33](../../../../../web/admin/src/lib/dag.ts#L33).

## Інтерфейси

### Інтерфейс `DagNode`

```typescript
interface DagNode
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `id` | `string` | так | читання й запис |  |
| `kind` | `"handler" \| "collect"` | так | читання й запис |  |
| `title` | `string` | так | читання й запис |  |
| `label` | `string` | так | читання й запис |  |
| `layer` | `number` | так | читання й запис |  |
| `order` | `number` | так | читання й запис |  |

Код: [dag.ts:4](../../../../../web/admin/src/lib/dag.ts#L4).

### Інтерфейс `DagEdge`

```typescript
interface DagEdge
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `from` | `string` | так | читання й запис |  |
| `to` | `string` | так | читання й запис |  |
| `select` | `string` | так | читання й запис |  |
| `conditional` | `boolean` | так | читання й запис |  |

Код: [dag.ts:13](../../../../../web/admin/src/lib/dag.ts#L13).

### Інтерфейс `Dag`

```typescript
interface Dag
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `nodes` | `DagNode[]` | так | читання й запис |  |
| `edges` | `DagEdge[]` | так | читання й запис |  |
| `issues` | `string[]` | так | читання й запис | Human-readable structural problems (the orchestrator validation is authoritative). |

Код: [dag.ts:20](../../../../../web/admin/src/lib/dag.ts#L20).
