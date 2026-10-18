import { TokenVerificationError } from "./errors.js";

/**
 * Extracts the token from an `Authorization: Bearer <token>` header (RFC 6750). Throws
 * `missing_token` when the header is absent or uses another scheme.
 */
export function bearerToken(authorization: string | undefined | null): string {
  const match = /^Bearer[ ]+([A-Za-z0-9\-._~+/]+=*)\s*$/i.exec(authorization ?? "");
  if (!match?.[1]) {
    throw new TokenVerificationError(
      "missing_token",
      "No bearer token in the Authorization header",
    );
  }
  return match[1];
}
