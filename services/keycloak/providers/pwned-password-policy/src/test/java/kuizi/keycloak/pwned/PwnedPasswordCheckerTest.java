package kuizi.keycloak.pwned;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.keycloak.policy.PasswordPolicyConfigException;
import org.keycloak.policy.PolicyError;

class PwnedPasswordCheckerTest {

  // SHA-1("password") = 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8 (well-known test vector).
  private static final String PASSWORD_PREFIX = "5BAA6";
  private static final String PASSWORD_SUFFIX = "1E4C9B93F3F0682250B6CF8331B7EE68FD8";

  /** Records every prefix sent to the "range API" and answers with a fixed body. */
  private static final class RecordingClient implements PwnedPasswordChecker.RangeClient {
    final List<String> prefixes = new ArrayList<>();
    final String body;

    RecordingClient(String body) {
      this.body = body;
    }

    @Override
    public String fetchRange(String prefix) {
      prefixes.add(prefix);
      return body;
    }
  }

  @Test
  void sha1IsUpperCaseHexOfUtf8() {
    assertEquals(PASSWORD_PREFIX + PASSWORD_SUFFIX, PwnedPasswordChecker.sha1Hex("password"));
    // Non-ASCII passwords are hashed as UTF-8, like the HIBP corpus (Arabic and French accents).
    assertEquals(40, PwnedPasswordChecker.sha1Hex("كلمةالسرّ-été").length());
  }

  @Test
  void onlyTheFiveCharacterPrefixLeavesTheServer() throws IOException {
    RecordingClient client = new RecordingClient("");
    new PwnedPasswordChecker(client).breachCount("password");
    assertEquals(List.of(PASSWORD_PREFIX), client.prefixes);
    assertEquals(PwnedPasswordChecker.PREFIX_LENGTH, client.prefixes.get(0).length());
  }

  @Test
  void findsTheSuffixAndItsCount() throws IOException {
    String body = "0018A45C4D1DEF81644B54AB7F969B88D65:1\r\n"
        + PASSWORD_SUFFIX + ":10434004\r\n"
        + "011053FD0102E94D6AE2F8B83D76FAF94F6:13\r\n";
    assertEquals(10434004, new PwnedPasswordChecker(new RecordingClient(body)).breachCount("password"));
  }

  @Test
  void suffixComparisonIgnoresCase() {
    assertEquals(7, PwnedPasswordChecker.countForSuffix(PASSWORD_SUFFIX.toLowerCase() + ":7", PASSWORD_SUFFIX));
  }

  @Test
  void paddingEntriesAndUnknownSuffixesCountAsZero() throws IOException {
    String padded = PASSWORD_SUFFIX + ":0\n0018A45C4D1DEF81644B54AB7F969B88D65:3\n";
    assertEquals(0, new PwnedPasswordChecker(new RecordingClient(padded)).breachCount("password"));
    assertEquals(0, new PwnedPasswordChecker(new RecordingClient("ABC:5\n")).breachCount("password"));
  }

  @Test
  void malformedLinesAreIgnored() {
    String body = "garbage\n:12\n" + PASSWORD_SUFFIX + ":not-a-number\n";
    assertEquals(0, PwnedPasswordChecker.countForSuffix(body, PASSWORD_SUFFIX));
    assertEquals(0, PwnedPasswordChecker.countForSuffix(null, PASSWORD_SUFFIX));
  }

  @Test
  void providerRejectsBreachedPasswordsAtTheThreshold() {
    PwnedPasswordChecker checker = new PwnedPasswordChecker(new RecordingClient(PASSWORD_SUFFIX + ":3"));
    PwnedPasswordPolicyProvider provider =
        new PwnedPasswordPolicyProvider(null, PwnedPasswordSettings.defaults(), checker);

    PolicyError error = provider.check(1, "password");
    assertNotNull(error);
    assertEquals(PwnedPasswordPolicyProvider.ERROR_BREACHED, error.getMessage());
    assertNotNull(provider.check(3, "password"));
    assertNull(provider.check(4, "password"), "3 breaches stay under a threshold of 4");
  }

  @Test
  void providerAcceptsUnknownPasswords() {
    PwnedPasswordChecker checker = new PwnedPasswordChecker(new RecordingClient("ABC:5"));
    PwnedPasswordPolicyProvider provider =
        new PwnedPasswordPolicyProvider(null, PwnedPasswordSettings.defaults(), checker);
    assertNull(provider.check(1, "a long and unusual passphrase"));
    assertNull(provider.check(1, ""), "empty passwords are left to the length policy");
  }

  @Test
  void unreachableApiFailsOpenByDefaultAndClosedWhenConfigured() {
    PwnedPasswordChecker down = new PwnedPasswordChecker(prefix -> {
      throw new IOException("connection refused");
    });
    PwnedPasswordPolicyProvider open =
        new PwnedPasswordPolicyProvider(null, PwnedPasswordSettings.defaults(), down);
    assertNull(open.check(1, "password"));

    PwnedPasswordSettings closedSettings =
        new PwnedPasswordSettings(PwnedPasswordSettings.DEFAULT_API_URL, 500, true);
    PwnedPasswordPolicyProvider closed = new PwnedPasswordPolicyProvider(null, closedSettings, down);
    PolicyError error = closed.check(1, "password");
    assertNotNull(error);
    assertEquals(PwnedPasswordPolicyProvider.ERROR_UNAVAILABLE, error.getMessage());
  }

  @Test
  void configMustBeAPositiveBreachCount() {
    PwnedPasswordPolicyProvider provider =
        new PwnedPasswordPolicyProvider(null, PwnedPasswordSettings.defaults(), new PwnedPasswordChecker(p -> ""));
    assertEquals(1, provider.parseConfig(null));
    assertEquals(5, provider.parseConfig("5"));
    assertThrows(PasswordPolicyConfigException.class, () -> provider.parseConfig("0"));
  }

  @Test
  void settingsNormaliseTheUrlAndRejectOtherSchemes() {
    assertTrue(new PwnedPasswordSettings("http://hibp-stub:8080/range", 0, false).apiUrl().endsWith("/range/"));
    assertEquals(PwnedPasswordSettings.DEFAULT_API_URL, new PwnedPasswordSettings("", 0, false).apiUrl());
    assertEquals(PwnedPasswordSettings.DEFAULT_TIMEOUT_MILLIS, new PwnedPasswordSettings(null, -1, false).timeoutMillis());
    assertThrows(IllegalArgumentException.class, () -> new PwnedPasswordSettings("file:///etc/passwd", 0, false));
  }
}
