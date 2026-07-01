"""Reusable score and category models for the audit engine.

These models represent the scoring breakdown returned in audit results.
They are used across the audit response and the scoring engine.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Severity classification for audit findings."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    PASS = "pass"


class CategoryName(str, Enum):
    """Standardised audit category identifiers.

    Each category groups related SEO checks so the frontend can
    display per-category score cards and breakdowns.
    """

    META = "meta"
    HEADINGS = "headings"
    IMAGES = "images"
    LINKS = "links"
    SOCIAL = "social"
    ROBOTS = "robots"


class CategoryScore(BaseModel):
    """Score for a single audit category."""

    category: CategoryName = Field(
        ..., description="The audit category this score belongs to."
    )
    score: float = Field(
        ..., ge=0, le=100, description="Category score from 0 to 100."
    )
    max_score: float = Field(
        100, ge=0, description="Maximum achievable score for this category."
    )
    label: str = Field(
        ...,
        description="Human-readable category label (e.g. 'Meta Tags').",
    )

    model_config = {"json_schema_extra": {"examples": [
        {
            "category": "meta",
            "score": 85.0,
            "max_score": 100,
            "label": "Meta Tags",
        }
    ]}}


class ScoreSummary(BaseModel):
    """Top-level scoring summary for an audit."""

    overall_score: float = Field(
        ..., ge=0, le=100, description="Aggregate SEO score from 0 to 100."
    )
    categories: list[CategoryScore] = Field(
        default_factory=list,
        description="Per-category score breakdown.",
    )
