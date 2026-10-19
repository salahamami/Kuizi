package kuizi.keycloak.pwned;

import org.keycloak.Config;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;
import org.keycloak.policy.PasswordPolicyProvider;
import org.keycloak.policy.PasswordPolicyProviderFactory;

/**
 * Registers the {@code pwnedPassword} password policy. The realm sets it in its password policy
 * string, for example {@code length(12) and pwnedPassword(1)}; the value is the minimum number of
 * breaches that rejects a password.
 *
 * <p>Server settings (SPI options, all optional):
 *
 * <ul>
 *   <li>{@code KC_SPI_PASSWORD_POLICY_PWNED_PASSWORD_API_URL}: range API base URL (default
 *       {@value PwnedPasswordSettings#DEFAULT_API_URL})
 *   <li>{@code KC_SPI_PASSWORD_POLICY_PWNED_PASSWORD_TIMEOUT_MS}: timeout in milliseconds (default
 *       {@value PwnedPasswordSettings#DEFAULT_TIMEOUT_MILLIS})
 *   <li>{@code KC_SPI_PASSWORD_POLICY_PWNED_PASSWORD_FAIL_CLOSED}: reject passwords while the API
 *       cannot be reached (default false)
 * </ul>
 */
public final class PwnedPasswordPolicyProviderFactory implements PasswordPolicyProviderFactory {

  public static final String ID = "pwnedPassword";

  private PwnedPasswordSettings settings = PwnedPasswordSettings.defaults();

  @Override
  public String getId() {
    return ID;
  }

  @Override
  public String getDisplayName() {
    return "Not in Have I Been Pwned (minimum breaches)";
  }

  @Override
  public String getConfigType() {
    return PasswordPolicyProvider.INT_CONFIG_TYPE;
  }

  @Override
  public String getDefaultConfigValue() {
    return String.valueOf(PwnedPasswordPolicyProvider.DEFAULT_MIN_BREACHES);
  }

  @Override
  public boolean isMultiplSupported() {
    return false;
  }

  @Override
  public void init(Config.Scope config) {
    settings =
        new PwnedPasswordSettings(
            config.get("apiUrl", PwnedPasswordSettings.DEFAULT_API_URL),
            config.getInt("timeoutMs", PwnedPasswordSettings.DEFAULT_TIMEOUT_MILLIS),
            config.getBoolean("failClosed", false));
  }

  @Override
  public void postInit(KeycloakSessionFactory factory) {}

  @Override
  public PasswordPolicyProvider create(KeycloakSession session) {
    return new PwnedPasswordPolicyProvider(session, settings);
  }

  @Override
  public void close() {}

  PwnedPasswordSettings settings() {
    return settings;
  }
}
