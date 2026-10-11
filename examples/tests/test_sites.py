"""Sites of examples/sites (real catalogs, ads, news, Telegram): documents, manifests and package tests, no services."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SITES = Path(__file__).resolve().parents[1] / "sites"
sys.path.insert(0, str(SITES))

import setup_sites  # noqa: E402


@pytest.mark.parametrize("site", [p.stem for p in sorted((SITES / "sites").glob("*.json"))])
def test_site_documents_and_packages(site: str) -> None:
    problems = setup_sites.check_site(SITES / "sites" / f"{site}.json", setup_sites.package_dirs(), set())
    assert problems == []
