# lib/secrets

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.lib.secrets.SECRET_MASK](#adminlibsecretssecret_mask)
- [admin.lib.secrets.SECRET_REF_PATTERN](#adminlibsecretssecret_ref_pattern)
- [admin.lib.secrets.isSecretRef](#adminlibsecretsissecretref)
- [admin.lib.secrets.looksLikeSecretKey](#adminlibsecretslookslikesecretkey)
- [admin.lib.secrets.looksLikeSecretValue](#adminlibsecretslookslikesecretvalue)
- [admin.lib.secrets.redactSecrets](#adminlibsecretsredactsecrets)
- [admin.lib.secrets.validateConnectionSecrets](#adminlibsecretsvalidateconnectionsecrets)

## admin.lib.secrets.SECRET_MASK

**Константа.** Код: [web/admin/src/lib/secrets.ts:5](../../../../../../web/admin/src/lib/secrets.ts#L5).

```typescript
SECRET_MASK: "••••••" = "••••••"
```

Доступ: читання — так; запис — так.

## admin.lib.secrets.SECRET_REF_PATTERN

**Константа.** Код: [web/admin/src/lib/secrets.ts:8](../../../../../../web/admin/src/lib/secrets.ts#L8).

```typescript
SECRET_REF_PATTERN: RegExp = /^(env:[A-Z_][A-Z0-9_]{0,127}|file:.{1,512}|vault:[^#]{1,512}#[A-Za-z0-9_.-]{1,128})$/
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
contracts/schemas/common/connection.schema.json#/$defs/SecretRef
```

## admin.lib.secrets.isSecretRef

**Функція.** Код: [web/admin/src/lib/secrets.ts:28](../../../../../../web/admin/src/lib/secrets.ts#L28).

```typescript
function isSecretRef(value: unknown): value is string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `unknown` | `—` | required |

Результат: `boolean`.

## admin.lib.secrets.looksLikeSecretKey

**Функція.** Код: [web/admin/src/lib/secrets.ts:32](../../../../../../web/admin/src/lib/secrets.ts#L32).

```typescript
function looksLikeSecretKey(key: string): boolean
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `string` | `—` | required |

Результат: `boolean`.

## admin.lib.secrets.looksLikeSecretValue

**Функція.** Код: [web/admin/src/lib/secrets.ts:38](../../../../../../web/admin/src/lib/secrets.ts#L38).

```typescript
function looksLikeSecretValue(value: string): boolean
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `string` | `—` | required |

Результат: `boolean`.

### Опис із вихідного коду

```text
Values that look like credentials regardless of the key (bearer tokens, PEM keys, URLs with passwords).
```

## admin.lib.secrets.redactSecrets

**Функція.** Код: [web/admin/src/lib/secrets.ts:57](../../../../../../web/admin/src/lib/secrets.ts#L57).

```typescript
function redactSecrets<T>(value: T): T
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `T` | `—` | required |

Результат: `T`.

### Опис із вихідного коду

```text
Deep copy with secret-looking values masked:
 - under `secret_refs`: valid references are kept (they are not secrets), anything else is masked;
 - keys that name a secret (password, token, api_key, authorization...) are masked unless the value is a
   valid reference or a boolean resolution state (e.g. `secrets_resolved.password: true`);
 - string values that look like credentials are masked anywhere.
```

## admin.lib.secrets.validateConnectionSecrets

**Функція.** Код: [web/admin/src/lib/secrets.ts:87](../../../../../../web/admin/src/lib/secrets.ts#L87).

```typescript
function validateConnectionSecrets(params: Record<string, unknown>, secretRefs: Record<string, string>): string[]
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `params` | `Record<string, unknown>` | `—` | required |
| `secretRefs` | `Record<string, string>` | `—` | required |

Результат: `string[]`.

### Опис із вихідного коду

```text
Validation for the connection form: params must not carry secrets, secret_refs must be references.
```
