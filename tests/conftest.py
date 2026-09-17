from __future__ import annotations

import pytest

from skyrim_wayfinder.data import load_canonical_content
from skyrim_wayfinder.persistence import StateRepository
from skyrim_wayfinder.services import WayfinderService


@pytest.fixture
def content():
    return load_canonical_content()


@pytest.fixture
def service(content):
    repository = StateRepository(":memory:", content.fingerprint)
    result = WayfinderService(content, repository)
    yield result
    repository.close()
