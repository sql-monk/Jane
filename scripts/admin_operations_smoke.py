"""Verify fresh image/volume ownership, configuration persistence and telemetry without touching a stack."""

from __future__ import annotations

import argparse
import json
import subprocess
import uuid


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--settings-module", required=True)
    args = parser.parse_args()
    volume = f"jane-wp33-smoke-{uuid.uuid4().hex}"
    subprocess.run(
        ["docker", "volume", "create", "--label", "jane.wp=33-smoke", volume], check=True, capture_output=True
    )
    program = """
import json, os
from pathlib import Path
from importlib import import_module
from fastapi.testclient import TestClient
from jane_kit.operations import Operations
from jane_kit.service import create_app
Settings = import_module(os.environ['SMOKE_SETTINGS_MODULE']).Settings
settings = Settings(host='127.0.0.1')
assert settings.operations_dir == Path('/var/lib/jane-operations')
assert os.access(settings.operations_dir, os.W_OK)
app = create_app(settings, configure_logs=False)
with TestClient(app) as client:
    current = client.get('/v1/configuration')
    assert current.status_code == 200
    field = next(f for f in current.json()['fields'] if f['path'] == 'settings.operations_max_points')
    expected = int(os.environ['SMOKE_EXPECTED_POINTS'])
    assert field['value'] == expected
    assert not current.json()['pending_restart']
    sampler = Operations(app, settings, None)
    sampler.sample()
    history = client.get('/v1/telemetry').json()
    assert len(history['samples']) >= int(os.environ['SMOKE_MIN_SAMPLES'])
    if expected == 720:
        saved = client.put('/v1/configuration', headers={'If-Match': current.headers['etag']}, json={'values': {'settings.operations_max_points': 721}})
        assert saved.status_code == 200 and saved.json()['pending_restart']
    print(json.dumps({'uid': os.getuid(), 'directory_owner': settings.operations_dir.stat().st_uid, 'active_max_points': expected, 'history_points': len(history['samples']), 'pending_restart_at_start': False}))
"""
    try:
        for expected, minimum in [(720, 1), (721, 2)]:
            subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "-v",
                    f"{volume}:/var/lib/jane-operations",
                    "-e",
                    f"SMOKE_SETTINGS_MODULE={args.settings_module}",
                    "-e",
                    f"SMOKE_EXPECTED_POINTS={expected}",
                    "-e",
                    f"SMOKE_MIN_SAMPLES={minimum}",
                    args.image,
                    "python",
                    "-c",
                    program,
                ],
                check=True,
            )
    finally:
        inspected = json.loads(subprocess.check_output(["docker", "volume", "inspect", volume]))[0]
        if inspected["Name"] == volume and inspected.get("Labels", {}).get("jane.wp") == "33-smoke":
            subprocess.run(["docker", "volume", "rm", volume], check=True, capture_output=True)


if __name__ == "__main__":
    main()
