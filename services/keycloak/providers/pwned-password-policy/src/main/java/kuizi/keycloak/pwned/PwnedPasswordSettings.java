package kuizi.keycloak.pwned;

import java.net.URI;

/**
 * Server-wide settings of the pwned-password policy, read once from the Keycloak SPI
 * configuration (for example {@code KC_SPI_PASSWORD_POLICY_PWNED_PASSWORD_API_URL}).
 *
 * @param apiUrl range API base URL; the 5-character prefix is appended to it
 * @param timeoutMillis connect and read timeout for one range request
 * @param failClosed when the range API cannot be reached: reject the password (true) or accept
 *     it with the other policies only and log a warning (false, the default)
 */
public record PwnedPasswordSettings(String apiUrl, int timeoutMillis, boolean failClosed) {

  public static final String DEFAULT_API_URL = "https://api.pwnedpasswords.com/range/";
  public static final int DEFAULT_TIMEOUT_MILLIS = 2000;

  public PwnedPasswordSettings {
    if (apiUrl == null || apiUrl.isBlank()) {
      apiUrl = DEFAULT_API_URL;
    }
    String scheme = URI.create(apiUrl).getScheme();
    if (!"https".equals(scheme) && !"http".equals(scheme)) {
      throw new IllegalArgumentException("api-url must be an http or https URL");
    }
    if (!apiUrl.endsWith("/")) {
      apiUrl = apiUrl + "/";
    }
    if (timeoutMillis <= 0) {
      timeoutMillis = DEFAULT_TIMEOUT_MILLIS;
    }
  }

  public static PwnedPasswordSettings defaults() {
    return new PwnedPasswordSettings(DEFAULT_API_URL, DEFAULT_TIMEOUT_MILLIS, false);
  }
}
