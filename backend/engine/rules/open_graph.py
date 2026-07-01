"""Open Graph tags audit rule module.

Rules:
    - og_missing           — No OG tags found at all (warning)
    - og_title_missing     — og:title missing (warning)
    - og_description_missing — og:description missing (warning)
    - og_image_missing     — og:image missing (warning)
    - og_complete          — All key OG tags present (pass)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import OpenGraphData

logger = logging.getLogger(__name__)

REQUIRED_OG_FIELDS = ["og_title", "og_description", "og_image"]
FIELD_WEIGHT: float = 100.0 / len(REQUIRED_OG_FIELDS)


@dataclass
class OpenGraphAuditResult:
    og_data: OpenGraphData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_og(html: str) -> OpenGraphData:
    soup = BeautifulSoup(html, "html.parser")
    mapping = {
        "og_title": "og:title",
        "og_description": "og:description",
        "og_image": "og:image",
        "og_url": "og:url",
        "og_type": "og:type",
        "og_site_name": "og:site_name",
    }
    data = {}
    for field, prop in mapping.items():
        tag = soup.find("meta", attrs={"property": prop})
        data[field] = (tag.get("content") or "").strip() if tag else None
    return OpenGraphData(**data)


def audit_open_graph(html: str) -> OpenGraphAuditResult:
    og = _extract_og(html)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    found_any = any(getattr(og, f) for f in REQUIRED_OG_FIELDS)

    if not found_any:
        issues.append(AuditIssue(
            rule_id="og_missing", category=CategoryName.SOCIAL,
            severity=SeverityLevel.WARNING,
            message="No Open Graph tags found on this page.",
        ))
        recs.append(AuditRecommendation(
            rule_id="og_missing", category=CategoryName.SOCIAL,
            severity=SeverityLevel.WARNING,
            message="Add Open Graph meta tags (og:title, og:description, og:image) to improve social sharing.",
        ))
        return OpenGraphAuditResult(
            og_data=og, score=0.0, issues=issues, recommendations=recs,
        )

    label_map = {
        "og_title": ("og:title", "Add an og:title tag for social sharing previews."),
        "og_description": ("og:description", "Add an og:description tag for social sharing previews."),
        "og_image": ("og:image", "Add an og:image tag to display an image when shared on social media."),
    }

    all_present = True
    for field in REQUIRED_OG_FIELDS:
        value = getattr(og, field)
        prop_name, rec_msg = label_map[field]
        if not value:
            all_present = False
            issues.append(AuditIssue(
                rule_id=f"{field}_missing", category=CategoryName.SOCIAL,
                severity=SeverityLevel.WARNING,
                message=f"Missing {prop_name} tag.",
            ))
            recs.append(AuditRecommendation(
                rule_id=f"{field}_missing", category=CategoryName.SOCIAL,
                severity=SeverityLevel.WARNING,
                message=rec_msg,
            ))
        else:
            score += FIELD_WEIGHT

    if all_present:
        issues.append(AuditIssue(
            rule_id="og_complete", category=CategoryName.SOCIAL,
            severity=SeverityLevel.PASS,
            message="All key Open Graph tags are present.",
        ))

    score = round(max(0.0, min(100.0, score)), 1)
    logger.info("OG audit: score %.1f", score)
    return OpenGraphAuditResult(
        og_data=og, score=score, issues=issues, recommendations=recs,
    )
