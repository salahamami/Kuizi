# Kuizi Keycloak image (T012): stock Keycloak plus Kuizi's providers and login theme.
# `make up` builds it the first time (docker compose), so the PC needs no Java or Maven.
# The same image moves to EKS with T240, where an optimised `kc.sh build` stage is added.
# Keep KEYCLOAK_VERSION in step with keycloak.version in providers/*/pom.xml.
ARG KEYCLOAK_VERSION=26.1.4
ARG MAVEN_IMAGE=maven:3.9.9-eclipse-temurin-21

FROM ${MAVEN_IMAGE} AS providers
WORKDIR /build/pwned-password-policy
COPY providers/pwned-password-policy/pom.xml .
RUN mvn -B -q dependency:go-offline
COPY providers/pwned-password-policy/src src
# Runs the unit tests: a failing test stops the image build.
RUN mvn -B -q package

FROM quay.io/keycloak/keycloak:${KEYCLOAK_VERSION}
COPY --from=providers /build/pwned-password-policy/target/kuizi-pwned-password-policy.jar /opt/keycloak/providers/
COPY themes/ /opt/keycloak/themes/
