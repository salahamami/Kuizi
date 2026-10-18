import { exportJWK, generateKeyPair, SignJWT, type JSONWebKeySet, type JWTPayload } from "jose";

export const ISSUER = "http://localhost:8080/realms/kuizi";
export const AUDIENCE = "kuizi-api";

/** A locally generated realm signing key, like Keycloak's RS256 key. */
export interface TestRealm {
  readonly jwks: JSONWebKeySet;
  sign(
    claims: JWTPayload,
    options?: { alg?: string; kid?: string; lifetime?: number; iat?: number },
  ): Promise<string>;
}

export async function createTestRealm(kid = "test-key-1"): Promise<TestRealm> {
  const { publicKey, privateKey } = await generateKeyPair("RS256", { extractable: true });
  const jwk = { ...(await exportJWK(publicKey)), kid, alg: "RS256", use: "sig" };
  return {
    jwks: { keys: [jwk] },
    async sign(claims, options = {}) {
      const iat = options.iat ?? Math.floor(Date.now() / 1000);
      return new SignJWT(claims)
        .setProtectedHeader({ alg: options.alg ?? "RS256", typ: "JWT", kid: options.kid ?? kid })
        .setIssuedAt(iat)
        .setExpirationTime(iat + (options.lifetime ?? 900))
        .sign(privateKey);
    },
  };
}

/**
 * The claims a Keycloak access token for dev-student carries (lightweight token, T012 realm).
 * An override set to `undefined` removes the claim.
 */
export function studentClaims(overrides: Record<string, unknown> = {}): JWTPayload {
  const claims: Record<string, unknown> = {
    iss: ISSUER,
    aud: AUDIENCE,
    sub: "f41e3b5c-b3e8-484d-8d70-a5405d99b689",
    typ: "Bearer",
    azp: "kuizi-web",
    sid: "5c08c133-6beb-4e9d-b6be-360b0c866c4c",
    jti: "9bce6cbe-1147-4158-85b6-9bbabaad7586",
    scope: "openid email profile",
    tenant_id: "demo-school-a",
    roles: ["student"],
    ...overrides,
  };
  return Object.fromEntries(Object.entries(claims).filter(([, value]) => value !== undefined));
}
