/**
 * AC1 on the local stack: real tokens from the running Keycloak pass the same checks Kong will
 * apply (signature against the realm JWKS, issuer, audience, expiry, tenant_id, roles).
 * Skips when Keycloak is not running (`make up` starts it).
 */
import { describe, expect, it } from "vitest";
import { createTokenVerifier, TokenVerificationError } from "../src/index.js";
import {
  AUDIENCE,
  claimsOf,
  DEV_USERS,
  ISSUER,
  keycloakReachable,
  passwordGrant,
  refreshGrant,
} from "./keycloak.js";

const running = await keycloakReachable();
const verifier = createTokenVerifier({ issuer: ISSUER, audience: AUDIENCE });

describe.skipIf(!running)(`Keycloak tokens (${ISSUER})`, () => {
  it.each(DEV_USERS)(
    "%s gets a token with role %s and tenant %s",
    async (username, role, tenant) => {
      const { status, body } = await passwordGrant(username);
      expect(status).toBe(200);
      const principal = await verifier.verify(body.access_token);
      expect(principal.tenantId).toBe(tenant);
      expect(principal.roles).toEqual([role]);
      expect(principal.clientId).toBe("kuizi-dev-cli");
    },
  );

  it("access tokens live 15 minutes and carry tenant_id and roles as top-level claims", async () => {
    const { body } = await passwordGrant("dev-student");
    // expires_in is counted from the current second, so it can read 899.
    expect(body.expires_in).toBeGreaterThanOrEqual(895);
    expect(body.expires_in).toBeLessThanOrEqual(900);
    const claims = claimsOf(body.access_token);
    expect(Number(claims["exp"]) - Number(claims["iat"])).toBe(900);
    expect(claims).toMatchObject({
      iss: ISSUER,
      aud: AUDIENCE,
      typ: "Bearer",
      tenant_id: "demo-school-a",
      roles: ["student"],
    });
  });

  it("access tokens carry no name, email or username (data minimisation)", async () => {
    const claims = claimsOf((await passwordGrant("dev-student")).body.access_token);
    for (const claim of [
      "email",
      "name",
      "given_name",
      "family_name",
      "preferred_username",
      "realm_access",
    ]) {
      expect(claims, claim).not.toHaveProperty(claim);
    }
  });

  it("two schools give two different tenants", async () => {
    const a = await verifier.verify((await passwordGrant("dev-teacher")).body.access_token);
    const b = await verifier.verify((await passwordGrant("dev-teacher-b")).body.access_token);
    expect(a.tenantId).not.toBe(b.tenantId);
  });

  it("an ID token is refused by the API", async () => {
    const { body } = await passwordGrant("dev-student");
    expect(body.id_token).toBeTypeOf("string");
    const error = await verifier.verify(body.id_token).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(TokenVerificationError);
    expect(["invalid_audience", "invalid_token_type"]).toContain(
      (error as TokenVerificationError).code,
    );
  });

  it("a verifier expecting another audience refuses Kuizi tokens", async () => {
    const other = createTokenVerifier({ issuer: ISSUER, audience: "another-api" });
    const { body } = await passwordGrant("dev-student");
    await expect(other.verify(body.access_token)).rejects.toMatchObject({
      code: "invalid_audience",
    });
  });

  it("refresh tokens rotate and a used refresh token is refused", async () => {
    const first = (await passwordGrant("dev-student")).body;
    const second = await refreshGrant(first.refresh_token);
    expect(second.status).toBe(200);
    expect(second.body.refresh_token).not.toBe(first.refresh_token);
    await expect(verifier.verify(second.body.access_token)).resolves.toBeDefined();

    const reuse = await refreshGrant(first.refresh_token);
    expect(reuse.status).toBe(400);
    expect(reuse.body.error).toBe("invalid_grant");
  });
});
