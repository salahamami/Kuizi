/**
 * Kuizi realm roles (T012). They arrive in the top-level `roles` claim of every access token.
 * Keycloak only puts these roles in tokens (clients use `fullScopeAllowed: false` with a scope
 * mapping to exactly this list), and the verifier ignores any other value as a second guard.
 */
export const KUIZI_ROLES = [
  "student",
  "parent",
  "teacher",
  "school_admin",
  "platform_admin",
  "curriculum_author",
] as const;

export type KuiziRole = (typeof KUIZI_ROLES)[number];

const ROLE_SET: ReadonlySet<string> = new Set(KUIZI_ROLES);

export function isKuiziRole(value: unknown): value is KuiziRole {
  return typeof value === "string" && ROLE_SET.has(value);
}

/**
 * Tenant identifiers: a school's ID, or one of the reserved tenants `individual` (students and
 * parents without a school) and `platform` (Kuizi staff). Same pattern as the Keycloak user
 * profile validation on the `tenant_id` attribute.
 */
export const TENANT_ID_PATTERN = /^[a-z0-9][a-z0-9-]{0,62}$/;

export function isTenantId(value: unknown): value is string {
  return typeof value === "string" && TENANT_ID_PATTERN.test(value);
}
