"""Point the dev stack's LLM gateway at the real Anthropic API (ADR-0006).

The key never passes through this script, the command line or a database: it is a single line in the
git-ignored ``.jane/secrets/anthropic_api_key`` (or ``JANE_SECRETS_DIR``), which ``infra/compose.yaml`` mounts
read-only into the llm container at ``/run/secrets``. Through llm.v1 this script stores in llm's database only
the connection with the reference ``file:/run/secrets/anthropic_api_key``, the ``anthropic`` provider with its
models and prices, the aliases ``default`` / ``strong`` / ``cheap`` and a platform budget. ``--check`` then
makes one short call through the gateway (a few tokens on the ``cheap`` alias).

    uv run --no-project python scripts/llm_anthropic.py --project <compose-project> [--check]

Stdlib only, like ``scripts/dev.py``; the stack must be up (``just up ... llm --project <compose-project>``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SECRET_NAME = "anthropic_api_key"  # noqa: S105 - a file name, not a secret
CONNECTION_ID = "anthropic-main"
PROVIDER_ID = "anthropic"

# Current models and first-party API prices per million tokens (USD).
MODELS: list[dict[str, Any]] = [
    {
        "model_id": "claude-opus-5-5",
        "max_context_tokens": 1_000_000,
        "supports_structured_output": True,
        "pricing": {"input_per_mtok": 4, "output_per_mtok": 20, "currency": "USD"},
    },
    {
        "model_id": "claude-sonnet-5-5",
        "max_context_tokens": 1_000_000,
        "supports_structured_output": True,
        "pricing": {"input_per_mtok": 2, "output_per_mtok": 10, "currency": "USD"},
    },
    {
        "model_id": "claude-haiku-5-5",
        "max_context_tokens": 1_000_000,
        "supports_structured_output": True,
        # Prompts up to 100K tokens; longer ones are billed at 0.50 / 2.50.
        "pricing": {"input_per_mtok": 0.1, "output_per_mtok": 0.5, "currency": "USD"},
    },
]
ALIASES = {"default": "claude-opus-5-5", "strong": "claude-opus-5-5", "cheap": "claude-haiku-5-5"}


def secrets_dir() -> Path:
    if env := os.environ.get("JANE_SECRETS_DIR"):
        return Path(env)
    return ROOT / ".jane" / "secrets"


def call(base: str, key: str, method: str, path: str, body: Any = None, *, timeout: float = 30) -> Any:
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if method == "POST":
        headers["Idempotency-Key"] = str(uuid.uuid4())
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)  # noqa: S310 - local stack URL
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - local stack URL
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise SystemExit(f"{method} {path} -> HTTP {exc.code}: {detail}") from None
    return json.loads(raw) if raw else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True, help="compose project of the running stack")
    ap.add_argument("--budget-usd-per-day", type=float, default=10.0, help="platform LLM budget (default 10)")
    ap.add_argument("--check", action="store_true", help="make one short test call on the cheap alias")
    ns = ap.parse_args(argv)

    secret = secrets_dir() / SECRET_NAME
    if not secret.is_file() or not secret.read_text(encoding="utf-8").strip():
        print(f"put the Anthropic API key (one line) into {secret} first", file=sys.stderr)
        return 1
    stack_path = ROOT / ".jane" / f"stack-{ns.project}.json"
    if not stack_path.is_file():
        print(f"no stack file {stack_path}: start the stack with `just up ... llm --project {ns.project}`")
        return 1
    stack = json.loads(stack_path.read_text(encoding="utf-8"))
    llm = (stack.get("services") or {}).get("llm")
    if not llm:
        print(f"the stack {ns.project} has no llm service")
        return 1
    base, key = llm["url"], stack["env"]["JANE_API_KEY_ADMIN"]

    call(
        base,
        key,
        "PUT",
        f"/v1/connections/{CONNECTION_ID}",
        {
            "connection_id": CONNECTION_ID,
            "kind": "llm_provider",
            "title": "Anthropic Messages API",
            "params": {"api_base": "https://api.anthropic.com"},
            "secret_refs": {"api_key": f"file:/run/secrets/{SECRET_NAME}"},
        },
    )
    call(
        base,
        key,
        "PUT",
        f"/v1/providers/{PROVIDER_ID}",
        {
            "provider_id": PROVIDER_ID,
            "kind": "anthropic",
            "connection_id": CONNECTION_ID,
            "enabled": True,
            "models": MODELS,
        },
    )
    for alias, model_id in ALIASES.items():
        call(
            base,
            key,
            "PUT",
            f"/v1/model-aliases/{alias}",
            {"alias": alias, "provider_id": PROVIDER_ID, "model_id": model_id},
        )
    call(
        base,
        key,
        "PUT",
        "/v1/budgets/platform/platform",
        {
            "scope_type": "platform",
            "scope_id": "platform",
            "budget": {"amount": ns.budget_usd_per_day, "currency": "USD", "period": "day"},
        },
    )
    print(
        f"llm {base}: connection {CONNECTION_ID} -> file:/run/secrets/{SECRET_NAME}, provider {PROVIDER_ID}"
    )
    for alias, model_id in ALIASES.items():
        print(f"  alias {alias:<8} -> {PROVIDER_ID}/{model_id}")
    print(f"  platform budget {ns.budget_usd_per_day:g} USD/day")

    if ns.check:
        result = call(
            base,
            key,
            "POST",
            "/v1/completions",
            {
                "model": "cheap",
                "instructions": "Reply with the single word: pong",
                "max_output_tokens": 256,
                "scope": {"purpose": "other"},
            },
            timeout=180,
        )
        usage = result.get("usage") or {}
        model = result.get("model") or {}
        print(
            f"check: {model.get('provider_id', '')}/{model.get('model_id', '')} "
            f"output={result.get('output_text')!r} usage={json.dumps(usage)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
