#!/usr/bin/env bash
# Smoke test of the local stack (T237): writes and reads real data in every service.
# Usage: make smoke   (the stack must be running: make up)
set -uo pipefail

cd "$(dirname "$0")/.."
COMPOSE=(docker compose -f infra/local/compose.yaml --env-file .env)
set -a; . ./.env; set +a

failures=0
check() {
  local name="$1"; shift
  if out=$("$@" 2>&1); then
    printf '  ok    %s\n' "$name"
  else
    printf '  FAIL  %s\n%s\n' "$name" "$(printf '%s' "$out" | tail -5 | sed 's/^/        /')"
    failures=$((failures + 1))
  fi
}

echo "Kuizi local stack smoke test"

check "PostgreSQL: pgvector distance query" \
  "${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
  "SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector"

check "PostgreSQL: Keycloak database exists" \
  "${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
  "SELECT 1 FROM pg_database WHERE datname = 'keycloak'"

check "Kafka: produce and consume one event" bash -c "
  ${COMPOSE[*]} exec -T redpanda rpk topic create smoke.test -p 1 >/dev/null 2>&1 || true
  echo '{\"event\":\"smoke\"}' | ${COMPOSE[*]} exec -T redpanda rpk topic produce smoke.test >/dev/null &&
  ${COMPOSE[*]} exec -T redpanda rpk topic consume smoke.test -n 1 -o start | grep -q smoke"

check "Schema registry answers" \
  "${COMPOSE[@]}" exec -T redpanda curl -sf http://localhost:8081/subjects

check "Redis: set and get" bash -c "
  ${COMPOSE[*]} exec -T redis redis-cli set kuizi:smoke ok >/dev/null &&
  ${COMPOSE[*]} exec -T redis redis-cli get kuizi:smoke | grep -q ok"

check "S3: buckets exist" bash -c "
  echo 's3.bucket.list' | ${COMPOSE[*]} exec -T seaweedfs weed shell -master=localhost:9333 2>/dev/null |
  grep -q '$S3_BUCKET_MEDIA' "

check "S3: signed upload and download with the local credentials" bash -c "
  echo ok > /tmp/kuizi-smoke.txt &&
  curl -sf --aws-sigv4 'aws:amz:$AWS_REGION:s3' --user '$S3_ACCESS_KEY_ID:$S3_SECRET_ACCESS_KEY' \
    -T /tmp/kuizi-smoke.txt '$S3_ENDPOINT_URL/$S3_BUCKET_MEDIA/smoke.txt' &&
  curl -sf --aws-sigv4 'aws:amz:$AWS_REGION:s3' --user '$S3_ACCESS_KEY_ID:$S3_SECRET_ACCESS_KEY' \
    '$S3_ENDPOINT_URL/$S3_BUCKET_MEDIA/smoke.txt' | grep -q ok"

check "S3: unsigned requests are refused" bash -c "
  ! curl -sf '$S3_ENDPOINT_URL/$S3_BUCKET_MEDIA/smoke.txt' >/dev/null"

check "Keycloak: realm '$KEYCLOAK_REALM' publishes its OpenID configuration" \
  curl -sf "$KEYCLOAK_URL/realms/$KEYCLOAK_REALM/.well-known/openid-configuration"

# T012: a synthetic dev user gets a 15-minute access token with the tenant_id and roles claims.
keycloak_dev_token() {
  curl -sf -d client_id=kuizi-dev-cli -d grant_type=password -d scope=openid \
    -d username=dev-student -d password=dev-student-local-only \
    "$KEYCLOAK_URL/realms/$KEYCLOAK_REALM/protocol/openid-connect/token" |
  python3 -c '
import base64, json, sys
token = json.load(sys.stdin)
part = token["access_token"].split(".")[1]
claims = json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
assert claims["exp"] - claims["iat"] == 900, "access token should live 900 s"
assert claims.get("tenant_id") == "demo-school-a", "tenant_id claim missing"
assert claims.get("roles") == ["student"], "roles claim missing"
'
}
check "Keycloak: dev user token has tenant_id and roles, lives 15 min" keycloak_dev_token

# T012: the login page in Arabic is right to left.
keycloak_login_rtl() {
  curl -sf "$KEYCLOAK_URL/realms/$KEYCLOAK_REALM/protocol/openid-connect/auth?client_id=kuizi-web&response_type=code&scope=openid&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&code_challenge_method=S256&ui_locales=ar" |
  grep -q '<html[^>]*dir="rtl"'
}
check "Keycloak: Arabic login page is right to left" keycloak_login_rtl

check "MLflow: log a run" \
  "${COMPOSE[@]}" exec -T mlflow python -c "
import mlflow
mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment('smoke-test')
with mlflow.start_run():
    mlflow.log_metric('auc', 0.5)
"

if [ -n "$("${COMPOSE[@]}" ps -q litellm 2>/dev/null)" ]; then
  check "LiteLLM gateway answers" curl -sf "$LITELLM_URL/health/liveliness"
fi

echo
if [ "$failures" -eq 0 ]; then
  echo "All checks passed."
else
  echo "$failures check(s) failed. Try: make logs"
  exit 1
fi
