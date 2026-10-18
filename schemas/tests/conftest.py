"""Shared fixtures. Tests marked `registry` use the local schema registry (make up) on throwaway
subjects that are deleted afterwards; they are skipped when it is not reachable, unless
KUIZI_REQUIRE_REGISTRY=1."""

from __future__ import annotations

import copy
import os
import uuid
from collections.abc import Iterator

import pytest
from kuizi_schemas import Paths
from kuizi_schemas.avsc import Sources, load_sources
from kuizi_schemas.catalogue import Catalogue, load_catalogue
from kuizi_schemas.registry import Registry, RegistryError, registry_url

from .fake_registry import FakeRegistry


@pytest.fixture(scope="session")
def paths() -> Paths:
    return Paths()


@pytest.fixture(scope="session")
def _catalogue(paths: Paths) -> Catalogue:
    return load_catalogue(paths.catalogue)


@pytest.fixture(scope="session")
def _sources(paths: Paths) -> Sources:
    return load_sources(paths.events)


@pytest.fixture
def catalogue(_catalogue: Catalogue) -> Catalogue:
    """A fresh copy each test, so a test may change it."""
    return copy.deepcopy(_catalogue)


@pytest.fixture
def sources(_sources: Sources) -> Sources:
    return copy.deepcopy(_sources)


@pytest.fixture(scope="session")
def live_registry(paths: Paths) -> Registry:
    try:
        registry = Registry(registry_url(paths.env_file))
        reachable = registry.reachable()
    except RegistryError:
        reachable = False
    if not reachable:
        if os.environ.get("KUIZI_REQUIRE_REGISTRY") == "1":
            pytest.fail("schema registry not reachable and KUIZI_REQUIRE_REGISTRY=1")
        pytest.skip("schema registry not reachable (start the stack with make up)")
    return registry


@pytest.fixture
def test_prefix(live_registry: Registry) -> Iterator[str]:
    """Unique subject prefix; every subject under it is deleted after the test."""
    prefix = f"t023-test-{uuid.uuid4().hex[:10]}."
    yield prefix
    for subject in live_registry.subjects():
        if subject.startswith(prefix):
            live_registry.delete_subject(subject)


@pytest.fixture
def fake_registry() -> Iterator[FakeRegistry]:
    with FakeRegistry() as fake:
        yield fake
