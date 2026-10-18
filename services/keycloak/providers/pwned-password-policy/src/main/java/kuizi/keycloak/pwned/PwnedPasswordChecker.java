package kuizi.keycloak.pwned;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Objects;

/**
 * Counts how often a password appears in Have I Been Pwned, with the k-anonymity range API.
 *
 * <p>Only the first {@value #PREFIX_LENGTH} hexadecimal characters of the password's SHA-1 hash
 * are sent to the range API. The API answers with every known hash suffix that shares this
 * prefix (several hundred, padded with fake zero-count entries), and the comparison with the
 * rest of the hash happens here. Neither the password nor its full hash ever leaves Keycloak.
 */
public final class PwnedPasswordChecker {

  /** Number of hash characters sent to the range API (fixed by the HIBP API). */
  public static final int PREFIX_LENGTH = 5;

  /** Fetches the range API response for one 5-character, upper-case SHA-1 prefix. */
  @FunctionalInterface
  public interface RangeClient {
    String fetchRange(String prefix) throws IOException;
  }

  private final RangeClient client;

  public PwnedPasswordChecker(RangeClient client) {
    this.client = Objects.requireNonNull(client, "client");
  }

  /**
   * Returns the number of breaches the password appears in, or 0 if it is not known.
   *
   * @throws IOException if the range API cannot be reached or answers with an error
   */
  public long breachCount(String password) throws IOException {
    String hash = sha1Hex(password);
    String prefix = hash.substring(0, PREFIX_LENGTH);
    String suffix = hash.substring(PREFIX_LENGTH);
    return countForSuffix(client.fetchRange(prefix), suffix);
  }

  /** Upper-case hexadecimal SHA-1 of the UTF-8 password, as the HIBP API expects. */
  static String sha1Hex(String password) {
    try {
      MessageDigest sha1 = MessageDigest.getInstance("SHA-1");
      byte[] digest = sha1.digest(password.getBytes(StandardCharsets.UTF_8));
      return HexFormat.of().withUpperCase().formatHex(digest);
    } catch (NoSuchAlgorithmException e) {
      throw new IllegalStateException("SHA-1 is required by every Java runtime", e);
    }
  }

  /**
   * Finds the suffix in a range API response ({@code SUFFIX:COUNT} per line) and returns its
   * count. Padding entries have a count of 0, so they never count as a breach.
   */
  static long countForSuffix(String body, String suffix) {
    if (body == null) {
      return 0;
    }
    for (String line : body.split("\\r?\\n")) {
      int colon = line.indexOf(':');
      if (colon <= 0 || !line.substring(0, colon).trim().equalsIgnoreCase(suffix)) {
        continue;
      }
      try {
        return Math.max(0, Long.parseLong(line.substring(colon + 1).trim()));
      } catch (NumberFormatException e) {
        return 0;
      }
    }
    return 0;
  }
}
