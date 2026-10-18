/** Why a token was refused. Stable values: services may log them and tests assert them. */
export type TokenErrorCode =
  | "missing_token"
  | "malformed_token"
  | "invalid_signature"
  | "token_expired"
  | "token_not_yet_valid"
  | "invalid_issuer"
  | "invalid_audience"
  | "invalid_token_type"
  | "token_lifetime_too_long"
  | "missing_claim"
  | "missing_tenant"
  | "missing_roles"
  | "jwks_unavailable";

/**
 * A token was refused. The message explains why in English for logs; it never contains the
 * token or any claim value, so it is safe to log (personal data and tokens are never logged).
 */
export class TokenVerificationError extends Error {
  override readonly name = "TokenVerificationError";
  readonly code: TokenErrorCode;
  /** HTTP status to answer: 401, or 503 when the realm's signing keys cannot be fetched. */
  readonly status: 401 | 503;

  constructor(code: TokenErrorCode, message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.code = code;
    this.status = code === "jwks_unavailable" ? 503 : 401;
  }
}

/**
 * `WWW-Authenticate` header value for a refused request (RFC 6750 section 3). A request without
 * a token gets no error code, as the RFC asks.
 */
export function wwwAuthenticate(error: TokenVerificationError, realm = "kuizi"): string {
  if (error.code === "missing_token") {
    return `Bearer realm="${realm}"`;
  }
  if (error.status === 503) {
    return `Bearer realm="${realm}", error="temporarily_unavailable"`;
  }
  return `Bearer realm="${realm}", error="invalid_token", error_description="${error.code}"`;
}
