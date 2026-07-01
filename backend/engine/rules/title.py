"""Title tag audit rule module.

Extracts the page title from rendered HTML and validates it against
SEO best practices using deterministic rules.

Rules implemented:
    - meta_title_missing     — No <title> tag found (critical)
    - meta_title_empty       — <title> tag exists but is empty (critical)
    - meta_title_too_short   — Title is shorter than 30 characters (warning)
    - meta_title_too_long    — Title is longer than 60 characters (warning)
    - meta_title_ok          — Title length is within best-practice range (pass)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import MetaTagData

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Best-practice constants
# ---------------------------------------------------------------------------

TITLE_MIN_LENGTH: int = 30
TITLE_MAX_LENGTH: int = 60

# Scoring weights (out of 100 for this rule's contribution)
TITLE_PRESENT_WEIGHT: float = 50.0
TITLE_LENGTH_WEIGHT: float = 50.0


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass
class TitleAuditResult:
    """Output of the title tag audit."""

    meta_data: MetaTagData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def _extract_title(html: str) -> str | None:
    """Extract the text content of the first <title> tag.

    Returns None if no <title> tag exists, or the stripped text
    (which may be empty) if one is found.
    """
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    if title_tag is None:
        return None
    return title_tag.get_text(strip=True)


# ---------------------------------------------------------------------------
# Validation & scoring
# ---------------------------------------------------------------------------


def audit_title(html: str) -> TitleAuditResult:
    """Run the full title tag audit on rendered HTML.

    Args:
        html: The fully rendered page HTML.

    Returns:
        A :class:`TitleAuditResult` with extracted data, score,
        issues, and recommendations.
    """
    title_text = _extract_title(html)

    issues: list[AuditIssue] = []
    recommendations: list[AuditRecommendation] = []
    score: float = 0.0

    # --- Rule: missing title ---
    if title_text is None:
        issues.append(AuditIssue(
            rule_id="meta_title_missing",
            category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message="Page is missing a <title> tag.",
            value=None,
        ))
        recommendations.append(AuditRecommendation(
            rule_id="meta_title_missing",
            category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message=(
                f"Add a descriptive <title> tag between "
                f"{TITLE_MIN_LENGTH} and {TITLE_MAX_LENGTH} characters."
            ),
        ))
        meta_data = MetaTagData(title=None, title_length=None)
        return TitleAuditResult(
            meta_data=meta_data,
            score=0.0,
            issues=issues,
            recommendations=recommendations,
        )

    title_length = len(title_text)

    # --- Rule: empty title ---
    if title_length == 0:
        issues.append(AuditIssue(
            rule_id="meta_title_empty",
            category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message="The <title> tag exists but is empty.",
            value="",
        ))
        recommendations.append(AuditRecommendation(
            rule_id="meta_title_empty",
            category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message=(
                f"Write a descriptive title between "
                f"{TITLE_MIN_LENGTH} and {TITLE_MAX_LENGTH} characters."
            ),
        ))
        meta_data = MetaTagData(title="", title_length=0)
        return TitleAuditResult(
            meta_data=meta_data,
            score=0.0,
            issues=issues,
            recommendations=recommendations,
        )

    # Title exists and is non-empty → earn presence points.
    score += TITLE_PRESENT_WEIGHT

    # --- Rule: too short ---
    if title_length < TITLE_MIN_LENGTH:
        issues.append(AuditIssue(
            rule_id="meta_title_too_short",
            category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=(
                f"Title is only {title_length} characters. "
                f"Recommended minimum is {TITLE_MIN_LENGTH}."
            ),
            value=title_text,
        ))
        recommendations.append(AuditRecommendation(
            rule_id="meta_title_too_short",
            category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=(
                f"Expand the title to at least {TITLE_MIN_LENGTH} characters "
                f"to improve search visibility."
            ),
        ))
        # Partial credit: proportional to how close to the minimum.
        score += TITLE_LENGTH_WEIGHT * (title_length / TITLE_MIN_LENGTH)

    # --- Rule: too long ---
    elif title_length > TITLE_MAX_LENGTH:
        issues.append(AuditIssue(
            rule_id="meta_title_too_long",
            category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=(
                f"Title is {title_length} characters. "
                f"Recommended maximum is {TITLE_MAX_LENGTH}. "
                f"It may be truncated in search results."
            ),
            value=title_text,
        ))
        recommendations.append(AuditRecommendation(
            rule_id="meta_title_too_long",
            category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=(
                f"Shorten the title to at most {TITLE_MAX_LENGTH} characters "
                f"to prevent truncation in search results."
            ),
        ))
        # Partial credit: deduct proportionally for excess length.
        excess_ratio = (title_length - TITLE_MAX_LENGTH) / TITLE_MAX_LENGTH
        penalty = min(excess_ratio, 1.0)
        score += TITLE_LENGTH_WEIGHT * (1.0 - penalty)

    # --- Rule: length OK ---
    else:
        issues.append(AuditIssue(
            rule_id="meta_title_ok",
            category=CategoryName.META,
            severity=SeverityLevel.PASS,
            message=(
                f"Title is {title_length} characters — "
                f"within the recommended range."
            ),
            value=title_text,
        ))
        score += TITLE_LENGTH_WEIGHT

    # Clamp score to [0, 100].
    score = round(max(0.0, min(100.0, score)), 1)

    meta_data = MetaTagData(
        title=title_text,
        title_length=title_length,
    )

    logger.info(
        "Title audit: '%s' (%d chars) → score %.1f, %d issue(s)",
        title_text[:50],
        title_length,
        score,
        len([i for i in issues if i.severity != SeverityLevel.PASS]),
    )

    return TitleAuditResult(
        meta_data=meta_data,
        score=score,
        issues=issues,
        recommendations=recommendations,
    )
