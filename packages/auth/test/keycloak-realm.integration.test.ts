/**
 * The realm settings T012 promises, checked on the running Keycloak: login page in Arabic (right
 * to left) and French (AC3), PKCE, password policy with the Have I Been Pwned check (AC2),
 * brute-force protection and the Google provider kept off. Skips when Keycloak is not running.
 * Creates one throwaway synthetic user and deletes it at the end.
 */
import { randomUUID } from "node:crypto";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { adminApi, ISSUER, keycloakReachable, passwordGrant, reachable } from "./keycloak.js";

const running = await keycloakReachable();
// The breach check needs the internet: skipped on an offline PC, like Keycloak then fails open.
const hibpOnline = running && (await reachable("https://api.pwnedpasswords.com/range/00000"));

const WEB_REDIRECT = "http://localhost:3000/callback";
const PKCE_CHALLENGE = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"; // RFC 7636 appendix B

function authUrl(params: Record<string, string>): string {
  const query = new URLSearchParams({
    client_id: "kuizi-web",
    response_type: "code",
    redirect_uri: WEB_REDIRECT,
    scope: "openid",
    ...params,
  });
  return `${ISSUER}/protocol/openid-connect/auth?${query.toString()}`;
}

async function loginPage(locale: string): Promise<string> {
  const response = await fetch(
    authUrl({ code_challenge: PKCE_CHALLENGE, code_challenge_method: "S256", ui_locales: locale }),
  );
  expect(response.status).toBe(200);
  return response.text();
}

describe.skipIf(!running)(`Keycloak realm settings (${ISSUER})`, () => {
  describe("login page", () => {
    it("renders right to left in Arabic, with Arabic labels", async () => {
      const html = await loginPage("ar");
      expect(html).toMatch(/<html[^>]*\blang="ar"/);
      expect(html).toMatch(/<html[^>]*\bdir="rtl"/);
      expect(html).toContain("كلمة المرور"); // "Password"
      expect(html).toContain("تسجيل دخول"); // "Sign in" button
    });

    it("renders left to right in French, with French labels", async () => {
      const html = await loginPage("fr");
      expect(html).toMatch(/<html[^>]*\blang="fr"/);
      expect(html).toMatch(/<html[^>]*\bdir="ltr"/);
      expect(html).toContain("Mot de passe");
      expect(html).toContain("Connexion");
    });

    it("offers exactly French and Arabic", async () => {
      const html = await loginPage("fr");
      const locales = [...html.matchAll(/kc_locale=([a-z-]+)/g)].map((m) => m[1]).sort();
      expect(locales).toEqual(["ar", "fr"]);
    });

    it("the web client refuses a sign-in without PKCE", async () => {
      const response = await fetch(authUrl({ ui_locales: "fr" }), { redirect: "manual" });
      const location = new URL(response.headers.get("location") ?? "", ISSUER);
      expect(location.searchParams.get("error")).toBe("invalid_request");
      expect(location.searchParams.get("error_description")).toMatch(/code_challenge/);
    });
  });

  describe("password policy and brute-force protection", () => {
    const username = `t012-check-${randomUUID().slice(0, 8)}`;
    let userId = "";

    beforeAll(async () => {
      const created = await adminApi("POST", "/users", {
        username,
        enabled: true,
        email: `${username}@kuizi.test`,
        emailVerified: true,
        firstName: "Policy",
        lastName: "Check",
        attributes: { tenant_id: ["demo-school-a"] },
      });
      expect(created.status).toBe(201);
      userId = (created.headers.get("location") ?? "").split("/").pop() ?? "";
    });

    afterAll(async () => {
      if (userId) {
        await adminApi("DELETE", `/attack-detection/brute-force/users/${userId}`);
        await adminApi("DELETE", `/users/${userId}`);
      }
    });

    async function setPassword(value: string) {
      const response = await adminApi("PUT", `/users/${userId}/reset-password`, {
        type: "password",
        value,
        temporary: false,
      });
      const text = await response.text();
      return {
        status: response.status,
        error: text ? (JSON.parse(text) as { error?: string }).error : undefined,
      };
    }

    it("refuses passwords shorter than 12 characters", async () => {
      expect(await setPassword("Short-pw-11")).toEqual({
        status: 400,
        error: "invalidPasswordMinLengthMessage",
      });
    });

    it("refuses the username as password", async () => {
      expect((await setPassword(username)).error).toBe("invalidPasswordNotUsernameMessage");
    });

    it.skipIf(!hibpOnline)("refuses a password found in Have I Been Pwned", async () => {
      // "Password1234!" passes length and character rules but appears in known breaches.
      expect(await setPassword("Password1234!")).toEqual({
        status: 400,
        error: "invalidPasswordPwnedMessage",
      });
    });

    it("accepts a long, unusual passphrase", async () => {
      expect((await setPassword(`violet-otter-${randomUUID()}`)).status).toBe(204);
    });

    // Keycloak 26.8 refuses a password grant with HTTP 400 invalid_grant (RFC 6749 section 5.2);
    // 26.1 answered 401. Both mean "no token".
    async function expectRefused(password: string) {
      const { status, body } = await passwordGrant(username, password);
      expect([400, 401]).toContain(status);
      expect(body.error).toBe("invalid_grant");
    }

    it("locks the account for a while after 5 failed sign-ins", async () => {
      const password = `amber-falcon-${randomUUID()}`;
      expect((await setPassword(password)).status).toBe(204);
      for (let attempt = 0; attempt < 5; attempt += 1) {
        await expectRefused("not-the-password-local-only");
      }
      const state = (await (
        await adminApi("GET", `/attack-detection/brute-force/users/${userId}`)
      ).json()) as { disabled: boolean; numFailures: number };
      expect(state.disabled).toBe(true);
      await expectRefused(password); // the right password is refused while locked
    });
  });

  it("the Google provider exists but stays off without credentials", async () => {
    const response = await adminApi("GET", "/identity-provider/instances/google");
    expect(response.status).toBe(200);
    const google = (await response.json()) as { enabled: boolean; providerId: string };
    expect(google).toMatchObject({ providerId: "google", enabled: false });
  });
});
