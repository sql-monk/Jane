# Модуль `lib.secrets`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/secrets.ts](../../../../../web/admin/src/lib/secrets.ts). Не редагуйте вручну.

## Функції

### Функція `isSecretRef`

```typescript
function isSecretRef(value: unknown): value is string
```

Код: [secrets.ts:28](../../../../../web/admin/src/lib/secrets.ts#L28).

### Функція `looksLikeSecretKey`

```typescript
function looksLikeSecretKey(key: string): boolean
```

Код: [secrets.ts:32](../../../../../web/admin/src/lib/secrets.ts#L32).

### Функція `looksLikeSecretValue`

```typescript
function looksLikeSecretValue(value: string): boolean
```

Values that look like credentials regardless of the key (bearer tokens, PEM keys, URLs with passwords).

Код: [secrets.ts:38](../../../../../web/admin/src/lib/secrets.ts#L38).

### Функція `redactSecrets`

```typescript
function redactSecrets<T>(value: T): T
```

Deep copy with secret-looking values masked:
 - under `secret_refs`: valid references are kept (they are not secrets), anything else is masked;
 - keys that name a secret (password, token, api_key, authorization...) are masked unless the value is a valid reference or a boolean resolution state (e.g. `secrets_resolved.password: true`);
 - string values that look like credentials are masked anywhere.

Код: [secrets.ts:57](../../../../../web/admin/src/lib/secrets.ts#L57).

### Функція `validateConnectionSecrets`

```typescript
function validateConnectionSecrets(params: Record<string, unknown>, secretRefs: Record<string, string>): string[]
```

Validation for the connection form: params must not carry secrets, secret_refs must be references.

Код: [secrets.ts:87](../../../../../web/admin/src/lib/secrets.ts#L87).

## Константи

### Константа `SECRET_MASK`

```typescript
const SECRET_MASK: "••••••"
```

Код: [secrets.ts:5](../../../../../web/admin/src/lib/secrets.ts#L5).

### Константа `SECRET_REF_PATTERN`

```typescript
const SECRET_REF_PATTERN: RegExp
```

contracts/schemas/common/connection.schema.json#/$defs/SecretRef

Код: [secrets.ts:8](../../../../../web/admin/src/lib/secrets.ts#L8).
