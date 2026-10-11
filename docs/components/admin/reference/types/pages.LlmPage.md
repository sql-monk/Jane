# Модуль `pages.LlmPage`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/pages/LlmPage.tsx](../../../../../web/admin/src/pages/LlmPage.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `LlmPage`

```typescript
function LlmPage(): React.JSX.Element
```

Код: [LlmPage.tsx:43](../../../../../web/admin/src/pages/LlmPage.tsx#L43).

## Функції

### Функція `validProvider`

```typescript
function validProvider(value: unknown): value is { provider_id: string; kind: string; connection_id?: string; enabled: boolean; models: { model_id: string; max_context_tokens?: number; supports_structured_output?: boolean; pricing?: { input_per_mtok: number; output_per_mtok: number; currency: string; }; }[]; limits?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: { amount: number; currency: string; period: "total" | "run" | "day" | "week" | "month"; }; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; }
```

Код: [LlmPage.tsx:732](../../../../../web/admin/src/pages/LlmPage.tsx#L732).
