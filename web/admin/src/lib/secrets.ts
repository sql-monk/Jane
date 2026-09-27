// Secrets are never displayed (ТЗ §11, ADR-0006): the API carries only secret references (env:/file:/vault:)
// and their resolution state. As defence in depth the admin also masks anything that looks like a secret value
// before rendering, even if a service returned it by mistake.

export const SECRET_MASK = "••••••";

/** contracts/schemas/common/connection.schema.json#/$defs/SecretRef */
export const SECRET_REF_PATTERN =
  /^(env:[A-Z_][A-Z0-9_]{0,127}|file:.{1,512}|vault:[^#]{1,512}#[A-Za-z0-9_.-]{1,128})$/;

// Matched against snake_case segments, so `input_tokens` or `secrets_resolved` are not treated as secrets.
const SECRET_KEY =
  /(^|_)(pass|password|passwd|passphrase|pwd|secret|token|api_?key|apikey|private_?key|credentials?|authorization|cookie|session_?key|access_?key|secret_?key|client_?secret|dsn|connection_?string)($|_)/i;

/** Contract fields that match the pattern but are not secrets (robots.txt user-agent token). */
const NOT_SECRET_KEYS = new Set(["user_agent_token"]);

function normaliseKey(key: string): string {
  return key
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
    .replace(/[-\s.]/g, "_")
    .toLowerCase();
}

/** Keys whose values are secret references by contract (shown as is when they are valid references). */
const REF_CONTAINERS = new Set(["secret_refs"]);

export function isSecretRef(value: unknown): value is string {
  return typeof value === "string" && SECRET_REF_PATTERN.test(value);
}

export function looksLikeSecretKey(key: string): boolean {
  const normalised = normaliseKey(key);
  return !NOT_SECRET_KEYS.has(normalised) && SECRET_KEY.test(normalised);
}

/** Values that look like credentials regardless of the key (bearer tokens, PEM keys, URLs with passwords). */
export function looksLikeSecretValue(value: string): boolean {
  return (
    /-----BEGIN [A-Z ]*PRIVATE KEY-----/.test(value) ||
    /^Bearer\s+\S{8,}/i.test(value) ||
    /^[a-z][a-z0-9+.-]*:\/\/[^/\s:@]+:[^/\s@]+@/i.test(value) ||
    /\b(AKIA|ASIA)[A-Z0-9]{16}\b/.test(value) ||
    /\b(sk|pk|rk)-[A-Za-z0-9_-]{16,}\b/.test(value) ||
    /\bgh[pousr]_[A-Za-z0-9]{20,}\b/.test(value) ||
    /\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b/.test(value)
  );
}

/**
 * Deep copy with secret-looking values masked:
 *  - under `secret_refs`: valid references are kept (they are not secrets), anything else is masked;
 *  - keys that name a secret (password, token, api_key, authorization...) are masked unless the value is a
 *    valid reference or a boolean resolution state (e.g. `secrets_resolved.password: true`);
 *  - string values that look like credentials are masked anywhere.
 */
export function redactSecrets<T>(value: T): T {
  return redact(value, false, false) as T;
}

function redact(value: unknown, secretKey: boolean, refContainer: boolean): unknown {
  if (Array.isArray(value)) return value.map((item) => redact(item, secretKey, refContainer));
  if (value !== null && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, item] of Object.entries(value as Record<string, unknown>)) {
      if (REF_CONTAINERS.has(key)) {
        out[key] = redact(item, true, true);
      } else if (refContainer) {
        out[key] = redact(item, true, true);
      } else {
        out[key] = redact(item, secretKey || looksLikeSecretKey(key), false);
      }
    }
    return out;
  }
  if (typeof value === "string") {
    if (refContainer) return isSecretRef(value) ? value : SECRET_MASK;
    if (secretKey && !isSecretRef(value)) return SECRET_MASK;
    if (looksLikeSecretValue(value)) return SECRET_MASK;
    return value;
  }
  if (typeof value === "number" && secretKey && !refContainer) return SECRET_MASK;
  return value;
}

/** Validation for the connection form: params must not carry secrets, secret_refs must be references. */
export function validateConnectionSecrets(
  params: Record<string, unknown>,
  secretRefs: Record<string, string>,
): string[] {
  const errors: string[] = [];
  for (const [key, value] of Object.entries(params)) {
    if (looksLikeSecretKey(key)) errors.push(`params.${key}: секрети задаються лише через secret_refs`);
    else if (typeof value === "string" && looksLikeSecretValue(value))
      errors.push(`params.${key}: значення схоже на секрет`);
  }
  for (const [name, ref] of Object.entries(secretRefs)) {
    if (!/^[a-z][a-z0-9_]{0,63}$/.test(name)) errors.push(`secret_refs.${name}: ім'я — [a-z][a-z0-9_]*`);
    if (!isSecretRef(ref))
      errors.push(`secret_refs.${name}: очікується посилання env:, file: або vault: (не значення)`);
  }
  return errors;
}
