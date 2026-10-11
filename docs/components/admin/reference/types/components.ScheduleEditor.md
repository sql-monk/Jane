# Модуль `components.ScheduleEditor`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/ScheduleEditor.tsx](../../../../../web/admin/src/components/ScheduleEditor.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `ScheduleEditor`

```typescript
function ScheduleEditor({ value, onChange, issues, }: { value: { type: "manual" | "once" | "cron" | "interval"; at?: string; cron?: string; interval_seconds?: number; timezone?: string; start_at?: string; end_at?: string; enabled?: boolean; overlap?: "skip" | "queue" | "allow"; } | undefined; onChange: (s: { type: "manual" | "once" | "cron" | "interval"; at?: string; cron?: string; interval_seconds?: number; timezone?: string; start_at?: string; end_at?: string; enabled?: boolean; overlap?: "skip" | "queue" | "allow"; } | undefined) => void; issues?: import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/lib/schema").SchemaIssue[]; }): React.JSX.Element
```

Editor of TaskConfig.schedule (manual | once | cron | interval), fields from task-config.schema.json.

Код: [ScheduleEditor.tsx:6](../../../../../web/admin/src/components/ScheduleEditor.tsx#L6).
