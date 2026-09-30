import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type { UserManager } from "oidc-client-ts";
import type { AdminConfig } from "../config";
import { createApiClients, type ApiClients } from "../api/client";
import { clearApiKey, readApiKey, writeApiKey } from "../auth/session";
import { createUserManager } from "../auth/oidc";

export interface AuthState {
  mode: AdminConfig["auth"]["mode"];
  authenticated: boolean;
  /** A request was rejected with 401: the key/token is wrong or expired. */
  expired: boolean;
  /** Who is signed in (OIDC profile name/email); never the key itself. */
  principal: string | null;
  loginWithApiKey: (key: string) => void;
  loginWithOidc: () => Promise<void>;
  completeOidcLogin: () => Promise<void>;
  logout: () => void;
}

interface AppContextValue {
  config: AdminConfig;
  api: ApiClients;
  auth: AuthState;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ config, children }: { config: AdminConfig; children: ReactNode }) {
  const [apiKey, setApiKey] = useState<string | null>(() =>
    config.auth.mode === "api_key" ? readApiKey() : null,
  );
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [principal, setPrincipal] = useState<string | null>(null);
  const [expired, setExpired] = useState(false);
  const tokenRef = useRef<string | null>(null);
  tokenRef.current =
    config.auth.mode === "api_key" ? apiKey : config.auth.mode === "oidc" ? accessToken : null;

  const userManager = useMemo<UserManager | null>(
    () => (config.auth.mode === "oidc" ? createUserManager(config.auth) : null),
    [config.auth],
  );

  useEffect(() => {
    if (!userManager) return;
    let active = true;
    const apply = (user: Awaited<ReturnType<UserManager["getUser"]>>) => {
      if (!active) return;
      setAccessToken(user && !user.expired ? user.access_token : null);
      setPrincipal(user ? String(user.profile.email ?? user.profile.name ?? user.profile.sub) : null);
    };
    void userManager.getUser().then(apply);
    userManager.events.addUserLoaded(apply);
    userManager.events.addUserUnloaded(() => apply(null));
    return () => {
      active = false;
    };
  }, [userManager]);

  const api = useMemo(
    () =>
      createApiClients(config, {
        getToken: () => tokenRef.current,
        onUnauthenticated: () => setExpired(true),
      }),
    [config],
  );

  const loginWithApiKey = useCallback((key: string) => {
    writeApiKey(key);
    setApiKey(key);
    setExpired(false);
  }, []);

  const loginWithOidc = useCallback(async () => {
    if (!userManager) throw new Error("OIDC is not configured");
    await userManager.signinRedirect();
  }, [userManager]);

  const completeOidcLogin = useCallback(async () => {
    if (!userManager) throw new Error("OIDC is not configured");
    const user = await userManager.signinRedirectCallback();
    setAccessToken(user.access_token);
    setExpired(false);
  }, [userManager]);

  const logout = useCallback(() => {
    clearApiKey();
    setApiKey(null);
    setAccessToken(null);
    setExpired(false);
    if (userManager) void userManager.signoutRedirect();
  }, [userManager]);

  const auth: AuthState = {
    mode: config.auth.mode,
    authenticated: config.auth.mode === "none" || Boolean(tokenRef.current),
    expired,
    principal: config.auth.mode === "api_key" ? (apiKey ? "API key" : null) : principal,
    loginWithApiKey,
    loginWithOidc,
    completeOidcLogin,
    logout,
  };

  return <AppContext.Provider value={{ config, api, auth }}>{children}</AppContext.Provider>;
}

function useApp(): AppContextValue {
  const value = useContext(AppContext);
  if (!value) throw new Error("AppProvider is missing");
  return value;
}

export const useApi = (): ApiClients => useApp().api;
export const useConfig = (): AdminConfig => useApp().config;
export const useAuth = (): AuthState => useApp().auth;
