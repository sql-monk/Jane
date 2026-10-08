"""Outbound address policy (SSRF guard): link-local/metadata denied by default, private ranges optional,
checked after DNS resolution for every connection, including every redirect hop.

The collector is the real app or the real fetcher with the real guarded transport; only DNS answers are
replaced (a resolver function) where a test needs a name that resolves to a chosen address.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import httpcore
import httpx
import pytest
from fastapi.testclient import TestClient

from jane_web_collector.app import build_app
from jane_web_collector.egress import EgressPolicy, GuardedBackend, GuardedTransport
from jane_web_collector.fetcher import Fetcher, FetchError
from jane_web_collector.host_limits import HostLimiter
from jane_web_collector.settings import Rate, Retries, ServiceLimits, Settings
from jane_web_collector.testing import FAST_LIMITS, Site, drain, errors, make_settings, start, wait_done

METADATA_URL = "http://169.254.169.254/latest/meta-data/"
OWNER_POLICY = {
    "mode": "owner_policy",
    "owner_policy": {"confirmed_owner": True, "justification": "Our own test site, owner allows it."},
}


@pytest.mark.parametrize(
    ("address", "default", "with_private"),
    [
        ("169.254.169.254", "denied", "denied"),
        ("169.254.0.1", "denied", "denied"),
        ("fe80::1", "denied", "denied"),
        ("fd00:ec2::254", "denied", "denied"),
        ("::ffff:169.254.169.254", "denied", "denied"),  # IPv4-mapped
        ("64:ff9b::a9fe:a9fe", "denied", "denied"),  # NAT64 of 169.254.169.254
        ("127.0.0.1", "allowed", "denied"),
        ("::1", "allowed", "denied"),
        ("10.1.2.3", "allowed", "denied"),
        ("172.18.0.5", "allowed", "denied"),  # a Docker network
        ("192.168.1.10", "allowed", "denied"),
        ("100.64.0.1", "allowed", "denied"),
        ("0.0.0.0", "allowed", "denied"),
        ("fd12:3456::1", "allowed", "denied"),
        ("::ffff:10.0.0.1", "allowed", "denied"),
        ("93.184.215.14", "allowed", "allowed"),
        ("2606:2800:21f:cb07:6820:80da:af6b:8b2c", "allowed", "allowed"),
    ],
)
def test_policy_classifies_addresses(address: str, default: str, with_private: str) -> None:
    def verdict(policy: EgressPolicy) -> str:
        return "allowed" if policy.reason(address) is None else "denied"

    assert verdict(EgressPolicy()) == default
    assert verdict(EgressPolicy(deny_private=True)) == with_private
    assert verdict(EgressPolicy(deny_link_local=False)) == "allowed"


def test_policy_comes_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    assert Settings().egress_policy() == EgressPolicy(deny_link_local=True, deny_private=False)
    monkeypatch.setenv("JANE_WEB_COLLECTOR_EGRESS_DENY_PRIVATE", "true")
    monkeypatch.setenv("JANE_WEB_COLLECTOR_EGRESS_DENY_LINK_LOCAL", "false")
    assert Settings().egress_policy() == EgressPolicy(deny_link_local=False, deny_private=True)


# ---------------------------------------------------------------- fetcher with the guarded transport


class RecordingBackend(httpcore.AnyIOBackend):
    """The real network backend that remembers which addresses it was asked to connect to."""

    def __init__(self) -> None:
        self.connected: list[str] = []

    async def connect_tcp(
        self, host: str, port: int, *args: Any, **kwargs: Any
    ) -> httpcore.AsyncNetworkStream:
        self.connected.append(host)
        return await super().connect_tcp(host, port, *args, **kwargs)


def fake_dns(answers: dict[str, list[str]]) -> Any:
    async def resolve(host: str, port: int) -> list[str]:
        if host not in answers:
            raise OSError(f"unknown host {host}")
        return answers[host]

    return resolve


LIMITS = ServiceLimits(
    rate=Rate(requests_per_second_per_host=1000, min_delay_ms_per_host=0),
    retries=Retries(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0),
)


async def test_dns_answer_is_checked_and_the_checked_address_is_used(site: Site) -> None:
    port = int(site.base.rsplit(":", 1)[1])
    dns = fake_dns(
        {
            "metadata.example.test": ["169.254.169.254"],
            "mixed.example.test": ["127.0.0.1", "169.254.169.254"],  # one forbidden address is enough
            "shop.example.test": ["127.0.0.1"],
        }
    )
    inner = RecordingBackend()
    transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(), resolver=dns, inner=inner))
    async with httpx.AsyncClient(transport=transport, follow_redirects=False) as client:
        fetcher = Fetcher(client, LIMITS, HostLimiter(LIMITS).session(LIMITS), user_agent="JaneBot")
        for host in ("metadata.example.test", "mixed.example.test"):
            with pytest.raises(FetchError) as denied:
                await fetcher.get(f"http://{host}:{port}/about")
            assert denied.value.code == "access_denied_by_policy"
            assert "169.254.169.254" in denied.value.message and "egress policy" in denied.value.message
            assert denied.value.attempts == 1  # a policy decision is not retried
        assert inner.connected == []  # nothing was opened towards a denied host
        # the name exists only in the fake DNS: the connection goes to the address that was checked
        ok = await fetcher.get(f"http://shop.example.test:{port}/about")
        assert ok.status == 200 and site.requests["/about"] == 1
        assert inner.connected == ["127.0.0.1"]


async def test_private_addresses_after_real_dns_resolution_when_enabled(site: Site) -> None:
    port = int(site.base.rsplit(":", 1)[1])
    transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(deny_private=True)))
    async with httpx.AsyncClient(transport=transport, follow_redirects=False) as client:
        fetcher = Fetcher(client, LIMITS, HostLimiter(LIMITS).session(LIMITS), user_agent="JaneBot")
        with pytest.raises(FetchError) as denied:
            await fetcher.get(f"http://localhost:{port}/about")  # "localhost" resolves to loopback
        assert denied.value.code == "access_denied_by_policy"
    assert site.requests["/about"] == 0


# ---------------------------------------------------------------- the service: POST /v1/fetches, collections


class Redirector:
    """A source on 127.0.0.1 whose every page redirects to ``target`` (the classic SSRF via redirect)."""

    def __init__(self, target: str) -> None:
        self.requests: list[str] = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                owner.requests.append(self.path)
                self.send_response(302)
                self.send_header("Location", target)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, format: str, *args: Any) -> None:
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, args=(0.05,), daemon=True)
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def redirector() -> Iterator[Redirector]:
    r = Redirector(METADATA_URL)
    yield r
    r.close()


def owner_rules(seed: str) -> dict[str, Any]:
    """Rules that allow the metadata host by scope and skip robots.txt: only the egress policy can stop it."""
    return {
        "collector": "web",
        "scope": {"allowed_domains": ["127.0.0.1", "169.254.169.254"]},
        "strategies": [{"type": "seed_list", "urls": [seed]}],
        "robots": OWNER_POLICY,
    }


def test_fetch_of_metadata_address_is_denied(client: TestClient) -> None:
    r = client.post(
        "/v1/fetches",
        json={"source_kind": "web", "url": METADATA_URL, "rules": owner_rules(METADATA_URL)},
    )
    assert r.status_code == 403, r.text
    problem = r.json()
    assert problem["code"] == "access_denied_by_policy" and "egress policy" in problem["detail"]
    # without rules robots.txt of the address is needed first, and it is denied as well
    plain = client.post("/v1/fetches", json={"source_kind": "web", "url": METADATA_URL})
    assert plain.status_code == 403 and plain.json()["code"] == "access_denied_by_policy"


def test_fetch_redirect_to_metadata_address_is_denied(client: TestClient, redirector: Redirector) -> None:
    url = redirector.base + "/start"
    r = client.post("/v1/fetches", json={"source_kind": "web", "url": url, "rules": owner_rules(url)})
    assert r.status_code == 403, r.text
    assert r.json()["code"] == "access_denied_by_policy"
    assert "169.254.169.254" in r.json()["detail"] and "egress policy" in r.json()["detail"]
    assert redirector.requests == ["/start"]  # the first hop was allowed, the redirect target was not


def test_collection_redirect_to_metadata_address_is_denied(
    client: TestClient, redirector: Redirector
) -> None:
    url = redirector.base + "/start"
    cid = start(client, {"source_kind": "web", "rules": owner_rules(url), "limits": FAST_LIMITS})
    assert drain(client, cid) == []
    assert wait_done(client, cid)["status"] == "succeeded"
    denied = [e for e in errors(client, cid) if e["code"] == "access_denied_by_policy"]
    assert len(denied) == 1 and denied[0]["url"].startswith(redirector.base)
    assert "169.254.169.254" in denied[0]["message"] and "egress policy" in denied[0]["message"]
    assert redirector.requests == ["/start"]


def test_private_ranges_are_optional(tmp_path: Path, site: Site) -> None:
    url = site.url("/about")
    body = {
        "source_kind": "web",
        "url": url,
        "rules": {**owner_rules(url), "scope": {"allowed_domains": [site.host]}},
    }
    with TestClient(build_app(make_settings(tmp_path / "a"))) as default:
        assert default.post("/v1/fetches", json=body).status_code == 200  # dev/e2e: the site is private
    assert site.requests["/about"] == 1
    site.reset()
    with TestClient(build_app(make_settings(tmp_path / "b", egress_deny_private=True))) as strict:
        r = strict.post("/v1/fetches", json=body)
        assert r.status_code == 403 and r.json()["code"] == "access_denied_by_policy"
        assert "127.0.0.1" in r.json()["detail"] and "egress policy" in r.json()["detail"]
        plain = strict.post("/v1/fetches", json={"source_kind": "web", "url": url})  # robots.txt first
        assert plain.status_code == 403 and plain.json()["code"] == "access_denied_by_policy"
    assert site.requests["/about"] == 0 and site.requests["/robots.txt"] == 0
