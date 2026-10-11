# auth/session

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.auth.session.readApiKey](#adminauthsessionreadapikey)
- [admin.auth.session.writeApiKey](#adminauthsessionwriteapikey)
- [admin.auth.session.clearApiKey](#adminauthsessionclearapikey)

## admin.auth.session.readApiKey

**Функція.** Код: [web/admin/src/auth/session.ts:12](../../../../../../web/admin/src/auth/session.ts#L12).

```typescript
function readApiKey(): string | null
```

Результат: `string | null`.

## admin.auth.session.writeApiKey

**Функція.** Код: [web/admin/src/auth/session.ts:16](../../../../../../web/admin/src/auth/session.ts#L16).

```typescript
function writeApiKey(key: string): void
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `string` | `—` | required |

Результат: `void`.

## admin.auth.session.clearApiKey

**Функція.** Код: [web/admin/src/auth/session.ts:20](../../../../../../web/admin/src/auth/session.ts#L20).

```typescript
function clearApiKey(): void
```

Результат: `void`.
