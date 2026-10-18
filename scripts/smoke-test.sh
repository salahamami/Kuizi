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
