from datetime import datetime, timezone


def parse_iso(ts: str) -> datetime:
    """
    Convert an RFC 3339 / ISO-8601 string (e.g. 2025-07-18T19:09:20Z)
    to a *naïve* datetime in UTC so it compares equal to DB-derived
    timestamps that lack tzinfo.
    """
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
