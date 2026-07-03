# ============================================================================
# Personalized Networking Assistant — Feedback Logger Service
# ============================================================================
# Provides JSON-file-based persistence for user feedback (star ratings and
# comments).  Each entry is stamped with a localized ISO-8601 timestamp.
#
# Mirrors the history_logger pattern for consistency across the codebase.
# ============================================================================

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


def _get_path() -> Path:
    """Return the resolved path to the feedback file, ensuring the parent dir exists."""
    path = settings.get_feedback_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _now_iso() -> str:
    """Return the current local time as a high-precision ISO-8601 string."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="microseconds")


def _read_file(path: Path) -> List[Dict[str, Any]]:
    """Safely read the JSON feedback file; return an empty list on any error."""
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read feedback file: %s", exc)
        return []


def _write_file(path: Path, data: List[Dict[str, Any]]) -> None:
    """Atomically write the full feedback list back to disk."""
    try:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.error("Failed to write feedback file: %s", exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_feedback(
    rating: int,
    comment: str = "",
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Append a new feedback entry to ``feedback.json``.

    Parameters
    ----------
    rating : int
        Star rating 1–5.
    comment : str
        Optional free-text comment.
    session_id : str | None
        Optional session identifier for traceability.

    Returns
    -------
    dict
        The persisted entry including its timestamp.
    """
    entry: Dict[str, Any] = {
        "timestamp": _now_iso(),
        "rating": rating,
        "comment": comment,
        "session_id": session_id or "",
    }

    path = _get_path()
    feedback = _read_file(path)
    feedback.append(entry)
    _write_file(path, feedback)

    logger.info("Feedback logged: rating=%d at %s", rating, entry["timestamp"])
    return entry


def get_feedback() -> List[Dict[str, Any]]:
    """
    Read and return all feedback entries.

    Returns
    -------
    list[dict]
        All feedback entries, newest-last.
    """
    path = _get_path()
    feedback = _read_file(path)
    logger.info("Retrieved %d feedback entries.", len(feedback))
    return feedback


def get_average_rating() -> float:
    """
    Compute the mean feedback rating.  Returns 0.0 if no feedback exists.
    """
    feedback = get_feedback()
    if not feedback:
        return 0.0
    total = sum(entry.get("rating", 0) for entry in feedback)
    return round(total / len(feedback), 2)
