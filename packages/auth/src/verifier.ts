import {
  createLocalJWKSet,
  createRemoteJWKSet,
  errors,
  jwtVerify,
  type JSONWebKeySet,
  type JWTPayload,
  type JWTVerifyOptions,
} from "jose";
import { jwksUriFor } from "./config.js";
import { TokenVerificationError } from "./errors.js";
import { isKuiziRole, isTenantId, type KuiziRole } from "./roles.js";

/** Who is calling, taken from a verified access token. Holds no name or email (T012 tokens carry none). */
export interface KuiziPrincipal {
  /** Keycloak user ID (`sub`), stable for the life of the account. */
  readonly subject: string;
  /** Tenant the user belongs to (`tenant_id`): a school, `individual` or `platform`. */
  readonly tenantId: string;
  /** Kuizi roles of the user (`roles`), never empty. */
  readonly roles: readonly KuiziRole[];
  /** Client the token was issued to (`azp`), for example `kuizi-web`. */
  readonly clientId: string | undefined;
  /** Keycloak session ID (`sid`). */
  readonly sessionId: string | undefined;
  /** Token ID (`jti`). */
  readonly tokenId: string | undefined;
  /** Granted OAuth scopes (`scope`). */
  readonly scopes: readonly string[];
  readonly expiresAt: Date;
}

export interface TokenVerifierOptions {
  /** Expected `iss`, for example `http://localhost:8080/realms/kuizi`. */
  readonly issuer: string;
  /** Expected audience, `kuizi-api` for every Kuizi service. */
  readonly audience: string;
  /** Realm signing keys URL. Default: `${issuer}/protocol/openid-connect/certs`. */
  readonly jwksUri?: string;
  /** Fixed key set instead of fetching one (tests and offline tools). */
  readonly jwks?: JSONWebKeySet;
  /** Accepted signature algorithms. Default `["RS256"]`, the realm's algorithm. */
  readonly algorithms?: readonly string[];
  /** Clock skew allowed on `exp`, `nbf` and `iat`, in seconds. Default 5. */
  readonly clockToleranceSeconds?: number;
  /** Longest accepted token lifetime (`exp - iat`), in seconds. Default 900, the realm's 15 minutes. */
  readonly maxTokenLifetimeSeconds?: number;
  /** Clock used for the time checks (tests). Default: the system clock. */
  readonly now?: () => Date;
}

export interface TokenVerifier {
  /** Verifies an access token and returns its principal, or throws {@link TokenVerificationError}. */
  verify(token: string | undefined | null): Promise<KuiziPrincipal>;
}

/** Access tokens are a few hundred bytes; anything this large is refused before parsing. */
const MAX_TOKEN_LENGTH = 8192;

/**
 * Creates a verifier that applies, in a service, the checks Kong will apply at the gateway
 * (docs/dev/identity.md): RS256 signature against the realm keys, issuer, audience, expiry,
 * Keycloak access-token type, lifetime, and the `tenant_id` and `roles` claims.
 */
export function createTokenVerifier(options: TokenVerifierOptions): TokenVerifier {
  const keys = options.jwks
    ? createLocalJWKSet(options.jwks)
    : createRemoteJWKSet(new URL(options.jwksUri ?? jwksUriFor(options.issuer)), {
        timeoutDuration: 5_000,
        cooldownDuration: 30_000,
        cacheMaxAge: 10 * 60_000,
      });
  const algorithms = [...(options.algorithms ?? ["RS256"])];
  const tolerance = options.clockToleranceSeconds ?? 5;
  const maxLifetime = options.maxTokenLifetimeSeconds ?? 900;

  return {
    async verify(token) {
      if (!token) {
        throw new TokenVerificationError("missing_token", "No access token");
      }
      if (token.length > MAX_TOKEN_LENGTH) {
        throw new TokenVerificationError("malformed_token", "Access token is too large");
      }
      const verifyOptions: JWTVerifyOptions = {
        issuer: options.issuer,
        audience: options.audience,
        algorithms,
        clockTolerance: tolerance,
        requiredClaims: ["exp", "iat", "sub"],
      };
      if (options.now) {
        verifyOptions.currentDate = options.now();
      }

      let payload: JWTPayload;
      try {
        ({ payload } = await jwtVerify(token, keys, verifyOptions));
      } catch (error) {
        throw toVerificationError(error);
      }
      return principalFrom(payload, maxLifetime, tolerance);
    },
  };
}

function principalFrom(
  payload: JWTPayload,
  maxLifetime: number,
  tolerance: number,
): KuiziPrincipal {
  // Keycloak marks access tokens "Bearer"; ID tokens ("ID") and others are refused.
  if (payload["typ"] !== "Bearer") {
    throw new TokenVerificationError("invalid_token_type", "Not a Keycloak access token");
  }
  const { exp, iat, sub } = payload as Required<Pick<JWTPayload, "exp" | "iat" | "sub">>;
  if (exp - iat > maxLifetime + tolerance) {
    throw new TokenVerificationError(
      "token_lifetime_too_long",
      `Access token lifetime is longer than ${maxLifetime} seconds`,
    );
  }
  if (typeof sub !== "string" || sub.length === 0) {
    throw new TokenVerificationError("missing_claim", "Access token has no subject");
  }
  const tenantId = payload["tenant_id"];
  if (!isTenantId(tenantId)) {
    throw new TokenVerificationError("missing_tenant", "Access token has no valid tenant_id claim");
  }
  const rawRoles = payload["roles"];
  const roles = Array.isArray(rawRoles) ? [...new Set(rawRoles.filter(isKuiziRole))] : [];
  if (roles.length === 0) {
    throw new TokenVerificationError("missing_roles", "Access token has no Kuizi role");
  }
  const scope = payload["scope"];
  return {
    subject: sub,
    tenantId,
    roles,
    clientId: stringClaim(payload["azp"]),
    sessionId: stringClaim(payload["sid"]),
    tokenId: stringClaim(payload.jti),
    scopes: typeof scope === "string" ? scope.split(" ").filter(Boolean) : [],
    expiresAt: new Date(exp * 1000),
  };
}

function stringClaim(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}

/** Maps jose errors to stable codes, without copying the token or claim values into messages. */
function toVerificationError(error: unknown): TokenVerificationError {
  const cause = { cause: error };
  if (error instanceof errors.JWTExpired) {
    return new TokenVerificationError("token_expired", "Access token has expired", cause);
  }
  if (error instanceof errors.JWTClaimValidationFailed) {
    switch (error.claim) {
      case "iss":
        return new TokenVerificationError(
          "invalid_issuer",
          "Access token issuer is not trusted",
          cause,
        );
      case "aud":
        return new TokenVerificationError(
          "invalid_audience",
          "Access token is not meant for this API",
          cause,
        );
      case "nbf":
        return new TokenVerificationError(
          "token_not_yet_valid",
          "Access token is not valid yet",
          cause,
        );
      default:
        return new TokenVerificationError(
          "missing_claim",
          `Access token claim "${error.claim}" is ${error.reason}`,
          cause,
        );
    }
  }
  if (
    error instanceof errors.JWSSignatureVerificationFailed ||
    error instanceof errors.JWKSNoMatchingKey ||
    error instanceof errors.JWKSMultipleMatchingKeys ||
    error instanceof errors.JOSEAlgNotAllowed
  ) {
    return new TokenVerificationError(
      "invalid_signature",
      "Access token signature is not valid",
      cause,
    );
  }
  if (
    error instanceof errors.JWSInvalid ||
    error instanceof errors.JWTInvalid ||
    error instanceof errors.JOSENotSupported ||
    error instanceof errors.JWKInvalid
  ) {
    return new TokenVerificationError("malformed_token", "Access token is malformed", cause);
  }
  // What is left comes from fetching the keys: timeout, invalid key set, HTTP error from Keycloak
  // (jose's generic error) or a network error.
  return new TokenVerificationError(
    "jwks_unavailable",
    "Realm signing keys are unavailable",
    cause,
  );
}
