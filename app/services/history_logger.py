# ============================================================================
# Personalized Networking Assistant — History Logger Service
# ============================================================================
# Provides JSON-file-based persistence for conversation-generation history.
# Each entry is stamped with a high-precision localized ISO-8601 timestamp.
#
# The data directory is auto-created if missing, preventing first-run errors.
# ============================================================================

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.config import settings

logger = logging.getLogger(__name__)


def _get_path() -> Path:
    """Return the resolved path to the history file, ensuring the parent dir exists."""
    path = settings.get_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _now_iso() -> str:
    """Return the current local time as a high-precision ISO-8601 string."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="microseconds")


def _read_file(path: Path) -> List[Dict[str, Any]]:
    """Safely read the JSON history file; return an empty list on any error."""
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read history file: %s", exc)
        return []


def _write_file(path: Path, data: List[Dict[str, Any]]) -> None:
    """Atomically write the full history list back to disk."""
    try:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.error("Failed to write history file: %s", exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_conversation(
    event_description: str,
    interests: List[str],
    categories: List[str],
    conversation_starters: List[str],
) -> Dict[str, Any]:
    """
    Append a new conversation-generation record to ``history.json``.

    Returns the persisted entry (including its timestamp).
    """
    entry: Dict[str, Any] = {
        "timestamp": _now_iso(),
        "event_description": event_description,
        "interests": interests,
        "categories": categories,
        "conversation_starters": conversation_starters,
    }

    path = _get_path()
    history = _read_file(path)
    history.append(entry)
    _write_file(path, history)

    logger.info("Conversation logged at %s", entry["timestamp"])
    return entry


def get_history() -> List[Dict[str, Any]]:
    """
    Read and return the full conversation history.

    Returns
    -------
    list[dict]
        All history entries, newest-last.
    """
    path = _get_path()
    history = _read_file(path)
    logger.info("Retrieved %d history entries.", len(history))
    return history


def clear_history() -> int:
    """
    Delete all conversation history and return the count of removed entries.
    """
    path = _get_path()
    history = _read_file(path)
    count = len(history)
    _write_file(path, [])
    logger.info("Cleared %d history entries.", count)
    return count
