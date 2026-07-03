# ============================================================================
# Personalized Networking Assistant — Conversation Router
# ============================================================================
# FastAPI router exposing all REST endpoints for the application:
#   • POST /api/generate      — Analyze event + generate starters
#   • POST /api/fact-check     — Wikipedia fact lookup
#   • POST /api/feedback       — Submit user feedback
#   • GET  /api/history        — Retrieve conversation history
#   • DELETE /api/history      — Clear conversation history
#   • GET  /api/feedback       — Retrieve all feedback entries
#   • GET  /api/stats          — Aggregated analytics
# ============================================================================

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ConversationRequest,
    ConversationResponse,
    FactCheckRequest,
    FactCheckResponse,
    FeedbackRequest,
    FeedbackResponse,
)
from app.services import (
    event_analyzer,
    fact_checker,
    feedback_logger,
    history_logger,
    topic_generator,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router instance — mounted by main.py
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/api", tags=["Conversation"])


# ── Generate Conversation Starters ─────────────────────────────────────────

@router.post(
    "/generate",
    response_model=ConversationResponse,
    summary="Analyze an event and generate smart conversation starters",
)
async def generate_starters(request: ConversationRequest) -> ConversationResponse:
    """
    1. Classify the event description into top-3 categories (DistilBERT).
    2. Generate conversation openers aligned with those categories and the
       user's interests (GPT-2 + fallback templates).
    3. Persist the result in history.json.
    """
    logger.info(
        "POST /api/generate — event=%r, interests=%s",
        request.event_description[:80],
        request.user_interests,
    )

    try:
        # Step 1: Event analysis (zero-shot classification)
        categories = event_analyzer.analyze_event(request.event_description)

        # Step 2: Topic generation
        starters = topic_generator.generate_topics(
            categories=categories,
            interests=request.user_interests,
        )

        # Step 3: Build response timestamp
        timestamp = (
            datetime.now(timezone.utc)
            .astimezone()
            .isoformat(timespec="microseconds")
        )

        # Step 4: Log to history
        history_logger.log_conversation(
            event_description=request.event_description,
            interests=request.user_interests,
            categories=categories,
            conversation_starters=starters,
        )

        return ConversationResponse(
            categories=categories,
            conversation_starters=starters,
            timestamp=timestamp,
        )

    except Exception as exc:
        logger.error("Generation pipeline error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate conversation starters: {exc}",
        )


# ── Fact Check ─────────────────────────────────────────────────────────────

@router.post(
    "/fact-check",
    response_model=FactCheckResponse,
    summary="Look up a topic on Wikipedia for quick fact verification",
)
async def fact_check(request: FactCheckRequest) -> FactCheckResponse:
    """
    Perform a live lookup against the Wikipedia REST API and return a
    structured summary.
    """
    logger.info("POST /api/fact-check — query=%r", request.query)

    result = fact_checker.check_fact(request.query)

    return FactCheckResponse(
        title=result["title"],
        summary=result["summary"],
        url=result.get("url", ""),
        status=result["status"],
        related_topics=result.get("related_topics", []),
    )


# ── Feedback ───────────────────────────────────────────────────────────────

@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit a user feedback rating and comment",
)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Record a star rating and optional comment."""
    logger.info(
        "POST /api/feedback — rating=%d, session=%s",
        request.rating,
        request.session_id,
    )

    entry = feedback_logger.log_feedback(
        rating=request.rating,
        comment=request.comment,
        session_id=request.session_id,
    )

    return FeedbackResponse(
        status="success",
        message="Thank you! Your feedback has been recorded.",
        timestamp=entry["timestamp"],
    )


@router.get(
    "/feedback",
    summary="Retrieve all user feedback entries",
)
async def get_feedback() -> list[dict]:
    """Return every feedback entry stored in feedback.json."""
    return feedback_logger.get_feedback()


# ── History ────────────────────────────────────────────────────────────────

@router.get(
    "/history",
    summary="Retrieve full conversation history",
)
async def get_history() -> list[dict]:
    """Return every conversation-generation entry stored in history.json."""
    return history_logger.get_history()


@router.delete(
    "/history",
    summary="Clear all conversation history",
)
async def clear_history() -> dict:
    """Wipe history.json and return the count of deleted entries."""
    count = history_logger.clear_history()
    return {"status": "success", "deleted": count}


# ── Stats / Analytics ─────────────────────────────────────────────────────

@router.get(
    "/stats",
    summary="Aggregated analytics for the dashboard",
)
async def get_stats() -> dict:
    """
    Return lightweight statistics consumed by the frontend analytics page.
    """
    history = history_logger.get_history()
    feedback = feedback_logger.get_feedback()
    avg_rating = feedback_logger.get_average_rating()

    # Count total fact-check–style entries (for demo purposes, tracked via history)
    total_starters = sum(
        len(h.get("conversation_starters", [])) for h in history
    )

    return {
        "total_conversations": len(history),
        "total_starters_generated": total_starters,
        "total_feedback": len(feedback),
        "average_rating": avg_rating,
    }
