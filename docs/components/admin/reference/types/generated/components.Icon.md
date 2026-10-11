# components/Icon

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.Icon.IconName](#admincomponentsiconiconname)
- [admin.components.Icon.Icon](#admincomponentsiconicon)

## admin.components.Icon.IconName

**Тип.** Код: [web/admin/src/components/Icon.tsx:27](../../../../../../web/admin/src/components/Icon.tsx#L27).

```typescript
export type IconName = keyof typeof paths;
```

## admin.components.Icon.Icon

**Функція.** Код: [web/admin/src/components/Icon.tsx:29](../../../../../../web/admin/src/components/Icon.tsx#L29).

```typescript
function Icon({ name, size }: { name: IconName; size?: number; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ name: IconName; size?: number; }` | `—` | required |

Результат: `any`.
