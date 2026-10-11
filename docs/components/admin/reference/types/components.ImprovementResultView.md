# Модуль `components.ImprovementResultView`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/ImprovementResultView.tsx](../../../../../web/admin/src/components/ImprovementResultView.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `ImprovementResultView`

```typescript
function ImprovementResultView({ result }: { result: Record<string, unknown>; }): React.JSX.Element
```

Job.result of assistant startImprovement (assistant.v1 ImprovementResult).

Код: [ImprovementResultView.tsx:9](../../../../../web/admin/src/components/ImprovementResultView.tsx#L9).

### Компонент `ProposalView`

```typescript
function ProposalView({ proposal }: { proposal: { based_on: { package_id: string; version: string; digest?: string; }; version: string; schema_change?: "none" | "additive" | "breaking"; change_summary?: string; manifest: { schema_version: "1"; package_id: string; version: string; kind: "llm" | "storage" | "extractor" | "transform" | "collector-rules"; title: string; description?: string; tags?: string[]; entry: { runtime: "python"; module: string; callable: string; } | { executor: "storage"; adapter: string; writes: "data" | "raw" | "entities" | "raw_and_entities"; format?: { raw?: "json" | "original" | "html"; entities?: "json" | "jsonl"; }; history?: boolean; } | { executor: "llm"; instructions: string; input_template?: string; output_schema: string; model?: string; temperature?: number; max_output_tokens?: number; } | { collector: string; rules: string; } | { executor: string; operation?: string; }; input?: { accepts?: ("data" | "entities" | "material")[]; media_types?: string[]; content_kinds?: string[]; entity_types?: string[]; data_schema?: string; }; params_schema?: string; output?: { entities?: { entity_type: string; schema: string; key_fields: string[]; description?: string; }[]; data_schema?: string; }; dependencies?: { runtime_profile?: string; python?: string[]; packages?: { package_id: string; version: string; digest?: string; }[]; }; required_connections?: { name: string; kind: string; purpose?: string; optional?: boolean; }[]; access?: { network?: "none" | "allowlist"; hosts?: string[]; }; tests?: { name: string; input: { material?: string; file?: string; media_type?: string; url?: string; entities?: string; data?: string; }; params?: Record<string, unknown>; expected_status: "success" | "failed" | "empty" | "unrecognized"; expected?: string; compare?: "exact" | "subset"; origin?: "llm" | "human" | "problem_sample"; }[]; provenance: { created_by: "llm" | "human" | "import"; authors?: string[]; created_at?: string; based_on?: { package_id: string; version: string; digest?: string; }; change_summary?: string; llm?: { provider?: string; model?: string; assistant_job_id?: string; reason?: "onboarding" | "improvement" | "unknown_material" | "upstream_port"; }; upstream_port?: { parent_version: string; requested_by?: string; }; }; fork_of?: { package_id: string; version: string; digest?: string; }; bindings_hint?: { source_kinds?: string[]; domains?: string[]; url_patterns?: string[]; }; }; files: { [key: string]: { encoding: "utf-8" | "base64"; data: string; }; }; omitted_files?: string[]; diff?: string; }; }): React.JSX.Element
```

`ImprovementResult.proposal` (outcome `proposal_only`): the package forbids automatic changes, the candidate passed its tests but is not published. The user reviews the changed files, the manifest and the diff, and publishes the version himself (registry publishPackageVersion with `based_on` + `files`). File contents are data: shown as text.

Код: [ImprovementResultView.tsx:83](../../../../../web/admin/src/components/ImprovementResultView.tsx#L83).
