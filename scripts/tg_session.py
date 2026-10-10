"""Create the Telethon session of the Telegram collector (interactive; run by the account's owner).

Telegram sends a login code to the account: the script asks for it (and the two-step password, if set) in
the terminal, then writes the session string to ``.jane/secrets/tg_session`` and the API hash to
``.jane/secrets/tg_api_hash`` - git-ignored, mounted read-only into telegram-collector as ``/run/secrets``
(``infra/compose.local.example.yaml``). Neither value is printed. The session is a full login of the account:
keep it like a password and end it in Telegram (Settings -> Devices -> "Jane collector") when not needed.

    uv run --package jane-telegram-collector --extra telethon python scripts/tg_session.py --api-id <id> --phone <+380...>
"""

from __future__ import annotations

import argparse
import getpass
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / ".jane" / "secrets"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api-id", type=int, required=True, help="api_id from my.telegram.org (not a secret)")
    ap.add_argument("--phone", help="phone number of the account (asked if omitted)")
    ns = ap.parse_args(argv)

    # Telethon is an optional extra, loaded only for this interactive command.
    sessions = importlib.import_module("telethon.sessions")
    sync = importlib.import_module("telethon.sync")

    SECRETS.mkdir(parents=True, exist_ok=True)
    hash_file, session_file = SECRETS / "tg_api_hash", SECRETS / "tg_session"
    api_hash = hash_file.read_text(encoding="utf-8").strip() if hash_file.is_file() else ""
    if not api_hash:
        api_hash = getpass.getpass("api_hash from my.telegram.org (input hidden): ").strip()
    if not api_hash:
        print("no api_hash given", file=sys.stderr)
        return 1
    client = sync.TelegramClient(sessions.StringSession(), ns.api_id, api_hash, device_model="Jane collector")
    client.start(phone=ns.phone or (lambda: input("Phone number: ").strip()))
    try:
        me = client.get_me()
        session = client.session.save()
    finally:
        client.disconnect()
    hash_file.write_text(api_hash + "\n", encoding="utf-8")
    session_file.write_text(session + "\n", encoding="utf-8")
    print(f"session saved for {'@' + me.username if me.username else 'user ' + str(me.id)}: {session_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
