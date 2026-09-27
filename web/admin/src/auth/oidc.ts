// OIDC Authorization Code + PKCE against an external IdP (ADR-0005 §4). Tokens stay in sessionStorage.
import { UserManager, WebStorageStateStore } from "oidc-client-ts";
import type { AuthConfig } from "../config";

type OidcConfig = Extract<AuthConfig, { mode: "oidc" }>;

export function createUserManager(config: OidcConfig, origin: string = window.location.origin): UserManager {
  return new UserManager({
    authority: config.authority,
    client_id: config.client_id,
    redirect_uri: origin + config.redirect_path,
    post_logout_redirect_uri: origin + config.post_logout_redirect_path,
    response_type: "code", // PKCE is always used by oidc-client-ts for the code flow
    scope: config.scope,
    userStore: new WebStorageStateStore({ store: window.sessionStorage }),
    stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
    automaticSilentRenew: true,
    loadUserInfo: true,
  });
}
