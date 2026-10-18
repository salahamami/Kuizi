# 0009. Identity: one Keycloak realm, tenant and role claims, a Kuizi Keycloak image

- Status: Proposed (the product owner accepts it by merging T012)
- Date: 2026-10-18

## Context

T012 makes Keycloak the single OIDC issuer for students, parents, teachers, school admins and Kuizi staff. Everything after it builds on its tokens: parental consent (T013), the authorisation middleware (T014), row-level security by tenant (T092), the web and mobile apps (T076, T163), school single sign-on (T094) and the gateway (T005). The ticket also asks for a breached-password check through Have I Been Pwned, which Keycloak does not provide, and for a login page that works in French and Arabic. Keycloak extensions are written in Java, a language [ADR 0008](0008-monorepo-layout-and-toolchains.md) does not list.

## Decision

- **One realm, `kuizi`, one issuer.** Roles distinguish populations (`student`, `parent`, `teacher`, `school_admin`, `platform_admin`, `curriculum_author`); the school is a user attribute, `tenant_id`, editable by admins only. No realm per role or per school: per-school sign-in (T094) is identity brokering into this realm.
- **A token contract every service relies on.** Access tokens carry `sub`, top-level `tenant_id` and `roles`, `aud` = `kuizi-api`, live 15 minutes, and carry no name or email (lightweight access tokens). Refresh tokens rotate and cannot be reused. Clients are public with PKCE S256 (`kuizi-web`, `kuizi-mobile`).
- **Services verify tokens themselves** with the shared library `packages/auth` (`@kuizi/auth`, built on `jose`), applying the same checks Kong will apply at the gateway (T005): signature against the realm JWKS, issuer, audience, expiry, token type, lifetime, `tenant_id`, `roles`. The gateway is a first line, not the only one.
- **A Kuizi Keycloak image** in `services/keycloak/`: stock Keycloak plus Kuizi's extensions, built by `docker compose` on the first `make up` and later pushed for EKS (T240). The first extensions are the `pwnedPassword` password policy (k-anonymity: only 5 characters of the SHA-1 hash leave Keycloak; fails open when the API is unreachable) and a login theme that raises touch targets to 44 px.
- **Java for Keycloak extensions only**, with Maven, built inside the image build (Maven image) so the product owner's PC needs no JDK. Unit tests run during the image build.

## Consequences

- Kong and every service trust one issuer and one key set; adding a population is adding a role, not a realm.
- T014 and T092 read `tenant_id` and `roles` straight from verified tokens; the second dev school (`demo-school-b`) gives them a cross-tenant test case from day one.
- Because access tokens live 15 minutes, anything that must take effect faster (consent revoked by a parent must freeze a student within 1 minute, T013) needs a check in services in addition to Keycloak, for example a revocation list read by `@kuizi/auth`.
- The image adds a build step and a Java toolchain to maintain: the provider's `keycloak.version` must follow the Keycloak image tag, and the provider uses Keycloak's internal password-policy SPI, which may change between major versions (Keycloak logs a warning at start-up). Upgrades re-run the provider's unit tests in the image build and the integration tests in `packages/auth`.
- The first `make up` needs the internet for a few extra minutes (Maven image and dependencies), and the breach check needs the internet at run time; offline, passwords are judged on the other rules.
- ADR 0008's toolchain list gains Java for `services/keycloak/providers/*`; CI (T006) can build the image to run those tests.
