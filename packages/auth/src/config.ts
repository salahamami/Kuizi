/** Where a service finds Keycloak: the same variable names locally and in the cloud (ADR 0006). */
export interface VerifierConfig {
  /** Expected `iss` claim: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}`. */
  readonly issuer: string;
  /** Expected `aud` value: `KEYCLOAK_API_AUDIENCE`, default `kuizi-api`. */
  readonly audience: string;
  /** The realm's signing keys (JWKS). */
  readonly jwksUri: string;
}

export const DEFAULT_AUDIENCE = "kuizi-api";

export function realmIssuer(keycloakUrl: string, realm: string): string {
  return `${keycloakUrl.replace(/\/+$/, "")}/realms/${encodeURIComponent(realm)}`;
}

export function jwksUriFor(issuer: string): string {
  return `${issuer}/protocol/openid-connect/certs`;
}

/**
 * Reads `KEYCLOAK_URL`, `KEYCLOAK_REALM` and `KEYCLOAK_API_AUDIENCE` (see `.env.example`).
 * Throws when a required variable is missing, so a misconfigured service fails at start-up
 * instead of refusing every request.
 */
export function verifierConfigFromEnv(
  env: Readonly<Record<string, string | undefined>> = process.env,
): VerifierConfig {
  const keycloakUrl = env["KEYCLOAK_URL"]?.trim();
  const realm = env["KEYCLOAK_REALM"]?.trim();
  const missing = [!keycloakUrl && "KEYCLOAK_URL", !realm && "KEYCLOAK_REALM"].filter(Boolean);
  if (!keycloakUrl || !realm) {
    throw new Error(`Missing environment variable(s): ${missing.join(", ")} (see .env.example)`);
  }
  const issuer = realmIssuer(keycloakUrl, realm);
  return {
    issuer,
    audience: env["KEYCLOAK_API_AUDIENCE"]?.trim() || DEFAULT_AUDIENCE,
    jwksUri: jwksUriFor(issuer),
  };
}
