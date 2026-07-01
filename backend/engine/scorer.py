"""SEO scoring engine.

Computes weighted category scores and the overall SEO score from raw
module results.

Scoring methodology
-------------------
Each audit *category* has a relative **weight** that reflects its
importance to search engine optimisation.  The weights are defined
in ``CATEGORY_WEIGHTS`` and must sum to exactly 1.0.

Within a category that contains multiple audit modules (e.g. META
contains Title + Description + Canonical), the individual module
scores are averaged first to produce the single category score.

The **overall score** is then the sum of each category score
multiplied by its weight, clamped to [0, 100].

Extending the engine
--------------------
- To change relative importance: edit ``CATEGORY_WEIGHTS``.
- To add a new category: add it to ``CategoryName`` and give it a
  weight here (then normalise so all weights still sum to 1.0).
- The pipeline does NOT need to change — it just passes module
  scores here and gets a ``ScoreSummary`` back.
"""

from __future__ import annotations

import logging

from schemas.scores import CategoryName, CategoryScore, ScoreSummary

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Category weights — must sum to 1.0
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS: dict[CategoryName, float] = {
    CategoryName.META: 0.30,           # Title, description, canonical — core on-page signals
    CategoryName.HEADINGS: 0.15,       # H1 + structure — important for relevance
    CategoryName.IMAGES: 0.10,         # Alt attributes — accessibility + SEO
    CategoryName.LINKS: 0.10,          # Internal/external link health
    CategoryName.SOCIAL: 0.15,         # OG + Twitter Card — social & CTR signals
    CategoryName.ROBOTS: 0.10,         # Indexability — binary but critical
    CategoryName.STRUCTURED_DATA: 0.10,  # JSON-LD / Microdata — rich result eligibility
}

_WEIGHT_SUM = sum(CATEGORY_WEIGHTS.values())
assert abs(_WEIGHT_SUM - 1.0) < 1e-9, (
    f"CATEGORY_WEIGHTS must sum to 1.0, got {_WEIGHT_SUM}"
)

CATEGORY_LABELS: dict[CategoryName, str] = {
    CategoryName.META: "Meta Tags",
    CategoryName.HEADINGS: "Headings",
    CategoryName.IMAGES: "Images",
    CategoryName.LINKS: "Links",
    CategoryName.SOCIAL: "Social Tags",
    CategoryName.ROBOTS: "Robots",
    CategoryName.STRUCTURED_DATA: "Structured Data",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_scores(
    raw_category_scores: dict[CategoryName, list[float]],
) -> ScoreSummary:
    """Compute category scores and the weighted overall SEO score.

    Args:
        raw_category_scores: A mapping from each category to a list of
            scores produced by its audit modules (0–100 each).

    Returns:
        A :class:`ScoreSummary` with per-category scores and the
        weighted overall score.
    """
    scored_categories: list[CategoryScore] = []
    weighted_sum: float = 0.0
    total_weight: float = 0.0

    for category, weight in CATEGORY_WEIGHTS.items():
        module_scores = raw_category_scores.get(category)

        if not module_scores:
            # Category was evaluated but produced no scores — treat as 0
            # so it still factors into the overall score.
            # Categories not present in raw_category_scores are skipped.
            continue

        # Average the individual module scores within this category.
        category_score = round(sum(module_scores) / len(module_scores), 1)

        scored_categories.append(CategoryScore(
            category=category,
            score=category_score,
            max_score=100.0,
            label=CATEGORY_LABELS.get(category, category.value),
        ))

        weighted_sum += category_score * weight
        total_weight += weight

    # weighted_sum = Σ(category_score × weight)
    # category_score ∈ [0, 100], weight ∈ [0, 1]
    # → weighted_sum ∈ [0, 100] when all weights are present.
    # Dividing by total_weight (< 1.0 when some categories absent)
    # redistributes their weight to evaluated categories proportionally.
    if total_weight > 0:
        overall = round(
            max(0.0, min(100.0, weighted_sum / total_weight)),
            1,
        )
    else:
        overall = 0.0

    logger.info(
        "Score computation: overall=%.1f (%d categories, total_weight=%.2f)",
        overall,
        len(scored_categories),
        total_weight,
    )

    return ScoreSummary(overall_score=overall, categories=scored_categories)
