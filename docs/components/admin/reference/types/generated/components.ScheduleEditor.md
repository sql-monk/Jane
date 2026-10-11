# components/ScheduleEditor

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.ScheduleEditor.ScheduleEditor](#admincomponentsscheduleeditorscheduleeditor)

## admin.components.ScheduleEditor.ScheduleEditor

**Функція.** Код: [web/admin/src/components/ScheduleEditor.tsx:5](../../../../../../web/admin/src/components/ScheduleEditor.tsx#L5).

```typescript
function ScheduleEditor({ value, onChange, }: { value: Schedule | undefined; onChange: (s: Schedule | undefined) => void; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ value: Schedule \| undefined; onChange: (s: Schedule \| undefined) => void; }` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
Editor of TaskConfig.schedule (manual | once | cron | interval), fields from task-config.schema.json.
```
