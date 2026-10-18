# CI container fixture

A minimal image (distroless static, Debian 13, pinned by digest) that CI builds, describes with a Syft SBOM and scans with Trivy on every branch and pull request, so the container workflow is proven before the first Kuizi service has a Dockerfile. It is never pushed to a registry. See [`docs/dev/ci.md`](../../../docs/dev/ci.md).
