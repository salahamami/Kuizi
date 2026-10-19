# @kuizi/auth

Verifies Keycloak access tokens in Kuizi's TypeScript services (T012). It applies the checks Kong will apply at the gateway in the cloud (T005), so a service is protected even when a request did not go through the gateway. Background: [`docs/dev/identity.md`](../../docs/dev/identity.md).

```ts
import {
  bearerToken,
  createTokenVerifier,
  TokenVerificationError,
  verifierConfigFromEnv,
  wwwAuthenticate,
} from "@kuizi/auth";

// KEYCLOAK_URL, KEYCLOAK_REALM and KEYCLOAK_API_AUDIENCE (default kuizi-api), see .env.example.
const verifier = createTokenVerifier(verifierConfigFromEnv());

async function authenticate(authorization: string | undefined) {
  try {
    const principal = await verifier.verify(bearerToken(authorization));
    return principal; // { subject, tenantId, roles, clientId, sessionId, tokenId, scopes, expiresAt }
  } catch (error) {
    if (error instanceof TokenVerificationError) {
      // error.status is 401, or 503 when Keycloak's keys cannot be fetched.
      // Reply with header WWW-Authenticate: wwwAuthenticate(error). error.message is safe to log.
    }
    throw error;
  }
}
```

## What is checked

1. A token is present (`missing_token`) and smaller than 8 KB (`malformed_token`).
2. RS256 signature against the realm's keys (`invalid_signature`). Keys come from `${issuer}/protocol/openid-connect/certs`, are cached for 10 minutes and refetched when a token names an unknown key, so Keycloak key rotation needs no restart. HMAC and unsigned tokens are refused.
3. `iss` is the realm (`invalid_issuer`); `aud` contains `kuizi-api` (`invalid_audience`).
4. `exp`, `nbf` and `iat` with 5 seconds of clock tolerance (`token_expired`, `token_not_yet_valid`).
5. `typ` is `Bearer`, so ID tokens are refused (`invalid_token_type`); lifetime `exp - iat` is at most 900 seconds (`token_lifetime_too_long`).
6. `sub` is present (`missing_claim`); `tenant_id` is present and matches `^[a-z0-9][a-z0-9-]{0,62}$` (`missing_tenant`); `roles` holds at least one Kuizi role (`missing_roles`). Unknown roles are dropped.

Errors never contain the token or claim values. Authorisation (which role may do what in which tenant) is not here: it is the job of the middleware in T014.

## Options

`createTokenVerifier({ issuer, audience, jwksUri?, jwks?, algorithms?, clockToleranceSeconds?, maxTokenLifetimeSeconds?, now? })`: `jwks` takes a fixed key set (tests, offline tools); `now` fixes the clock in tests.

## Scripts

```bash
pnpm --filter @kuizi/auth lint
pnpm --filter @kuizi/auth typecheck
pnpm --filter @kuizi/auth test    # unit tests with local keys + integration tests against the local Keycloak
pnpm --filter @kuizi/auth build
```

The integration tests (`test/*.integration.test.ts`) use the synthetic dev users and the local-only `kuizi-dev-cli` client; they skip themselves when Keycloak is not reachable. Settings come from the environment, then the repository's `.env`, then the `.env.example` defaults.
