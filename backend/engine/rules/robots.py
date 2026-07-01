"""Meta robots / robots directives audit rule module.

Rules:
    - robots_noindex           — Page has noindex directive (critical)
    - robots_nofollow          — Page has nofollow directive (warning)
    - robots_ok                — No blocking directives found (pass)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import RobotsData

logger = logging.getLogger(__name__)


@dataclass
class RobotsAuditResult:
    robots_data: RobotsData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_robots(html: str) -> RobotsData:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", attrs={"name": "robots"})
    meta_robots = None
    if tag:
        meta_robots = (tag.get("content") or "").strip() or None
    return RobotsData(meta_robots=meta_robots)


def audit_robots(html: str, x_robots_tag: str | None = None) -> RobotsAuditResult:
    data = _extract_robots(html)
    data.x_robots_tag = x_robots_tag

    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 100.0

    # Combine all directives
    all_directives: list[str] = []
    if data.meta_robots:
        all_directives.extend(
            d.strip().lower() for d in data.meta_robots.split(",")
        )
    if data.x_robots_tag:
        all_directives.extend(
            d.strip().lower() for d in data.x_robots_tag.split(",")
        )

    if "noindex" in all_directives:
        score = 0.0
        issues.append(AuditIssue(
            rule_id="robots_noindex", category=CategoryName.ROBOTS,
            severity=SeverityLevel.CRITICAL,
            message="Page has a 'noindex' directive — it will not appear in search results.",
            value=data.meta_robots or data.x_robots_tag,
        ))
        recs.append(AuditRecommendation(
            rule_id="robots_noindex", category=CategoryName.ROBOTS,
            severity=SeverityLevel.CRITICAL,
            message="Remove the 'noindex' directive if you want this page to be indexed by search engines.",
        ))

    if "nofollow" in all_directives:
        score = min(score, 50.0)
        issues.append(AuditIssue(
            rule_id="robots_nofollow", category=CategoryName.ROBOTS,
            severity=SeverityLevel.WARNING,
            message="Page has a 'nofollow' directive — search engines will not follow links on this page.",
            value=data.meta_robots or data.x_robots_tag,
        ))
        recs.append(AuditRecommendation(
            rule_id="robots_nofollow", category=CategoryName.ROBOTS,
            severity=SeverityLevel.WARNING,
            message="Remove the 'nofollow' directive if you want search engines to follow links on this page.",
        ))

    if not issues:
        issues.append(AuditIssue(
            rule_id="robots_ok", category=CategoryName.ROBOTS,
            severity=SeverityLevel.PASS,
            message="No blocking robots directives found.",
        ))

    score = round(max(0.0, min(100.0, score)), 1)
    logger.info("Robots audit: directives=%s → score %.1f", all_directives, score)
    return RobotsAuditResult(
        robots_data=data, score=score, issues=issues, recommendations=recs,
    )
