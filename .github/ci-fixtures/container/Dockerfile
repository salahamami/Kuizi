# CI fixture (T006): a minimal image that keeps the container workflow honest (build, Syft SBOM,
# Trivy gate on CRITICAL) while Kuizi has no service image yet. CI builds and scans it on every
# branch and pull request and never publishes it (scripts/ci/discover.py, docs/dev/ci.md).
FROM gcr.io/distroless/static-debian13:nonroot@sha256:e2e927ec666bae08560abb3c55d0659eceabb657f56b6782ab500a9fc7f555e3
COPY README.md /kuizi/README.md
USER nonroot
