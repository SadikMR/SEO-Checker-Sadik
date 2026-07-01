"""Audit request and response schemas.

These are the top-level models for the ``POST /audit`` endpoint as
defined in the specification (§8).
"""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import ScoreSummary
from schemas.seo_data import RawSEOData


# ------------------------------------------------------------------
# Request
# ------------------------------------------------------------------


class AuditRequest(BaseModel):
    """Request body for the ``POST /audit`` endpoint."""

    url: HttpUrl = Field(
        ...,
        description="The publicly accessible URL to audit. "
        "Must use http or https.",
    )

    model_config = {"json_schema_extra": {"examples": [
        {"url": "https://example.com"}
    ]}}


# ------------------------------------------------------------------
# Redirect entry (matches renderer.RedirectEntry shape)
# ------------------------------------------------------------------


class RedirectInfo(BaseModel):
    """A single hop in a redirect chain."""

    url: str = Field(..., description="URL of this redirect hop.")
    status: int = Field(..., description="HTTP status code of the redirect.")


# ------------------------------------------------------------------
# Response
# ------------------------------------------------------------------


class AuditResponse(BaseModel):
    """Complete audit result returned by ``POST /audit``.

    The structure mirrors the API contract in the specification:
    ``input_url``, ``final_url``, ``redirects``, ``scores``,
    ``results`` (issues), ``recommendations``, and ``raw_data``.
    """

    input_url: str = Field(
        ..., description="The original URL submitted for audit."
    )
    final_url: str = Field(
        ...,
        description="The URL after following all redirects.",
    )
    redirects: list[RedirectInfo] = Field(
        default_factory=list,
        description="Ordered list of redirect hops, if any.",
    )
    scores: ScoreSummary = Field(
        ..., description="Overall and per-category score breakdown."
    )
    results: list[AuditIssue] = Field(
        default_factory=list,
        description="List of issues discovered during the audit.",
    )
    recommendations: list[AuditRecommendation] = Field(
        default_factory=list,
        description="Actionable recommendations for each issue.",
    )
    raw_data: RawSEOData = Field(
        ..., description="Raw extracted SEO data from the rendered page."
    )

    model_config = {"json_schema_extra": {"examples": [
        {
            "input_url": "https://example.com",
            "final_url": "https://www.example.com",
            "redirects": [
                {"url": "https://example.com", "status": 301}
            ],
            "scores": {
                "overall_score": 72.5,
                "categories": [
                    {
                        "category": "meta",
                        "score": 85.0,
                        "max_score": 100,
                        "label": "Meta Tags",
                    }
                ],
            },
            "results": [
                {
                    "rule_id": "meta_description_too_short",
                    "category": "meta",
                    "severity": "warning",
                    "message": "Meta description is only 45 characters.",
                    "value": "Short description here.",
                }
            ],
            "recommendations": [
                {
                    "rule_id": "meta_description_too_short",
                    "category": "meta",
                    "severity": "warning",
                    "message": "Write a meta description between 120 and 160 characters.",
                }
            ],
            "raw_data": {
                "meta": {
                    "title": "Example Domain",
                    "title_length": 14,
                    "description": "Short description here.",
                    "description_length": 45,
                    "canonical": "https://www.example.com",
                },
                "headings": {"h1": ["Example Domain"], "h1_count": 1},
                "open_graph": {},
                "twitter_card": {},
                "images": {"total_images": 0},
                "links": {"total_links": 1, "internal_links": 0, "external_links": 1},
                "robots": {},
            },
        }
    ]}}


# ------------------------------------------------------------------
# Error response (for consistent API error payloads)
# ------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Structured error payload returned on 4xx / 5xx responses."""

    detail: str = Field(
        ..., description="Human-readable error message."
    )
    error_code: str | None = Field(
        None,
        description="Machine-readable error code "
        "(e.g. 'INVALID_URL', 'RENDER_TIMEOUT').",
    )
