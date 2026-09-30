import { useEffect, useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../app/context";
import { ErrorBox } from "../components/ui";

export function LoginPage() {
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [key, setKey] = useState("");
  const [error, setError] = useState<unknown>(null);
  const from = (location.state as { from?: string } | null)?.from ?? "/";

  if (auth.authenticated && !auth.expired) return <Navigate to={from} replace />;

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!key.trim()) return;
    auth.loginWithApiKey(key.trim());
    setKey("");
    navigate(from, { replace: true });
  }

  return (
    <main className="login">
      <h1>Jane — адмінка</h1>
      {auth.mode === "api_key" ? (
        <form onSubmit={submit} autoComplete="off" aria-label="Вхід за ключем API">
          <p className="muted">
            Режим розробки (<code>auth.mode = api_key</code>): ключ адміністратора зберігається лише в
            sessionStorage цієї вкладки й передається як <code>Authorization: Bearer</code>.
          </p>
          <label className="field">
            <span className="field-label">Ключ API</span>
            <input
              type="password"
              name="api-key"
              autoComplete="off"
              spellCheck={false}
              value={key}
              onChange={(e) => setKey(e.target.value)}
            />
          </label>
          <button type="submit" className="btn btn-primary" disabled={!key.trim()}>
            Увійти
          </button>
        </form>
      ) : null}
      {auth.mode === "oidc" ? (
        <div>
          <p className="muted">Вхід через постачальника ідентичності (OIDC Authorization Code + PKCE).</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => auth.loginWithOidc().catch((e: unknown) => setError(e))}
          >
            Увійти через IdP
          </button>
        </div>
      ) : null}
      <ErrorBox error={error} />
    </main>
  );
}

export function OidcCallbackPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<unknown>(null);
  useEffect(() => {
    auth
      .completeOidcLogin()
      .then(() => navigate("/", { replace: true }))
      .catch((e: unknown) => setError(e));
    // Run once on mount: the callback URL carries a one-time code.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <main className="login">
      <p>Завершення входу…</p>
      <ErrorBox error={error} />
    </main>
  );
}
