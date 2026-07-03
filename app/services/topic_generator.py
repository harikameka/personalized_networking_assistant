# ============================================================================
# Personalized Networking Assistant — Topic Generator Service
# ============================================================================
# Uses HuggingFace GPT-2 text-generation pipeline to produce context-aware
# networking conversation starters from extracted event categories and the
# user's declared interests.
#
# A rich set of FALLBACK TEMPLATES guarantees usable output even when the
# model produces malformed text.
# ============================================================================

from __future__ import annotations

import logging
import random
import re
from typing import List

from transformers import pipeline, set_seed  # type: ignore

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global model loading
# ---------------------------------------------------------------------------
logger.info("Loading text-generation model: %s …", settings.generator_model)

try:
    _generator = pipeline(
        task="text-generation",
        model=settings.generator_model,
    )
    logger.info("Text-generation model loaded successfully.")
except Exception as exc:
    logger.error("Failed to load generator model: %s", exc)
    _generator = None

# ---------------------------------------------------------------------------
# Fallback conversation-starter templates
# ---------------------------------------------------------------------------
_FALLBACK_TEMPLATES: List[str] = [
    "I've been exploring the intersection of {category} and {interest} — "
    "what trends are you most excited about?",

    "With all the buzz around {category}, I'm curious how you see it "
    "impacting {interest} in the next few years.",

    "As someone passionate about {interest}, I'd love to hear your "
    "perspective on {category} and its real-world applications.",

    "I recently came across some fascinating developments in {category}. "
    "How does that connect with your work in {interest}?",

    "What drew you to this event? I'm personally interested in how "
    "{category} can drive innovation in {interest}.",

    "Have you noticed how {category} is starting to reshape conversations "
    "around {interest}? I'd love to swap notes.",

    "I think the synergy between {category} and {interest} is underexplored "
    "— do you agree?",

    "Between sessions, I've been reflecting on how {category} could "
    "transform {interest}. What's your take?",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_prompt(categories: List[str], interests: List[str]) -> str:
    """
    Construct a GPT-2 prompt that nudges the model toward producing
    networking conversation starters.
    """
    cats_str = ", ".join(categories)
    ints_str = ", ".join(interests)
    return (
        f"Generate professional networking conversation starters for an event "
        f"about {cats_str}. The attendee is interested in {ints_str}.\n\n"
        f"1."
    )


def _extract_sentences(raw_text: str, target_count: int = 3) -> List[str]:
    """
    Post-process raw model output to extract clean, individual sentences.

    Strategy:
    1. Split on numbered prefixes like '1.', '2.', '3.'.
    2. Fall back to sentence-boundary splitting.
    3. Strip and deduplicate.
    """

    # Try numbered-list extraction first
    parts = re.split(r"\d+\.\s*", raw_text)
    sentences = [s.strip().split("\n")[0].strip() for s in parts if s.strip()]

    # Fall back to sentence splitting if we didn't get enough
    if len(sentences) < target_count:
        sentences = re.split(r"(?<=[.!?])\s+", raw_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for s in sentences:
        normalized = s.lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(s)

    return unique[:target_count]


def _generate_fallbacks(
    categories: List[str],
    interests: List[str],
    count: int = 3,
) -> List[str]:
    """
    Produce deterministic but varied conversation starters from the
    template bank when the generative model is unavailable or returns
    unusable output.
    """
    starters: List[str] = []
    templates = random.sample(_FALLBACK_TEMPLATES, min(count, len(_FALLBACK_TEMPLATES)))

    for template in templates:
        category = random.choice(categories) if categories else "technology"
        interest = random.choice(interests) if interests else "innovation"
        starters.append(template.format(category=category, interest=interest))

    return starters[:count]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_topics(
    categories: List[str],
    interests: List[str],
    num_starters: int = 3,
) -> List[str]:
    """
    Generate *num_starters* networking conversation openers by combining
    event categories with user interests.

    Parameters
    ----------
    categories : list[str]
        Contextual categories from the event analyzer.
    interests : list[str]
        User-declared personal interests.
    num_starters : int
        Desired number of starters (default 3).

    Returns
    -------
    list[str]
        Clean, ready-to-use conversation starters.
    """

    # Guard: if the model never loaded, go straight to fallbacks
    if _generator is None:
        logger.warning("Generator unavailable — using fallback templates.")
        return _generate_fallbacks(categories, interests, num_starters)

    prompt = _build_prompt(categories, interests)
    logger.info("Generating topics with prompt: %s", prompt[:120])

    try:
        set_seed(42)
        outputs = _generator(
            prompt,
            max_new_tokens=200,
            num_return_sequences=1,
            temperature=0.8,
            top_p=0.92,
            do_sample=True,
            pad_token_id=_generator.tokenizer.eos_token_id,
        )

        raw_text: str = outputs[0]["generated_text"]
        logger.debug("Raw model output: %s", raw_text[:300])

        starters = _extract_sentences(raw_text, target_count=num_starters)

        # If extraction couldn't pull enough sentences, pad with fallbacks
        if len(starters) < num_starters:
            logger.info(
                "Model produced %d starters; padding with fallbacks.",
                len(starters),
            )
            fallbacks = _generate_fallbacks(categories, interests, num_starters)
            for fb in fallbacks:
                if len(starters) >= num_starters:
                    break
                if fb.lower() not in {s.lower() for s in starters}:
                    starters.append(fb)

        return starters[:num_starters]

    except Exception as exc:
        logger.error("Topic generation failed: %s", exc)
        return _generate_fallbacks(categories, interests, num_starters)
