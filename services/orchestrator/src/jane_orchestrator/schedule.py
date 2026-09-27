"""Next fire time of a ``Schedule`` (manual | once | cron | interval), IANA time zones via zoneinfo."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

__all__ = ["CronError", "next_fire", "parse_cron"]

CRON_SEARCH_DAYS = 366 * 5  # a cron that never fires within 5 years (e.g. Feb 30) has no next run


class CronError(ValueError):
    pass


_RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
_NAMES = {
    3: {
        m: i + 1
        for i, m in enumerate(
            ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        )
    },
    4: {d: i for i, d in enumerate(["sun", "mon", "tue", "wed", "thu", "fri", "sat"])},
}


def _field(text: str, idx: int) -> set[int]:
    lo, hi = _RANGES[idx]
    out: set[int] = set()
    for part in text.lower().split(","):
        step = 1
        has_step = "/" in part
        if has_step:
            part, step_s = part.split("/", 1)
            if not step_s.isdigit() or int(step_s) < 1:
                raise CronError(f"bad step in {text!r}")
            step = int(step_s)
        if part in {"*", ""}:
            a, b = lo, hi
        elif "-" in part:
            a_s, b_s = part.split("-", 1)
            a, b = _value(a_s, idx), _value(b_s, idx)
        else:
            a = _value(part, idx)
            b = hi if has_step else a
        if not (lo <= a <= hi and lo <= b <= hi) or a > b:
            raise CronError(f"value out of range in {text!r}")
        out.update(range(a, b + 1, step))
    if idx == 4 and 7 in out:  # 7 = Sunday
        out.discard(7)
        out.add(0)
    return out


def _value(text: str, idx: int) -> int:
    names = _NAMES.get(idx, {})
    if text in names:
        return names[text]
    if not text.isdigit():
        raise CronError(f"bad cron value {text!r}")
    return int(text)


def parse_cron(expr: str) -> tuple[set[int], set[int], set[int], set[int], set[int], bool, bool]:
    parts = expr.split()
    if len(parts) != 5:
        raise CronError("cron needs five fields")
    fields = [_field(p, i) for i, p in enumerate(parts)]
    dom_any = parts[2] == "*"
    dow_any = parts[4] == "*"
    return fields[0], fields[1], fields[2], fields[3], fields[4], dom_any, dow_any


def _cron_next(expr: str, after: datetime, tz: ZoneInfo) -> datetime | None:
    minutes, hours, doms, months, dows, dom_any, dow_any = parse_cron(expr)
    local = after.astimezone(tz)
    day: date = local.date()
    for _ in range(CRON_SEARCH_DAYS):
        if day.month in months:
            dom_ok = day.day in doms
            dow_ok = (day.isoweekday() % 7) in dows
            if dom_any and dow_any:
                ok = True
            elif dom_any:
                ok = dow_ok
            elif dow_any:
                ok = dom_ok
            else:
                ok = dom_ok or dow_ok  # classic cron: either matches
            if ok:
                for h in sorted(hours):
                    for m in sorted(minutes):
                        candidate = datetime(day.year, day.month, day.day, h, m, tzinfo=tz)
                        if candidate.astimezone(UTC) > after.astimezone(UTC):
                            return candidate.astimezone(UTC)
        day += timedelta(days=1)
    return None


def next_fire(
    schedule: Mapping[str, Any] | None, after: datetime, last_fired: datetime | None
) -> datetime | None:
    """Next run strictly after ``after`` (UTC), or ``None`` (manual, disabled, finished)."""
    if not schedule or schedule.get("enabled", True) is False:
        return None
    kind = schedule.get("type")
    start = _ts(schedule.get("start_at"))
    end = _ts(schedule.get("end_at"))
    floor = max(after, start - timedelta(microseconds=1)) if start else after
    result: datetime | None
    if kind == "once":
        at = _ts(schedule.get("at"))
        result = at if at is not None and last_fired is None else None
    elif kind == "interval":
        step = timedelta(seconds=int(schedule["interval_seconds"]))
        if last_fired is None:
            result = start if start and start > after else after + step  # first tick: start_at or one interval from now
        else:
            result = last_fired + step
            if result <= after:  # missed ticks while down: fire once now, then continue the cadence
                result = after
    elif kind == "cron":
        result = _cron_next(str(schedule["cron"]), floor, ZoneInfo(schedule.get("timezone") or "UTC"))
    else:
        return None
    if result is not None and end is not None and result > end:
        return None
    return result


def _ts(value: Any) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
