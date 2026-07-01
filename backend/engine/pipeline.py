"""Audit pipeline — orchestrates individual rule modules.

The pipeline receives rendered HTML and runs each registered audit
module, collecting issues, recommendations, scores, and raw data
into a unified :class:`AuditResponse`.
"""

from __future__ import annotations

import logging

from engine.rules.canonical import audit_canonical
from engine.rules.description import audit_description
from engine.rules.headings import audit_headings
from engine.rules.images import audit_images
from engine.rules.links import audit_links
from engine.rules.open_graph import audit_open_graph
from engine.rules.robots import audit_robots
from engine.rules.structured_data import audit_structured_data
from engine.rules.title import audit_title
from engine.rules.twitter_card import audit_twitter_card
from engine.scorer import compute_scores
from schemas.audit import AuditResponse, RedirectInfo
from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName
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
    html = render_result.html
    page_url = render_result.final_url

    all_issues: list[AuditIssue] = []
    all_recommendations: list[AuditRecommendation] = []
    category_scores: dict[CategoryName, list[float]] = {}

    def _collect(cat: CategoryName, score: float,
                 issues: list[AuditIssue],
                 recs: list[AuditRecommendation]) -> None:
        all_issues.extend(issues)
        all_recommendations.extend(recs)
        category_scores.setdefault(cat, []).append(score)

    # ------------------------------------------------------------------
    # 1. Title Tag
    # ------------------------------------------------------------------
    title_result = audit_title(html)
    _collect(CategoryName.META, title_result.score,
             title_result.issues, title_result.recommendations)

    # ------------------------------------------------------------------
    # 2. Meta Description
    # ------------------------------------------------------------------
    desc_result = audit_description(html)
    _collect(CategoryName.META, desc_result.score,
             desc_result.issues, desc_result.recommendations)

    # ------------------------------------------------------------------
    # 3. Canonical Tag
    # ------------------------------------------------------------------
    canonical_result = audit_canonical(html, page_url)
    _collect(CategoryName.META, canonical_result.score,
             canonical_result.issues, canonical_result.recommendations)

    # ------------------------------------------------------------------
    # 4. Heading Structure
    # ------------------------------------------------------------------
    headings_result = audit_headings(html)
    _collect(CategoryName.HEADINGS, headings_result.score,
             headings_result.issues, headings_result.recommendations)

    # ------------------------------------------------------------------
    # 5. Open Graph Tags
    # ------------------------------------------------------------------
    og_result = audit_open_graph(html)
    _collect(CategoryName.SOCIAL, og_result.score,
             og_result.issues, og_result.recommendations)

    # ------------------------------------------------------------------
    # 6. Twitter Card Tags
    # ------------------------------------------------------------------
    twitter_result = audit_twitter_card(html)
    _collect(CategoryName.SOCIAL, twitter_result.score,
             twitter_result.issues, twitter_result.recommendations)

    # ------------------------------------------------------------------
    # 7. Images & Alt Attributes
    # ------------------------------------------------------------------
    images_result = audit_images(html)
    _collect(CategoryName.IMAGES, images_result.score,
             images_result.issues, images_result.recommendations)

    # ------------------------------------------------------------------
    # 8. Internal & External Links
    # ------------------------------------------------------------------
    links_result = audit_links(html, page_url)
    _collect(CategoryName.LINKS, links_result.score,
             links_result.issues, links_result.recommendations)

    # ------------------------------------------------------------------
    # 9. Meta Robots / Robots Directives
    # ------------------------------------------------------------------
    robots_result = audit_robots(html)
    _collect(CategoryName.ROBOTS, robots_result.score,
             robots_result.issues, robots_result.recommendations)

    # ------------------------------------------------------------------
    # 10. Basic Structured Data detection
    # ------------------------------------------------------------------
    sd_result = audit_structured_data(html)
    _collect(CategoryName.STRUCTURED_DATA, sd_result.score,
             sd_result.issues, sd_result.recommendations)

    # ------------------------------------------------------------------
    # Build raw SEO data (merge results from all modules)
    # ------------------------------------------------------------------
    raw_data = RawSEOData()

    # Meta: merge title + description + canonical data
    raw_data.meta.title = title_result.meta_data.title
    raw_data.meta.title_length = title_result.meta_data.title_length
    raw_data.meta.description = desc_result.meta_data.description
    raw_data.meta.description_length = desc_result.meta_data.description_length
    raw_data.meta.canonical = canonical_result.meta_data.canonical

    raw_data.headings = headings_result.heading_data
    raw_data.open_graph = og_result.og_data
    raw_data.twitter_card = twitter_result.twitter_data
    raw_data.images = images_result.image_data
    raw_data.links = links_result.link_data
    raw_data.robots = robots_result.robots_data
    raw_data.structured_data = sd_result.structured_data

    # ------------------------------------------------------------------
    # Compute weighted scores via the scoring engine
    # ------------------------------------------------------------------
    scores = compute_scores(category_scores)

    # ------------------------------------------------------------------
    # Build redirect list
    # ------------------------------------------------------------------
    redirects = [
        RedirectInfo(url=r.url, status=r.status)
        for r in render_result.redirects
    ]

    logger.info(
        "Audit complete for %s → overall score: %.1f (%d categories)",
        render_result.final_url,
        scores.overall_score,
        len(scores.categories),
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
