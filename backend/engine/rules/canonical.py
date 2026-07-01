"""Canonical tag audit rule module.

Rules:
    - canonical_missing    — No canonical link found (warning)
    - canonical_present    — Canonical tag found (pass)
    - canonical_mismatch   — Canonical URL differs from page URL (info)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import MetaTagData

logger = logging.getLogger(__name__)


@dataclass
class CanonicalAuditResult:
    meta_data: MetaTagData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_canonical(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("link", attrs={"rel": "canonical"})
    if tag is None:
        return None
    return (tag.get("href") or "").strip() or None


def audit_canonical(html: str, page_url: str) -> CanonicalAuditResult:
    canonical = _extract_canonical(html)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    if canonical is None:
        issues.append(AuditIssue(
            rule_id="canonical_missing", category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message="Page is missing a canonical link tag.",
        ))
        recs.append(AuditRecommendation(
            rule_id="canonical_missing", category=CategoryName.META,
            severity=SeverityLevel.WARNING,
            message="Add a <link rel='canonical'> tag pointing to the preferred URL for this page.",
        ))
        return CanonicalAuditResult(
            meta_data=MetaTagData(), score=0.0, issues=issues, recommendations=recs,
        )

    score = 100.0
    issues.append(AuditIssue(
        rule_id="canonical_present", category=CategoryName.META,
        severity=SeverityLevel.PASS,
        message=f"Canonical tag found: {canonical}",
        value=canonical,
    ))

    # Informational: check for mismatch with page URL
    if canonical.rstrip("/") != page_url.rstrip("/"):
        issues.append(AuditIssue(
            rule_id="canonical_mismatch", category=CategoryName.META,
            severity=SeverityLevel.INFO,
            message=f"Canonical URL ({canonical}) differs from the page URL ({page_url}).",
            value=canonical,
        ))

    meta_data = MetaTagData(canonical=canonical)
    logger.info("Canonical audit: '%s' → score %.1f", canonical, score)
    return CanonicalAuditResult(
        meta_data=meta_data, score=score, issues=issues, recommendations=recs,
    )
