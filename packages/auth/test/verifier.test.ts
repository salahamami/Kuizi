import { createServer, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import { SignJWT, UnsecuredJWT, type JSONWebKeySet } from "jose";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import {
  bearerToken,
  createTokenVerifier,
  TokenVerificationError,
  wwwAuthenticate,
  type TokenErrorCode,
  type TokenVerifier,
} from "../src/index.js";
import { AUDIENCE, createTestRealm, ISSUER, studentClaims, type TestRealm } from "./helpers.js";

let realm: TestRealm;
let verifier: TokenVerifier;

beforeAll(async () => {
  realm = await createTestRealm();
  verifier = createTokenVerifier({ issuer: ISSUER, audience: AUDIENCE, jwks: realm.jwks });
});

async function refusal(token: string | undefined, using: TokenVerifier = verifier) {
  const error = await using.verify(token).then(
    () => undefined,
    (e: unknown) => e,
  );
  expect(error, "the token should be refused").toBeInstanceOf(TokenVerificationError);
  return error as TokenVerificationError;
}

async function expectRefused(token: string | undefined, code: TokenErrorCode) {
  const error = await refusal(token);
  expect(error.code).toBe(code);
  expect(error.status).toBe(401);
  if (token) {
    expect(error.message, "messages are logged and must not contain the token").not.toContain(
      token,
    );
  }
}

describe("a valid Keycloak access token", () => {
  it("gives the principal with subject, tenant and roles", async () => {
    const principal = await verifier.verify(await realm.sign(studentClaims()));
    expect(principal).toMatchObject({
      subject: "f41e3b5c-b3e8-484d-8d70-a5405d99b689",
      tenantId: "demo-school-a",
      roles: ["student"],
      clientId: "kuizi-web",
      sessionId: "5c08c133-6beb-4e9d-b6be-360b0c866c4c",
      tokenId: "9bce6cbe-1147-4158-85b6-9bbabaad7586",
      scopes: ["openid", "email", "profile"],
    });
    expect(principal.expiresAt.getTime()).toBeGreaterThan(Date.now());
  });

  it("accepts an audience list that includes kuizi-api", async () => {
    const token = await realm.sign(studentClaims({ aud: ["account", AUDIENCE] }));
    await expect(verifier.verify(token)).resolves.toMatchObject({ tenantId: "demo-school-a" });
  });

  it("keeps only Kuizi roles, once each", async () => {
    const token = await realm.sign(
      studentClaims({ roles: ["teacher", "offline_access", "teacher", "school_admin", 42] }),
    );
    const principal = await verifier.verify(token);
    expect(principal.roles).toEqual(["teacher", "school_admin"]);
  });

  it("accepts a UUID tenant and the reserved tenants", async () => {
    for (const tenant of ["0b7c2f0e-8d1a-4c47-9e43-6f4b1c2d3e4f", "individual", "platform"]) {
      const principal = await verifier.verify(
        await realm.sign(studentClaims({ tenant_id: tenant })),
      );
      expect(principal.tenantId).toBe(tenant);
    }
  });

  it("tolerates a few seconds of clock skew", async () => {
    const iat = Math.floor(Date.now() / 1000) - 903; // expired 3 seconds ago
    await expect(
      verifier.verify(await realm.sign(studentClaims(), { iat })),
    ).resolves.toBeDefined();
  });
});

describe("refused tokens", () => {
  it("no token at all", async () => {
    await expectRefused(undefined, "missing_token");
    await expectRefused("", "missing_token");
  });

  it("not a JWT", async () => {
    await expectRefused("not-a-jwt", "malformed_token");
    await expectRefused("a".repeat(9000), "malformed_token");
  });

  it("signed by another key (forged or from another Keycloak)", async () => {
    const other = await createTestRealm();
    await expectRefused(await other.sign(studentClaims()), "invalid_signature");
  });

  it("unknown key ID", async () => {
    const other = await createTestRealm("unknown-kid");
    await expectRefused(await other.sign(studentClaims()), "invalid_signature");
  });

  it("an HMAC token (algorithm confusion)", async () => {
    const token = await new SignJWT(studentClaims())
      .setProtectedHeader({ alg: "HS256", kid: "test-key-1" })
      .setIssuedAt()
      .setExpirationTime("15m")
      .sign(new TextEncoder().encode("a-shared-secret-that-is-long-enough"));
    await expectRefused(token, "invalid_signature");
  });

  it("an unsigned token (alg none)", async () => {
    const token = new UnsecuredJWT(studentClaims()).setIssuedAt().setExpirationTime("15m").encode();
    const error = await refusal(token);
    expect(["invalid_signature", "malformed_token"]).toContain(error.code);
  });

  it("another issuer", async () => {
    const token = await realm.sign(studentClaims({ iss: "http://localhost:8080/realms/master" }));
    await expectRefused(token, "invalid_issuer");
  });

  it("another audience, or none", async () => {
    await expectRefused(await realm.sign(studentClaims({ aud: "kuizi-web" })), "invalid_audience");
    await expectRefused(await realm.sign(studentClaims({ aud: undefined })), "invalid_audience");
  });

  it("expired", async () => {
    const iat = Math.floor(Date.now() / 1000) - 1000;
    await expectRefused(await realm.sign(studentClaims(), { iat }), "token_expired");
  });

  it("not valid yet", async () => {
    const nbf = Math.floor(Date.now() / 1000) + 600;
    await expectRefused(await realm.sign(studentClaims({ nbf })), "token_not_yet_valid");
  });

  it("an ID token or a token without a type", async () => {
    await expectRefused(await realm.sign(studentClaims({ typ: "ID" })), "invalid_token_type");
    await expectRefused(await realm.sign(studentClaims({ typ: undefined })), "invalid_token_type");
  });

  it("a token that lives longer than 15 minutes", async () => {
    await expectRefused(
      await realm.sign(studentClaims(), { lifetime: 3600 }),
      "token_lifetime_too_long",
    );
  });

  it("no subject", async () => {
    await expectRefused(await realm.sign(studentClaims({ sub: undefined })), "missing_claim");
  });

  it("no tenant_id, or one that is not a tenant ID", async () => {
    for (const tenant of [
      undefined,
      "",
      42,
      ["demo-school-a"],
      "Demo School",
      "../other",
      "x".repeat(64),
    ]) {
      await expectRefused(await realm.sign(studentClaims({ tenant_id: tenant })), "missing_tenant");
    }
  });

  it("no Kuizi role", async () => {
    for (const roles of [undefined, [], ["offline_access", "uma_authorization"], "student"]) {
      await expectRefused(await realm.sign(studentClaims({ roles })), "missing_roles");
    }
  });
});

describe("options", () => {
  it("a fixed clock decides expiry", async () => {
    const token = await realm.sign(studentClaims());
    const later = createTokenVerifier({
      issuer: ISSUER,
      audience: AUDIENCE,
      jwks: realm.jwks,
      now: () => new Date(Date.now() + 20 * 60_000),
    });
    expect((await refusal(token, later)).code).toBe("token_expired");
  });

  it("a longer lifetime can be allowed explicitly", async () => {
    const relaxed = createTokenVerifier({
      issuer: ISSUER,
      audience: AUDIENCE,
      jwks: realm.jwks,
      maxTokenLifetimeSeconds: 3600,
    });
    const token = await realm.sign(studentClaims(), { lifetime: 3600 });
    await expect(relaxed.verify(token)).resolves.toBeDefined();
  });
});

describe("signing keys fetched from the realm (JWKS URL)", () => {
  let server: Server;
  let baseUrl: string;
  let jwks: JSONWebKeySet | undefined;
  let requests = 0;

  beforeAll(async () => {
    server = createServer((req, res) => {
      requests += 1;
      if (req.url === "/realms/kuizi/protocol/openid-connect/certs" && jwks) {
        res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify(jwks));
      } else {
        res.writeHead(500).end("down");
      }
    });
    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
    baseUrl = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
  });

  afterAll(() => new Promise<void>((resolve) => server.close(() => resolve())));

  it("fetches the keys from the default URL and caches them", async () => {
    jwks = realm.jwks;
    const issuer = `${baseUrl}/realms/kuizi`;
    const remote = createTokenVerifier({ issuer, audience: AUDIENCE });
    requests = 0;
    const token = await realm.sign(studentClaims({ iss: issuer }));
    await expect(remote.verify(token)).resolves.toMatchObject({ roles: ["student"] });
    await expect(remote.verify(token)).resolves.toBeDefined();
    expect(requests).toBe(1);
  });

  it("answers 503 when the keys cannot be fetched", async () => {
    jwks = undefined;
    const issuer = `${baseUrl}/realms/kuizi`;
    const remote = createTokenVerifier({ issuer, audience: AUDIENCE });
    const error = await refusal(await realm.sign(studentClaims({ iss: issuer })), remote);
    expect(error.code).toBe("jwks_unavailable");
    expect(error.status).toBe(503);
  });

  it("answers 503 when Keycloak cannot be reached at all", async () => {
    const remote = createTokenVerifier({
      issuer: ISSUER,
      audience: AUDIENCE,
      jwksUri: "http://127.0.0.1:9/realms/kuizi/protocol/openid-connect/certs",
    });
    const error = await refusal(await realm.sign(studentClaims()), remote);
    expect(error.code).toBe("jwks_unavailable");
  });
});

describe("bearerToken and wwwAuthenticate", () => {
  it("reads the token from an Authorization header", () => {
    expect(bearerToken("Bearer abc.def.ghi")).toBe("abc.def.ghi");
    expect(bearerToken("bearer abc.def-_.ghi")).toBe("abc.def-_.ghi");
  });

  it("refuses a missing header or another scheme", () => {
    for (const header of [undefined, null, "", "Basic dXNlcjpwYXNz", "Bearer", "Bearer a b"]) {
      expect(() => bearerToken(header)).toThrow(TokenVerificationError);
    }
  });

  it("builds RFC 6750 challenges", () => {
    expect(wwwAuthenticate(new TokenVerificationError("missing_token", "x"))).toBe(
      'Bearer realm="kuizi"',
    );
    expect(wwwAuthenticate(new TokenVerificationError("token_expired", "x"))).toBe(
      'Bearer realm="kuizi", error="invalid_token", error_description="token_expired"',
    );
    expect(wwwAuthenticate(new TokenVerificationError("jwks_unavailable", "x"))).toContain(
      "temporarily_unavailable",
    );
  });
});
