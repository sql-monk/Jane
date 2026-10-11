# components/UnifiedDiff

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.UnifiedDiff.UnifiedDiff](#admincomponentsunifieddiffunifieddiff)

## admin.components.UnifiedDiff.UnifiedDiff

**Функція.** Код: [web/admin/src/components/UnifiedDiff.tsx:2](../../../../../../web/admin/src/components/UnifiedDiff.tsx#L2).

```typescript
function UnifiedDiff({ diff, label }: { diff: string; label: string; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ diff: string; label: string; }` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
Renders a unified diff (from registry diffPackage or computed locally) with added/removed line colouring.
```
