"""Meta description audit rule module.

Rules:
    - meta_desc_missing      — No meta description found (critical)
    - meta_desc_empty        — Meta description exists but is empty (critical)
    - meta_desc_too_short    — Shorter than 120 characters (warning)
    - meta_desc_too_long     — Longer than 160 characters (warning)
    - meta_desc_ok           — Length within recommended range (pass)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import MetaTagData

logger = logging.getLogger(__name__)

DESC_MIN_LENGTH: int = 120
DESC_MAX_LENGTH: int = 160

PRESENCE_WEIGHT: float = 50.0
LENGTH_WEIGHT: float = 50.0


@dataclass
class DescriptionAuditResult:
    meta_data: MetaTagData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_description(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", attrs={"name": "description"})
    if tag is None:
        return None
    return (tag.get("content") or "").strip()


def audit_description(html: str) -> DescriptionAuditResult:
    desc = _extract_description(html)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    if desc is None:
        issues.append(AuditIssue(
            rule_id="meta_desc_missing", category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message="Page is missing a meta description tag.",
        ))
        recs.append(AuditRecommendation(
            rule_id="meta_desc_missing", category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message=f"Add a meta description between {DESC_MIN_LENGTH} and {DESC_MAX_LENGTH} characters.",
        ))
        return DescriptionAuditResult(
            meta_data=MetaTagData(), score=0.0, issues=issues, recommendations=recs,
        )

    desc_len = len(desc)

    if desc_len == 0:
        issues.append(AuditIssue(
            rule_id="meta_desc_empty", category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message="Meta description tag exists but is empty.", value="",
        ))
        recs.append(AuditRecommendation(
            rule_id="meta_desc_empty", category=CategoryName.META,
            severity=SeverityLevel.CRITICAL,
            message=f"Write a compelling meta description between {DESC_MIN_LENGTH} and {DESC_MAX_LENGTH} characters.",
        ))
        return DescriptionAuditResult(
            meta_data=MetaTagData(description="", description_length=0),
            score=0.0, issues=issues, recommendations=recs,
        )

    score += PRESENCE_WEIGHT

    if desc_len < DESC_MIN_LENGTH:
        issues.append(AuditIssue(
            rule_id="meta_desc_too_short", category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=f"Meta description is only {desc_len} characters. Recommended minimum is {DESC_MIN_LENGTH}.",
            value=desc,
        ))
        recs.append(AuditRecommendation(
            rule_id="meta_desc_too_short", category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=f"Expand the meta description to at least {DESC_MIN_LENGTH} characters.",
        ))
        score += LENGTH_WEIGHT * (desc_len / DESC_MIN_LENGTH)
    elif desc_len > DESC_MAX_LENGTH:
        issues.append(AuditIssue(
            rule_id="meta_desc_too_long", category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=f"Meta description is {desc_len} characters. Recommended maximum is {DESC_MAX_LENGTH}.",
            value=desc,
        ))
        recs.append(AuditRecommendation(
            rule_id="meta_desc_too_long", category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message=f"Shorten the meta description to at most {DESC_MAX_LENGTH} characters.",
        ))
        excess = (desc_len - DESC_MAX_LENGTH) / DESC_MAX_LENGTH
        score += LENGTH_WEIGHT * (1.0 - min(excess, 1.0))
    else:
        issues.append(AuditIssue(
            rule_id="meta_desc_ok", category=CategoryName.META,
            severity=SeverityLevel.PASS,
            message=f"Meta description is {desc_len} characters — within the recommended range.",
            value=desc,
        ))
        score += LENGTH_WEIGHT

    score = round(max(0.0, min(100.0, score)), 1)

    meta_data = MetaTagData(description=desc, description_length=desc_len)

    logger.info("Description audit: %d chars → score %.1f", desc_len, score)
    return DescriptionAuditResult(
        meta_data=meta_data, score=score, issues=issues, recommendations=recs,
    )
