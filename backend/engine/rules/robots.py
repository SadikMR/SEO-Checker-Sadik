"""Meta robots / robots directives audit rule module.

Rules:
    - robots_txt_blocked       — Page is blocked by robots.txt (critical)
    - robots_noindex           — Page has noindex directive (critical)
    - robots_nofollow          — Page has nofollow directive (warning)
    - robots_ok                — No blocking directives found (pass)
"""

from __future__ import annotations

import logging
import urllib.parse
import urllib.request
from dataclasses import dataclass
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import RobotsData

logger = logging.getLogger(__name__)

ROBOTS_TXT_TIMEOUT_S: int = 5


@dataclass
class RobotsAuditResult:
    robots_data: RobotsData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_meta_robots(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", attrs={"name": "robots"})
    if tag:
        return (tag.get("content") or "").strip() or None
    return None


def _check_robots_txt(page_url: str) -> bool:
    """Return True if the page is disallowed by robots.txt for Googlebot."""
    try:
        parsed = urllib.parse.urlparse(page_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser(robots_url)
        rp.set_url(robots_url)
        rp.read()
        allowed = rp.can_fetch("Googlebot", page_url)
        return not allowed
    except Exception as exc:
        logger.debug("Could not fetch robots.txt for %s: %s", page_url, exc)
        return False


def audit_robots(
    html: str,
    page_url: str = "",
    x_robots_tag: str | None = None,
) -> RobotsAuditResult:
    meta_robots = _extract_meta_robots(html)
    robots_txt_disallowed = _check_robots_txt(page_url) if page_url else False

    data = RobotsData(
        meta_robots=meta_robots,
        x_robots_tag=x_robots_tag,
        robots_txt_disallowed=robots_txt_disallowed,
    )

    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 100.0

    # robots.txt check
    if robots_txt_disallowed:
        score = 0.0
        issues.append(AuditIssue(
            rule_id="robots_txt_blocked", category=CategoryName.ROBOTS,
            severity=SeverityLevel.CRITICAL,
            message="This page is disallowed by robots.txt for Googlebot.",
            value=page_url,
        ))
        recs.append(AuditRecommendation(
            rule_id="robots_txt_blocked", category=CategoryName.ROBOTS,
            severity=SeverityLevel.CRITICAL,
            message="Update robots.txt to allow Googlebot access to this page if you want it indexed.",
        ))

    # Combine meta + header directives
    all_directives: list[str] = []
    if meta_robots:
        all_directives.extend(d.strip().lower() for d in meta_robots.split(","))
    if x_robots_tag:
        all_directives.extend(d.strip().lower() for d in x_robots_tag.split(","))

    if "noindex" in all_directives:
        score = 0.0
        issues.append(AuditIssue(
            rule_id="robots_noindex", category=CategoryName.ROBOTS,
            severity=SeverityLevel.CRITICAL,
            message="Page has a 'noindex' directive — it will not appear in search results.",
            value=meta_robots or x_robots_tag,
        ))
        recs.append(AuditRecommendation(
            rule_id="robots_noindex", category=CategoryName.ROBOTS,
            severity=SeverityLevel.CRITICAL,
            message="Remove the 'noindex' directive if you want this page indexed by search engines.",
        ))

    if "nofollow" in all_directives:
        score = min(score, 50.0)
        issues.append(AuditIssue(
            rule_id="robots_nofollow", category=CategoryName.ROBOTS,
            severity=SeverityLevel.WARNING,
            message="Page has a 'nofollow' directive — search engines will not follow links on this page.",
            value=meta_robots or x_robots_tag,
        ))
        recs.append(AuditRecommendation(
            rule_id="robots_nofollow", category=CategoryName.ROBOTS,
            severity=SeverityLevel.WARNING,
            message="Remove the 'nofollow' directive if you want search engines to follow links.",
        ))

    if not issues:
        issues.append(AuditIssue(
            rule_id="robots_ok", category=CategoryName.ROBOTS,
            severity=SeverityLevel.PASS,
            message="No blocking robots directives found.",
        ))

    score = round(max(0.0, min(100.0, score)), 1)
    logger.info("Robots audit: meta=%s, txt_blocked=%s → score %.1f",
                meta_robots, robots_txt_disallowed, score)
    return RobotsAuditResult(
        robots_data=data, score=score, issues=issues, recommendations=recs,
    )
