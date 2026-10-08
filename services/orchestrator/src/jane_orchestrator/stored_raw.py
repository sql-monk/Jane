"""RAW references recorded by the orchestrator itself; no reads of storage-owned tables."""

from __future__ import annotations

from typing import Any


def stored_raw_id(
    conn: Any,
    source_id: str,
    observation_id: str | None,
    *,
    run_id: str | None = None,
    invocation_id: str | None = None,
) -> str | None:
    """Return a known RAW id for this observation and run, never a different observation of its URL.

    A problem sample identifies its run through the invocation. Missing provenance or several distinct
    RAW copies is not resolved by choosing an arbitrary object: the optional API field stays absent.
    """
    if not observation_id:
        return None
    rows = conn.execute(
        """
        SELECT DISTINCT raw.stored_object_id, raw.stored_object_ambiguous FROM items raw
        WHERE raw.source_id = %s AND raw.observation_id = %s
          AND (raw.stored_object_id IS NOT NULL OR raw.stored_object_ambiguous)
          AND (%s::text IS NULL OR raw.run_id = %s)
          AND (%s::text IS NULL OR EXISTS (
              SELECT 1 FROM items problem WHERE problem.run_id = raw.run_id AND problem.invocation_id = %s))
        """,
        (source_id, observation_id, run_id, run_id, invocation_id, invocation_id),
    ).fetchall()
    if any(row["stored_object_ambiguous"] for row in rows):
        return None
    return str(rows[0]["stored_object_id"]) if len(rows) == 1 else None
