# Модуль `components.ModuleSettingsForm`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/ModuleSettingsForm.tsx](../../../../../web/admin/src/components/ModuleSettingsForm.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `ModuleSettingsForm`

```typescript
function ModuleSettingsForm({ configuration, save, pending, error, }: { configuration: { service: string; instance_id: string; revision: number; updated_at?: string | null; fields: { path: string; value: string | number | boolean; configured_value?: string | number | boolean; type: "string" | "number" | "boolean"; integer?: boolean; description?: string; requires_restart: boolean; origin: string; minimum?: number; maximum?: number; exclusive_minimum?: number; choices?: (string | number | boolean)[]; inherited_value?: string | number | boolean; }[]; overrides: { [key: string]: string | number | boolean; }; pending_restart: boolean; }; save: (values: { [key: string]: string | number | boolean; }) => void; pending: boolean; error: unknown; }): React.JSX.Element
```

Код: [ModuleSettingsForm.tsx:85](../../../../../web/admin/src/components/ModuleSettingsForm.tsx#L85).
