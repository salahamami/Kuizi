# CI fixture (T006): a minimal image that keeps the container workflow honest (build, Syft SBOM,
# Trivy gate on CRITICAL) while Kuizi has no service image yet. CI builds and scans it on every
# branch and pull request and never publishes it (scripts/ci/discover.py, docs/dev/ci.md).
# NEGATIVE TEST: Alpine 3.12.0 has CRITICAL CVEs, the Trivy gate must fail.
FROM alpine:3.12.0@sha256:185518070891758909c9f839cf4ca393ee977ac378609f700f60a771a2dfe321
COPY README.md /kuizi/README.md
USER nonroot
