"""Heading structure audit rule module.

Rules:
    - h1_missing           — No H1 tag found (critical)
    - h1_multiple          — Multiple H1 tags found (warning)
    - h1_ok                — Exactly one H1 tag (pass)
    - headings_hierarchy   — Skipped heading levels (info)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import HeadingData

logger = logging.getLogger(__name__)

H1_WEIGHT: float = 60.0
HIERARCHY_WEIGHT: float = 40.0


@dataclass
class HeadingsAuditResult:
    heading_data: HeadingData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_headings(html: str) -> HeadingData:
    soup = BeautifulSoup(html, "html.parser")
    data = HeadingData()
    for level in range(1, 7):
        tag_name = f"h{level}"
        texts = [tag.get_text(strip=True) for tag in soup.find_all(tag_name)]
        setattr(data, tag_name, texts)
    data.h1_count = len(data.h1)
    return data


def _check_hierarchy(data: HeadingData) -> list[str]:
    """Return list of skipped heading levels."""
    levels_present: set[int] = set()
    for level in range(1, 7):
        if getattr(data, f"h{level}"):
            levels_present.add(level)
    if not levels_present:
        return []

    skipped: list[str] = []
    max_level = max(levels_present)
    for level in range(1, max_level + 1):
        if level not in levels_present:
            skipped.append(f"H{level}")
    return skipped


def audit_headings(html: str) -> HeadingsAuditResult:
    data = _extract_headings(html)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    # H1 checks
    if data.h1_count == 0:
        issues.append(AuditIssue(
            rule_id="h1_missing", category=CategoryName.HEADINGS,
            severity=SeverityLevel.CRITICAL,
            message="Page is missing an H1 heading.",
        ))
        recs.append(AuditRecommendation(
            rule_id="h1_missing", category=CategoryName.HEADINGS,
            severity=SeverityLevel.CRITICAL,
            message="Add exactly one H1 heading that describes the page's main topic.",
        ))
    elif data.h1_count > 1:
        issues.append(AuditIssue(
            rule_id="h1_multiple", category=CategoryName.HEADINGS,
            severity=SeverityLevel.WARNING,
            message=f"Page has {data.h1_count} H1 headings. Best practice is exactly one.",
            value="; ".join(data.h1),
        ))
        recs.append(AuditRecommendation(
            rule_id="h1_multiple", category=CategoryName.HEADINGS,
            severity=SeverityLevel.WARNING,
            message="Use only one H1 heading per page. Demote extras to H2 or lower.",
        ))
        score += H1_WEIGHT * 0.5
    else:
        issues.append(AuditIssue(
            rule_id="h1_ok", category=CategoryName.HEADINGS,
            severity=SeverityLevel.PASS,
            message="Page has exactly one H1 heading.",
            value=data.h1[0],
        ))
        score += H1_WEIGHT

    # Hierarchy check
    skipped = _check_hierarchy(data)
    if skipped:
        issues.append(AuditIssue(
            rule_id="headings_hierarchy", category=CategoryName.HEADINGS,
            severity=SeverityLevel.INFO,
            message=f"Heading hierarchy skips levels: {', '.join(skipped)}.",
            value=", ".join(skipped),
        ))
        recs.append(AuditRecommendation(
            rule_id="headings_hierarchy", category=CategoryName.HEADINGS,
            severity=SeverityLevel.INFO,
            message="Use a sequential heading hierarchy (H1 → H2 → H3) without skipping levels.",
        ))
        score += HIERARCHY_WEIGHT * 0.5
    else:
        score += HIERARCHY_WEIGHT

    score = round(max(0.0, min(100.0, score)), 1)
    logger.info("Headings audit: H1=%d → score %.1f", data.h1_count, score)
    return HeadingsAuditResult(
        heading_data=data, score=score, issues=issues, recommendations=recs,
    )
