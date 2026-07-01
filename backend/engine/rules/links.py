"""Internal & external links audit rule module.

Rules:
    - links_none_found        — No links found on the page (info)
    - links_no_internal       — No internal links found (warning)
    - links_no_external       — No external links found (info)
    - links_ok                — Both internal and external links present (pass)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import LinkData

logger = logging.getLogger(__name__)

INTERNAL_WEIGHT: float = 60.0
EXTERNAL_WEIGHT: float = 40.0


@dataclass
class LinksAuditResult:
    link_data: LinkData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_links(html: str, page_url: str) -> LinkData:
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.find_all("a", href=True)

    page_domain = urlparse(page_url).netloc.lower()
    internal = 0
    external = 0
    nofollow = 0

    for a in anchors:
        href = a.get("href", "").strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue

        rel = (a.get("rel") or [])
        if isinstance(rel, str):
            rel = rel.split()
        if "nofollow" in [r.lower() for r in rel]:
            nofollow += 1

        parsed = urlparse(href)
        link_domain = parsed.netloc.lower()

        if not link_domain or link_domain == page_domain:
            internal += 1
        else:
            external += 1

    return LinkData(
        total_links=internal + external,
        internal_links=internal,
        external_links=external,
        nofollow_links=nofollow,
    )


def audit_links(html: str, page_url: str) -> LinksAuditResult:
    data = _extract_links(html, page_url)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    if data.total_links == 0:
        issues.append(AuditIssue(
            rule_id="links_none_found", category=CategoryName.LINKS,
            severity=SeverityLevel.INFO,
            message="No links found on this page.",
        ))
        recs.append(AuditRecommendation(
            rule_id="links_none_found", category=CategoryName.LINKS,
            severity=SeverityLevel.INFO,
            message="Add internal links to improve site navigation and help search engines discover content.",
        ))
        return LinksAuditResult(
            link_data=data, score=50.0, issues=issues, recommendations=recs,
        )

    # Internal links
    if data.internal_links == 0:
        issues.append(AuditIssue(
            rule_id="links_no_internal", category=CategoryName.LINKS,
            severity=SeverityLevel.WARNING,
            message="No internal links found on this page.",
        ))
        recs.append(AuditRecommendation(
            rule_id="links_no_internal", category=CategoryName.LINKS,
            severity=SeverityLevel.WARNING,
            message="Add internal links to help users and search engines navigate your site.",
        ))
    else:
        score += INTERNAL_WEIGHT

    # External links
    if data.external_links == 0:
        issues.append(AuditIssue(
            rule_id="links_no_external", category=CategoryName.LINKS,
            severity=SeverityLevel.INFO,
            message="No external links found on this page.",
        ))
    else:
        score += EXTERNAL_WEIGHT

    if data.internal_links > 0 and data.external_links > 0:
        issues.append(AuditIssue(
            rule_id="links_ok", category=CategoryName.LINKS,
            severity=SeverityLevel.PASS,
            message=f"Page has {data.internal_links} internal and {data.external_links} external links.",
        ))

    score = round(max(0.0, min(100.0, score)), 1)
    logger.info("Links audit: %d internal, %d external → score %.1f",
                data.internal_links, data.external_links, score)
    return LinksAuditResult(
        link_data=data, score=score, issues=issues, recommendations=recs,
    )
