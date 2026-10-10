"""Package of examples/channels (posts of real Telegram channels): manifest tests, without services."""

from __future__ import annotations

from pathlib import Path

from jane_extractor_sdk.testing import assert_package_tests_pass

CHANNELS = Path(__file__).resolve().parents[1] / "channels" / "packages"


def test_telegram_posts_extractor_manifest_tests_pass() -> None:
    assert_package_tests_pass(CHANNELS / "channels.telegram-posts")
