from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))  # assistant_fakes (unique name across the workspace)

from assistant_fakes import World, world

from jane_kit.contracts import contracts_dir

CONTRACTS = contracts_dir(Path(__file__).parent)


@pytest.fixture(scope="session")
def contracts() -> Path:
    if CONTRACTS is None or not (CONTRACTS / "openapi" / "assistant.v1.yaml").is_file():
        pytest.skip("contracts/ (WP-00) not available")
    return CONTRACTS


@pytest.fixture
def w(contracts: Path) -> Iterator[World]:
    with world(contracts) as wd:
        yield wd
        assert wd.violations() == [], "contract violations of neighbour calls"
