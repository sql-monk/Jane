# auth/oidc

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.auth.oidc.createUserManager](#adminauthoidccreateusermanager)

## admin.auth.oidc.createUserManager

**Функція.** Код: [web/admin/src/auth/oidc.ts:7](../../../../../../web/admin/src/auth/oidc.ts#L7).

```typescript
function createUserManager(config: OidcConfig, origin?: string): UserManager
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `config` | `{ mode: "oidc"; authority: string; client_id: string; scope: string; redirect_path: string; post_logout_redirect_path: string; }` | `—` | required |
| `origin` | `string` | `window.location.origin` | required |

Результат: `UserManager`.
