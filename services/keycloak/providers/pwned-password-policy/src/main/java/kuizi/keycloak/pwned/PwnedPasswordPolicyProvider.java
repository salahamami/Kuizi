package kuizi.keycloak.pwned;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.util.EntityUtils;
import org.jboss.logging.Logger;
import org.keycloak.connections.httpclient.HttpClientProvider;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;
import org.keycloak.policy.PasswordPolicyConfigException;
import org.keycloak.policy.PasswordPolicyProvider;
import org.keycloak.policy.PolicyError;

/**
 * Password policy {@code pwnedPassword(N)}: rejects a password that appears at least N times in
 * Have I Been Pwned. Only the first 5 characters of its SHA-1 hash leave Keycloak.
 *
 * <p>Nothing about the password (not the password, its hash or the prefix) is ever logged.
 */
public final class PwnedPasswordPolicyProvider implements PasswordPolicyProvider {

  /** Message keys, translated in theme-resources/messages (fr, ar, en). */
  static final String ERROR_BREACHED = "invalidPasswordPwnedMessage";

  static final String ERROR_UNAVAILABLE = "invalidPasswordPwnedUnavailableMessage";

  static final int DEFAULT_MIN_BREACHES = 1;

  private static final Logger LOG = Logger.getLogger(PwnedPasswordPolicyProvider.class);
  private static final String USER_AGENT = "kuizi-keycloak-pwned-password-policy";

  private final KeycloakSession session;
  private final PwnedPasswordSettings settings;
  private final PwnedPasswordChecker checker;

  PwnedPasswordPolicyProvider(KeycloakSession session, PwnedPasswordSettings settings) {
    this(session, settings, null);
  }

  /** Visible for tests: a custom checker replaces the HTTP call to the range API. */
  PwnedPasswordPolicyProvider(
      KeycloakSession session, PwnedPasswordSettings settings, PwnedPasswordChecker checker) {
    this.session = session;
    this.settings = settings;
    this.checker = checker != null ? checker : new PwnedPasswordChecker(this::fetchRange);
  }

  @Override
  public PolicyError validate(RealmModel realm, UserModel user, String password) {
    return check(minBreaches(realm), password);
  }

  @Override
  public PolicyError validate(String username, String password) {
    RealmModel realm = session == null ? null : session.getContext().getRealm();
    return check(minBreaches(realm), password);
  }

  @Override
  public Object parseConfig(String value) {
    Integer minBreaches = parseInteger(value, DEFAULT_MIN_BREACHES);
    if (minBreaches < 1) {
      throw new PasswordPolicyConfigException("pwnedPassword needs a minimum breach count of at least 1");
    }
    return minBreaches;
  }

  @Override
  public void close() {}

  PolicyError check(int minBreaches, String password) {
    if (password == null || password.isEmpty()) {
      return null; // the length policy reports empty passwords
    }
    try {
      return checker.breachCount(password) >= minBreaches ? new PolicyError(ERROR_BREACHED) : null;
    } catch (IOException | RuntimeException e) {
      String reason =
          e instanceof RangeUnavailableException ? e.getMessage() : e.getClass().getSimpleName();
      if (settings.failClosed()) {
        LOG.warnf("Pwned-password check unavailable (%s): password rejected (fail-closed)", reason);
        return new PolicyError(ERROR_UNAVAILABLE);
      }
      LOG.warnf("Pwned-password check unavailable (%s): password accepted on the other policies", reason);
      return null;
    }
  }

  private int minBreaches(RealmModel realm) {
    if (realm == null || realm.getPasswordPolicy() == null) {
      return DEFAULT_MIN_BREACHES;
    }
    Integer configured =
        realm.getPasswordPolicy().getPolicyConfig(PwnedPasswordPolicyProviderFactory.ID);
    return configured == null ? DEFAULT_MIN_BREACHES : configured;
  }

  /** Calls the range API through Keycloak's HTTP client, so proxy and truststore settings apply. */
  private String fetchRange(String prefix) throws IOException {
    HttpGet get = new HttpGet(settings.apiUrl() + prefix);
    get.setHeader("Add-Padding", "true"); // fake entries hide the real response size
    get.setHeader("User-Agent", USER_AGENT);
    int timeout = settings.timeoutMillis();
    get.setConfig(
        RequestConfig.custom()
            .setConnectTimeout(timeout)
            .setConnectionRequestTimeout(timeout)
            .setSocketTimeout(timeout)
            .build());
    var http = session.getProvider(HttpClientProvider.class).getHttpClient();
    try (CloseableHttpResponse response = http.execute(get)) {
      int status = response.getStatusLine().getStatusCode();
      if (status != 200) {
        EntityUtils.consumeQuietly(response.getEntity());
        throw new RangeUnavailableException("range API answered HTTP " + status);
      }
      return EntityUtils.toString(response.getEntity(), StandardCharsets.UTF_8);
    }
  }

  /** The range API answered, but not with a usable result. The message is safe to log. */
  static final class RangeUnavailableException extends IOException {
    RangeUnavailableException(String message) {
      super(message);
    }
  }
}
