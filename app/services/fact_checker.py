# ============================================================================
# Personalized Networking Assistant — Fact Checker Service
# ============================================================================
# Performs live outbound HTTP requests against the Wikipedia REST API to
# retrieve article summaries for quick fact verification.
#
# All network calls are wrapped in try/except blocks with timeout handling
# to ensure the backend never crashes from external API failures.
# ============================================================================

from __future__ import annotations

import logging
from typing import Dict
from urllib.parse import quote

import requests

from app.config import settings

logger = logging.getLogger(__name__)


def check_fact(query: str) -> Dict[str, object]:
    """
    Look up *query* on Wikipedia and return a structured summary.

    Parameters
    ----------
    query : str
        Topic or keyword to search (e.g. "Blockchain in healthcare").

    Returns
    -------
    dict
        Keys: title, summary, url, status, related_topics.
        ``status`` is one of ``'found'``, ``'not_found'``, or ``'error'``.
    """

    # URL-encode the query for safe inclusion in the REST path
    encoded_query = quote(query.strip().replace(" ", "_"), safe="")
    url = f"{settings.wikipedia_base_url}{encoded_query}"

    logger.info("Fact-check request: query=%r → %s", query, url)

    try:
        response = requests.get(
            url,
            timeout=settings.wikipedia_timeout,
            headers={"User-Agent": "PersonalizedNetworkingAssistant/1.0"},
        )

        # ── Article found ───────────────────────────────────────────────
        if response.status_code == 200:
            data = response.json()
            result = {
                "title": data.get("title", query),
                "summary": data.get("extract", "No summary available."),
                "url": data.get("content_urls", {})
                         .get("desktop", {})
                         .get("page", f"https://en.wikipedia.org/wiki/{encoded_query}"),
                "status": "found",
                "related_topics": _extract_related(data),
            }
            logger.info("Fact-check success: %s", result["title"])
            return result

        # ── Article not found (404) ─────────────────────────────────────
        if response.status_code == 404:
            logger.warning("Wikipedia article not found for: %s", query)
            return {
                "title": query,
                "summary": f"No Wikipedia article found for '{query}'.",
                "url": "",
                "status": "not_found",
                "related_topics": [],
            }

        # ── Other HTTP errors ───────────────────────────────────────────
        logger.error(
            "Wikipedia API returned HTTP %d for query: %s",
            response.status_code,
            query,
        )
        return {
            "title": query,
            "summary": f"Wikipedia returned an unexpected status ({response.status_code}).",
            "url": "",
            "status": "error",
            "related_topics": [],
        }

    except requests.exceptions.Timeout:
        logger.error("Wikipedia API timed out for query: %s", query)
        return {
            "title": query,
            "summary": "The Wikipedia lookup timed out. Please try again later.",
            "url": "",
            "status": "error",
            "related_topics": [],
        }

    except requests.exceptions.ConnectionError:
        logger.error("Network error during Wikipedia lookup for: %s", query)
        return {
            "title": query,
            "summary": "Unable to connect to Wikipedia. Check your internet connection.",
            "url": "",
            "status": "error",
            "related_topics": [],
        }

    except Exception as exc:
        logger.error("Unexpected error during fact-check: %s", exc)
        return {
            "title": query,
            "summary": f"An unexpected error occurred: {exc}",
            "url": "",
            "status": "error",
            "related_topics": [],
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_related(data: dict) -> list[str]:
    """
    Pull related topic hints from the Wikipedia response payload.
    The REST summary endpoint doesn't always include related links,
    so this is best-effort.
    """
    related: list[str] = []

    # 'description' often contains useful topical keywords
    description = data.get("description", "")
    if description:
        related.append(description)

    # If the API returned 'wikibase_item', include it as metadata
    wikibase = data.get("wikibase_item", "")
    if wikibase:
        related.append(f"Wikidata: {wikibase}")

    return related
