import { describe, expect, it } from "vitest";
import {
  SECRET_MASK,
  isSecretRef,
  looksLikeSecretKey,
  redactSecrets,
  validateConnectionSecrets,
} from "./secrets";
import { openapiExample } from "../test/contracts";

describe("redactSecrets", () => {
  it("keeps valid secret references and masks anything else under secret_refs", () => {
    const out = redactSecrets({
      connection: {
        connection_id: "results-pg",
        params: { host: "postgres", port: 5432 },
        secret_refs: {
          password: "env:RESULTS_PG_PASSWORD",
          token: "raw-token-value-123",
          key: "vault:kv/jane#key",
        },
      },
    });
    expect(out.connection.secret_refs).toEqual({
      password: "env:RESULTS_PG_PASSWORD",
      token: SECRET_MASK,
      key: "vault:kv/jane#key",
    });
    expect(out.connection.params).toEqual({ host: "postgres", port: 5432 });
  });

  it("masks values of secret-named keys, but not counters or resolution flags", () => {
    const out = redactSecrets({
      params: {
        password: "hunter2",
        api_key: "k-123",
        Authorization: "Basic abc",
        user_agent_token: "JaneBot",
      },
      usage: { input_tokens: 240112, max_output_tokens_per_request: 1000 },
      secrets_resolved: { password: true, username: false },
    });
    expect(out.params).toEqual({
      password: SECRET_MASK,
      api_key: SECRET_MASK,
      Authorization: SECRET_MASK,
      user_agent_token: "JaneBot",
    });
    expect(out.usage).toEqual({ input_tokens: 240112, max_output_tokens_per_request: 1000 });
    expect(out.secrets_resolved).toEqual({ password: true, username: false });
  });

  it("masks credential-looking strings under any key", () => {
    const out = redactSecrets({
      note: "Bearer abcdefghijklmnop",
      dsnish: "postgres://jane:s3cret@db:5432/x",
      aws: ["AKIA", "ABCDEFGHIJKLMNOP"].join(""), // built at runtime: fake, keeps secret scanners quiet
      pem: "-----BEGIN RSA PRIVATE KEY-----\nabc",
      url: "https://shop.example.test/product/a-100",
    });
    expect(out).toEqual({
      note: SECRET_MASK,
      dsnish: SECRET_MASK,
      aws: SECRET_MASK,
      pem: SECRET_MASK,
      url: "https://shop.example.test/product/a-100",
    });
  });

  it("leaves the contract connection example intact (it carries only references)", () => {
    const example = openapiExample<Record<string, unknown>>("connection-pg");
    expect(redactSecrets(example)).toEqual(example);
  });
});

describe("connection form checks", () => {
  it("accepts references and rejects raw values", () => {
    expect(isSecretRef("env:RESULTS_PG_PASSWORD")).toBe(true);
    expect(isSecretRef("file:/run/secrets/pg")).toBe(true);
    expect(isSecretRef("hunter2")).toBe(false);
    expect(validateConnectionSecrets({ host: "db" }, { password: "env:PG_PASSWORD" })).toEqual([]);
    const errors = validateConnectionSecrets({ host: "db", password: "hunter2" }, { password: "hunter2" });
    expect(errors).toHaveLength(2);
  });

  it("recognises secret-like keys in snake/camel/kebab case", () => {
    expect(looksLikeSecretKey("clientSecret")).toBe(true);
    expect(looksLikeSecretKey("x-api-key")).toBe(true);
    expect(looksLikeSecretKey("input_tokens")).toBe(false);
    expect(looksLikeSecretKey("secret_refs")).toBe(false);
  });
});
