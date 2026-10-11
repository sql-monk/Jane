"""Backup/restore rehearsal, restricted to disposable jane-docs-* stacks."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "deploy/profiles"))
from stack import APP_SERVICES, Stack  # noqa: E402 -- import the checkout-local stack helper

DBS = (
    "jane_handler_runtime",
    "jane_orchestrator",
    "jane_registry",
    "jane_llm",
    "jane_assistant",
    "jane_storage_results",
)


def command(args, data=None):
    r = subprocess.run(args, input=data, capture_output=True)  # noqa: S603 -- fixed Docker argv and validated isolated project
    if r.returncode:
        raise RuntimeError(f"{args[0]} exited {r.returncode}: " + r.stderr.decode(errors="replace")[:300])
    return r.stdout


def sql(cid, db, text):
    return (
        command(
            [
                "docker",
                "exec",
                cid,
                "psql",
                "-U",
                "jane",
                "-d",
                db,
                "-X",
                "-A",
                "-t",
                "-v",
                "ON_ERROR_STOP=1",
                "-c",
                text,
            ]
        )
        .decode()
        .strip()
    )


def rows(cid, db):
    tables = sql(
        cid,
        db,
        "SELECT n.nspname||'.'||c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%' ORDER BY 1",
    ).splitlines()
    result = {}
    for table in tables:
        if not re.fullmatch(r"[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*", table):
            raise ValueError("unexpected table name")
        text = sql(cid, db, f"SELECT row_to_json(t)::text FROM {table} AS t ORDER BY row_to_json(t)::text")  # noqa: S608 -- table passes the identifier allowlist above
        result[table] = {
            "rows": len(text.splitlines()) if text else 0,
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
    return result


def files(data):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for item in tar:
            path = PurePosixPath(item.name)
            if path.is_absolute() or ".." in path.parts or item.issym() or item.islnk():
                raise ValueError("unsafe member")
            if item.isfile():
                result[item.name] = hashlib.sha256(tar.extractfile(item).read()).hexdigest()
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True)
    ns = ap.parse_args()
    if not re.fullmatch(r"jane-docs-[a-z0-9-]+", ns.project):
        ap.error("only disposable jane-docs-* project allowed")
    stack = Stack(ns.project, verbose=False)
    meta = json.loads((ROOT / ".jane" / f"stack-{ns.project}.json").read_text(encoding="utf-8"))
    if meta["project"] != ns.project:
        raise ValueError("metadata identity mismatch")
    cid = stack.compose("ps", "-q", "postgres", quiet=True).stdout.strip()
    details = json.loads(command(["docker", "inspect", cid]))[0]
    if details["Config"]["Labels"].get("com.docker.compose.project") != ns.project:
        raise ValueError("postgres project mismatch")
    out = ROOT / ".jane/documentation-backups" / ns.project
    out.mkdir(parents=True, exist_ok=True)
    running = stack.compose("ps", "--services", "--status", "running", quiet=True).stdout.splitlines()
    stopped = [x for x in running if x in APP_SERVICES or x == "minio"]
    clones = []
    dbs = []
    report = {"project": ns.project, "databases": {}, "volumes": {}}
    try:
        if stopped:
            stack.compose("stop", *stopped, quiet=True)
        for db in DBS:
            data = command(["docker", "exec", cid, "pg_dump", "-U", "jane", "-d", db, "-Fc"])
            (out / f"{db}.dump").write_bytes(data)
            before = rows(cid, db)
            target = "documentation_restore_" + db[5:]
            if sql(cid, "postgres", f"SELECT 1 FROM pg_database WHERE datname='{target}'"):  # noqa: S608 -- generated from the fixed DBS tuple
                raise ValueError("restore database exists; inspect before retry")
            sql(cid, "postgres", f"CREATE DATABASE {target} TEMPLATE template0")
            dbs.append(target)
            command(
                [
                    "docker",
                    "exec",
                    "-i",
                    cid,
                    "pg_restore",
                    "-U",
                    "jane",
                    "-d",
                    target,
                    "--no-owner",
                    "--no-privileges",
                ],
                data,
            )
            if rows(cid, target) != before:
                raise RuntimeError(db + " row content differs")
            report["databases"][db] = {
                "tables": len(before),
                "rows": sum(x["rows"] for x in before.values()),
                "data_equal": True,
            }
        volumes = (
            command(
                ["docker", "volume", "ls", "-q", "--filter", f"label=com.docker.compose.project={ns.project}"]
            )
            .decode()
            .splitlines()
        )
        for volume in volumes:
            labels = json.loads(command(["docker", "volume", "inspect", volume]))[0]["Labels"]
            logical = labels.get("com.docker.compose.volume")
            if logical not in {"minio-data", "storage-data", "web-collector-data", "telegram-collector-data"}:
                continue
            archive = command(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{volume}:/data:ro",
                    "postgres:18",
                    "tar",
                    "-C",
                    "/data",
                    "-cf",
                    "-",
                    ".",
                ]
            )
            expected = files(archive)
            (out / f"{logical}.tar").write_bytes(archive)
            clone = f"{ns.project}-restore-{logical}"
            if command(["docker", "volume", "ls", "-q", "--filter", f"name=^{clone}$"]).strip():
                raise ValueError("restore volume exists; inspect before retry")
            command(
                [
                    "docker",
                    "volume",
                    "create",
                    "--label",
                    f"io.jane.documentation.project={ns.project}",
                    clone,
                ]
            )
            clones.append(clone)
            command(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-i",
                    "-v",
                    f"{clone}:/data",
                    "postgres:18",
                    "tar",
                    "-C",
                    "/data",
                    "-xf",
                    "-",
                ],
                archive,
            )
            restored = command(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{clone}:/data:ro",
                    "postgres:18",
                    "tar",
                    "-C",
                    "/data",
                    "-cf",
                    "-",
                    ".",
                ]
            )
            if files(restored) != expected:
                raise RuntimeError(logical + " bytes differ")
            report["volumes"][logical] = {"files": len(expected), "data_equal": True}
        report["ok"] = True
        (out / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
    finally:
        for db in dbs:
            sql(cid, "postgres", f"DROP DATABASE {db}")
        for clone in clones:
            labels = json.loads(command(["docker", "volume", "inspect", clone]))[0]["Labels"]
            if labels.get("io.jane.documentation.project") == ns.project:
                command(["docker", "volume", "rm", clone])
        if stopped:
            stack.compose("start", *stopped, quiet=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
