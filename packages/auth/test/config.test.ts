import { describe, expect, it } from "vitest";
import { realmIssuer, verifierConfigFromEnv } from "../src/index.js";

describe("verifierConfigFromEnv", () => {
  it("builds issuer, audience and JWKS URL from the .env names", () => {
    expect(
      verifierConfigFromEnv({ KEYCLOAK_URL: "http://localhost:8080/", KEYCLOAK_REALM: "kuizi" }),
    ).toEqual({
      issuer: "http://localhost:8080/realms/kuizi",
      audience: "kuizi-api",
      jwksUri: "http://localhost:8080/realms/kuizi/protocol/openid-connect/certs",
    });
  });

  it("reads the audience when it is set", () => {
    const config = verifierConfigFromEnv({
      KEYCLOAK_URL: "https://id.example.test",
      KEYCLOAK_REALM: "kuizi",
      KEYCLOAK_API_AUDIENCE: "kuizi-api-staging",
    });
    expect(config.audience).toBe("kuizi-api-staging");
  });

  it("fails at start-up when a variable is missing", () => {
    expect(() => verifierConfigFromEnv({ KEYCLOAK_URL: "http://localhost:8080" })).toThrow(
      /KEYCLOAK_REALM/,
    );
    expect(() => verifierConfigFromEnv({})).toThrow(/KEYCLOAK_URL, KEYCLOAK_REALM/);
  });

  it("encodes the realm name", () => {
    expect(realmIssuer("http://kc", "a b")).toBe("http://kc/realms/a%20b");
  });
});
