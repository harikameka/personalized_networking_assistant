# ============================================================================
# Personalized Networking Assistant — Event Analyzer Service
# ============================================================================
# Uses HuggingFace zero-shot-classification pipeline (DistilBERT) to extract
# the most relevant contextual categories from a raw event description.
#
# The pipeline is loaded ONCE at module level to avoid expensive reloads on
# every request.  The module is fully stateless beyond the cached model.
# ============================================================================

from __future__ import annotations

import logging
from typing import List, Optional

from transformers import pipeline  # type: ignore

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global model loading — happens once when the module is first imported.
# ---------------------------------------------------------------------------
logger.info(
    "Loading zero-shot-classification model: %s …", settings.classifier_model
)

try:
    _classifier = pipeline(
        task="zero-shot-classification",
        model=settings.classifier_model,
    )
    logger.info("Zero-shot classifier loaded successfully.")
except Exception as exc:
    logger.error("Failed to load classifier model: %s", exc)
    _classifier = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_event(
    text: str,
    candidate_labels: Optional[List[str]] = None,
    top_k: int = 3,
) -> List[str]:
    """
    Classify *text* against a set of candidate labels and return the top-*k*
    categories ranked by confidence.

    Parameters
    ----------
    text : str
        Raw event description or context string.
    candidate_labels : list[str] | None
        Labels to classify against.  Falls back to the config defaults.
    top_k : int
        Number of top categories to return (default 3).

    Returns
    -------
    list[str]
        Top-k category labels sorted by descending confidence score.
    """

    # Fall back to default labels from application configuration
    if candidate_labels is None:
        candidate_labels = settings.default_candidate_labels

    # If the classifier failed to load, return a safe fallback
    if _classifier is None:
        logger.warning(
            "Classifier unavailable — returning first %d default labels.", top_k
        )
        return candidate_labels[:top_k]

    try:
        result = _classifier(
            text,
            candidate_labels=candidate_labels,
            multi_label=False,
        )
        # result is a dict with keys: 'labels', 'scores', 'sequence'
        top_labels: List[str] = result["labels"][:top_k]
        top_scores = result["scores"][:top_k]

        logger.info(
            "Event analysis complete — top categories: %s (scores: %s)",
            top_labels,
            [round(s, 4) for s in top_scores],
        )
        return top_labels

    except Exception as exc:
        logger.error("Event analysis failed: %s", exc)
        # Graceful degradation: return first top_k default labels
        return candidate_labels[:top_k]
