# Temporary CI canary (T006): built from the repository root like every service image.
FROM gcr.io/distroless/static-debian13:nonroot@sha256:e2e927ec666bae08560abb3c55d0659eceabb657f56b6782ab500a9fc7f555e3
COPY services/ci-canary/src/grade.ts /app/grade.ts
USER nonroot
