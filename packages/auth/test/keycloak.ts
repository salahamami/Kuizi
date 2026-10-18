/**
 * Helpers for the integration tests against the local Keycloak (`make up`). Settings come from
 * the environment, then from the repository's .env, then from the .env.example defaults.
 * Only the synthetic dev users of infra/local/keycloak/kuizi-users-0.json are used.
 */
import { existsSync, readFileSync } from "node:fs";
import { parseEnv } from "node:util";
import { realmIssuer } from "../src/index.js";

const repoEnvFile = new URL("../../../.env", import.meta.url);
const fileEnv: Record<string, string | undefined> = existsSync(repoEnvFile)
  ? parseEnv(readFileSync(repoEnvFile, "utf8"))
  : {};
const setting = (name: string, fallback: string): string =>
  process.env[name] || fileEnv[name] || fallback;

export const KEYCLOAK_URL = setting("KEYCLOAK_URL", "http://localhost:8080").replace(/\/+$/, "");
export const REALM = setting("KEYCLOAK_REALM", "kuizi");
export const AUDIENCE = setting("KEYCLOAK_API_AUDIENCE", "kuizi-api");
export const ISSUER = realmIssuer(KEYCLOAK_URL, REALM);
const ADMIN = setting("KEYCLOAK_ADMIN", "admin");
const ADMIN_PASSWORD = setting("KEYCLOAK_ADMIN_PASSWORD", "admin-local-only");

/** Local-only client with the password grant (never exists outside the local stack). */
export const DEV_CLIENT = "kuizi-dev-cli";

/** Synthetic dev users: username, role, tenant. Passwords are `<username>-local-only`. */
export const DEV_USERS = [
  ["dev-student", "student", "demo-school-a"],
  ["dev-parent", "parent", "demo-school-a"],
  ["dev-teacher", "teacher", "demo-school-a"],
  ["dev-teacher-b", "teacher", "demo-school-b"],
  ["dev-school-admin", "school_admin", "demo-school-a"],
  ["dev-platform-admin", "platform_admin", "platform"],
  ["dev-curriculum-author", "curriculum_author", "platform"],
] as const;

export interface TokenResponse {
  access_token: string;
  id_token?: string;
  refresh_token: string;
  expires_in: number;
  refresh_expires_in: number;
}

export async function reachable(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(3000) });
    return response.ok;
  } catch {
    return false;
  }
}

export const keycloakReachable = () => reachable(`${ISSUER}/.well-known/openid-configuration`);

async function tokenRequest(form: Record<string, string>): Promise<Response> {
  return fetch(`${ISSUER}/protocol/openid-connect/token`, {
    method: "POST",
    body: new URLSearchParams({ client_id: DEV_CLIENT, ...form }),
  });
}

export async function passwordGrant(username: string, password = `${username}-local-only`) {
  const response = await tokenRequest({
    grant_type: "password",
    username,
    password,
    scope: "openid",
  });
  return {
    status: response.status,
    body: (await response.json()) as TokenResponse & { error?: string },
  };
}

export async function refreshGrant(refreshToken: string) {
  const response = await tokenRequest({ grant_type: "refresh_token", refresh_token: refreshToken });
  return {
    status: response.status,
    body: (await response.json()) as TokenResponse & { error?: string },
  };
}

export function claimsOf(jwt: string): Record<string, unknown> {
  const payload = jwt.split(".")[1] ?? "";
  return JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as Record<string, unknown>;
}

/** Calls the Keycloak admin REST API of the realm with the local bootstrap admin. */
export async function adminApi(method: string, path: string, body?: unknown): Promise<Response> {
  const login = await fetch(`${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token`, {
    method: "POST",
    body: new URLSearchParams({
      client_id: "admin-cli",
      grant_type: "password",
      username: ADMIN,
      password: ADMIN_PASSWORD,
    }),
  });
  const { access_token: token } = (await login.json()) as { access_token: string };
  const init: RequestInit = {
    method,
    headers: { authorization: `Bearer ${token}`, "content-type": "application/json" },
  };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
  }
  return fetch(`${KEYCLOAK_URL}/admin/realms/${REALM}${path}`, init);
}
