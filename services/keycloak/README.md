# Kuizi Keycloak image

Stock Keycloak (`quay.io/keycloak/keycloak:26.1.4`) plus Kuizi's extensions (T012, [ADR 0009](../../docs/architecture/decisions/0009-identity-single-realm-and-keycloak-image.md)). The local stack builds it on the first `make up`; the cloud uses the same image (T240). The realm itself lives in [`infra/local/keycloak/`](../../infra/local/keycloak/) and is explained in [`docs/dev/identity.md`](../../docs/dev/identity.md).

| Path | What |
| --- | --- |
| `Dockerfile` | Two stages: Maven builds and tests the providers, then they are copied into the Keycloak image with the themes |
| `providers/pwned-password-policy/` | Password policy `pwnedPassword(N)`: refuses passwords found at least N times in Have I Been Pwned |
| `themes/kuizi/login/` | Login theme: Keycloak's `keycloak.v2` with touch targets of at least 44 px and a fixed Arabic title |

## Build

`make up` builds the image when it is missing (tag in `infra/local/compose.yaml`). After changing anything here, bump that tag or rebuild:

```bash
docker compose -f infra/local/compose.yaml --env-file .env build keycloak
```

No Java is needed on the PC. To work on the provider with a local JDK 21 and Maven:

```bash
cd services/keycloak/providers/pwned-password-policy
mvn -B package        # compiles, runs the unit tests, writes target/kuizi-pwned-password-policy.jar
```

`ARG MAVEN_IMAGE` lets a build use a mirror of the Maven image when Docker Hub rate-limits pulls.

## `pwnedPassword` password policy

The realm sets it in its policy string: `... and pwnedPassword(1)`; the number is the minimum count of breaches that refuses a password.

How it checks a password (k-anonymity):

1. SHA-1 of the UTF-8 password, in upper-case hex.
2. `GET https://api.pwnedpasswords.com/range/<first 5 characters>` with `Add-Padding: true`, through Keycloak's own HTTP client (so Keycloak's proxy and truststore settings apply).
3. The answer lists every known suffix for that prefix (padded with fake zero-count entries); the provider looks for the remaining 35 characters locally.

Only the 5-character prefix leaves Keycloak. The password, its hash and the prefix are never logged. The unit tests (`PwnedPasswordCheckerTest`) check that exactly 5 characters are sent, parsing, padding, thresholds and both failure modes.

Server settings (environment variables of the Keycloak container, all optional):

| Variable | Default | Meaning |
| --- | --- | --- |
| `KC_SPI_PASSWORD_POLICY_PWNED_PASSWORD_API_URL` | `https://api.pwnedpasswords.com/range/` | Range API base URL (a self-hosted mirror, or a stub in tests) |
| `KC_SPI_PASSWORD_POLICY_PWNED_PASSWORD_TIMEOUT_MS` | `2000` | Connect and read timeout |
| `KC_SPI_PASSWORD_POLICY_PWNED_PASSWORD_FAIL_CLOSED` | `false` | When the API cannot be reached: refuse the password (`true`) or judge it on the other rules and log `Pwned-password check unavailable` (`false`) |

Messages shown to users are in `src/main/resources/theme-resources/messages/` (French, Arabic, English fallback); they are product copy reviewed by the product owner.

If the API is blocked on a network, two fallbacks exist: a self-hosted copy of the range data (the API URL setting), or Keycloak's built-in `passwordBlacklist` policy with a file of common passwords.

Keycloak logs `pwnedPassword ... is implementing the internal SPI password-policy` at start-up: password policies are an internal extension point that may change in a major Keycloak upgrade. Upgrading Keycloak means changing `KEYCLOAK_VERSION` in the `Dockerfile` and `keycloak.version` in the `pom.xml` together, then rebuilding (the unit tests run in the build) and running `pnpm --filter @kuizi/auth test` against the new image.
