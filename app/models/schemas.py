# ============================================================================
# Personalized Networking Assistant — Pydantic Schemas
# ============================================================================
# Explicit validation models for every request and response payload that
# flows through the FastAPI backend.  Using Pydantic v2 conventions.
# ============================================================================

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Conversation (Topic Generation) ────────────────────────────────────────

class ConversationRequest(BaseModel):
    """Payload sent by the frontend to generate conversation starters."""

    event_description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Free-text description of the networking event or context.",
        examples=["AI for Sustainable Cities summit focusing on urban tech"],
    )
    user_interests: List[str] = Field(
        ...,
        min_length=1,
        description="List of the user's personal interests to tailor conversation topics.",
        examples=[["climate change", "urban planning", "smart cities"]],
    )


class ConversationResponse(BaseModel):
    """Payload returned after event analysis and topic generation."""

    categories: List[str] = Field(
        ...,
        description="Top-3 contextual categories extracted from the event description.",
    )
    conversation_starters: List[str] = Field(
        ...,
        description="AI-generated networking conversation openers.",
    )
    timestamp: str = Field(
        ...,
        description="ISO-8601 timestamp of when the response was created.",
    )


# ── Fact Checking ──────────────────────────────────────────────────────────

class FactCheckRequest(BaseModel):
    """Payload for a Wikipedia-based fact-check lookup."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Topic or keyword to look up on Wikipedia.",
        examples=["Blockchain in healthcare"],
    )


class FactCheckResponse(BaseModel):
    """Payload returned from the Wikipedia fact-check service."""

    title: str = Field(..., description="Title of the Wikipedia article.")
    summary: str = Field(..., description="Short extract / summary of the article.")
    url: str = Field(..., description="Direct URL to the Wikipedia article.")
    status: str = Field(
        ...,
        description="Lookup status: 'found', 'not_found', or 'error'.",
    )
    related_topics: List[str] = Field(
        default_factory=list,
        description="Optional list of related topic suggestions.",
    )


# ── User Feedback ─────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    """Payload submitted when a user rates the assistant."""

    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Star rating between 1 (poor) and 5 (excellent).",
    )
    comment: str = Field(
        default="",
        max_length=2000,
        description="Optional free-text comment.",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for traceability.",
    )


class FeedbackResponse(BaseModel):
    """Acknowledgement returned after feedback is recorded."""

    status: str = Field(default="success")
    message: str = Field(default="Feedback recorded successfully.")
    timestamp: str = Field(
        ...,
        description="ISO-8601 timestamp of the recorded feedback.",
    )


# ── Persisted Log Entries ──────────────────────────────────────────────────

class HistoryEntry(BaseModel):
    """Schema for a single row in history.json."""

    timestamp: str
    event_description: str
    interests: List[str]
    categories: List[str]
    conversation_starters: List[str]


class FeedbackEntry(BaseModel):
    """Schema for a single row in feedback.json."""

    timestamp: str
    rating: int
    comment: str
    session_id: Optional[str] = None


# ── Health Check ───────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Simple health-check response."""

    status: str = "healthy"
    version: str = ""
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
    )
