# components/ConnectionPicker

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.ConnectionPicker.ConnectionPicker](#admincomponentsconnectionpickerconnectionpicker)

## admin.components.ConnectionPicker.ConnectionPicker

**Функція.** Код: [web/admin/src/components/ConnectionPicker.tsx:7](../../../../../../web/admin/src/components/ConnectionPicker.tsx#L7).

```typescript
function ConnectionPicker({ label, value, onChange, }: { label: string; value: string; onChange: (value: string) => void; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ label: string; value: string; onChange: (value: string) => void; }` | `—` | required |

Результат: `JSX.Element`.

### Опис із вихідного коду

```text
Picks a platform connection (orchestrator registry) by id; free text is allowed as well.
```
