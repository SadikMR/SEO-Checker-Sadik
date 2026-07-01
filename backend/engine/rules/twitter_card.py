"""Twitter Card tags audit rule module.

Rules:
    - twitter_card_missing        — No Twitter Card tags found (warning)
    - twitter_card_type_missing   — twitter:card missing (warning)
    - twitter_card_title_missing  — twitter:title missing (warning)
    - twitter_card_desc_missing   — twitter:description missing (warning)
    - twitter_card_complete       — All key tags present (pass)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import TwitterCardData

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["card", "title", "description"]
FIELD_WEIGHT: float = 100.0 / len(REQUIRED_FIELDS)


@dataclass
class TwitterCardAuditResult:
    twitter_data: TwitterCardData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_twitter(html: str) -> TwitterCardData:
    soup = BeautifulSoup(html, "html.parser")
    mapping = {
        "card": "twitter:card",
        "title": "twitter:title",
        "description": "twitter:description",
        "image": "twitter:image",
        "site": "twitter:site",
    }
    data = {}
    for field, name in mapping.items():
        tag = soup.find("meta", attrs={"name": name})
        if tag is None:
            tag = soup.find("meta", attrs={"property": name})
        data[field] = (tag.get("content") or "").strip() if tag else None
    return TwitterCardData(**data)


def audit_twitter_card(html: str) -> TwitterCardAuditResult:
    tc = _extract_twitter(html)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    found_any = any(getattr(tc, f) for f in REQUIRED_FIELDS)

    if not found_any:
        issues.append(AuditIssue(
            rule_id="twitter_card_missing", category=CategoryName.SOCIAL,
            severity=SeverityLevel.WARNING,
            message="No Twitter Card tags found on this page.",
        ))
        recs.append(AuditRecommendation(
            rule_id="twitter_card_missing", category=CategoryName.SOCIAL,
            severity=SeverityLevel.WARNING,
            message="Add Twitter Card meta tags (twitter:card, twitter:title, twitter:description) for better Twitter sharing.",
        ))
        return TwitterCardAuditResult(
            twitter_data=tc, score=0.0, issues=issues, recommendations=recs,
        )

    label_map = {
        "card": ("twitter:card", "Add a twitter:card tag (e.g. 'summary_large_image')."),
        "title": ("twitter:title", "Add a twitter:title tag for Twitter sharing previews."),
        "description": ("twitter:description", "Add a twitter:description tag for Twitter sharing previews."),
    }

    all_present = True
    for field in REQUIRED_FIELDS:
        value = getattr(tc, field)
        prop_name, rec_msg = label_map[field]
        if not value:
            all_present = False
            issues.append(AuditIssue(
                rule_id=f"twitter_card_{field}_missing", category=CategoryName.SOCIAL,
                severity=SeverityLevel.WARNING,
                message=f"Missing {prop_name} tag.",
            ))
            recs.append(AuditRecommendation(
                rule_id=f"twitter_card_{field}_missing", category=CategoryName.SOCIAL,
                severity=SeverityLevel.WARNING,
                message=rec_msg,
            ))
        else:
            score += FIELD_WEIGHT

    if all_present:
        issues.append(AuditIssue(
            rule_id="twitter_card_complete", category=CategoryName.SOCIAL,
            severity=SeverityLevel.PASS,
            message="All key Twitter Card tags are present.",
        ))

    score = round(max(0.0, min(100.0, score)), 1)
    logger.info("Twitter Card audit: score %.1f", score)
    return TwitterCardAuditResult(
        twitter_data=tc, score=score, issues=issues, recommendations=recs,
    )
