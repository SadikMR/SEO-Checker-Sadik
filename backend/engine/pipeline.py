"""Audit pipeline — orchestrates individual rule modules.

The pipeline receives rendered HTML and runs each registered audit
module, collecting issues, recommendations, scores, and raw data
into a unified :class:`AuditResponse`.
"""

from __future__ import annotations

import logging

from engine.rules.title import audit_title
from schemas.audit import AuditResponse, RedirectInfo
from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, CategoryScore, ScoreSummary
from schemas.seo_data import RawSEOData
from services.renderer import RenderResult

logger = logging.getLogger(__name__)


def run_audit(render_result: RenderResult) -> AuditResponse:
    """Execute all registered audit modules against a rendered page.

    Args:
        render_result: The output from the page renderer containing
            the fully rendered HTML, final URL, and redirect chain.

    Returns:
        A complete :class:`AuditResponse` ready to be serialised.
    """
    all_issues: list[AuditIssue] = []
    all_recommendations: list[AuditRecommendation] = []
    category_scores: dict[CategoryName, float] = {}

    # ------------------------------------------------------------------
    # 1. Title Tag audit
    # ------------------------------------------------------------------
    title_result = audit_title(render_result.html)
    all_issues.extend(title_result.issues)
    all_recommendations.extend(title_result.recommendations)
    category_scores[CategoryName.META] = title_result.score

    # ------------------------------------------------------------------
    # Build raw SEO data (merge results from all modules)
    # ------------------------------------------------------------------
    raw_data = RawSEOData()
    raw_data.meta = title_result.meta_data

    # ------------------------------------------------------------------
    # Build category score list and compute overall score
    # ------------------------------------------------------------------
    category_labels: dict[CategoryName, str] = {
        CategoryName.META: "Meta Tags",
        CategoryName.HEADINGS: "Headings",
        CategoryName.IMAGES: "Images",
        CategoryName.LINKS: "Links",
        CategoryName.SOCIAL: "Social Tags",
        CategoryName.ROBOTS: "Robots",
    }

    scored_categories: list[CategoryScore] = []
    for cat, score_val in category_scores.items():
        scored_categories.append(CategoryScore(
            category=cat,
            score=score_val,
            max_score=100.0,
            label=category_labels.get(cat, cat.value),
        ))

    # Overall score = average of all category scores that have been evaluated.
    if scored_categories:
        overall = round(
            sum(c.score for c in scored_categories) / len(scored_categories),
            1,
        )
    else:
        overall = 0.0

    scores = ScoreSummary(
        overall_score=overall,
        categories=scored_categories,
    )

    # ------------------------------------------------------------------
    # Build redirect list
    # ------------------------------------------------------------------
    redirects = [
        RedirectInfo(url=r.url, status=r.status)
        for r in render_result.redirects
    ]

    logger.info(
        "Audit complete for %s → overall score: %.1f",
        render_result.final_url,
        overall,
    )

    return AuditResponse(
        input_url=render_result.input_url,
        final_url=render_result.final_url,
        redirects=redirects,
        scores=scores,
        results=all_issues,
        recommendations=all_recommendations,
        raw_data=raw_data,
    )
