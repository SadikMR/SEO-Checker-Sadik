"""Basic structured data detection audit rule module.

Rules:
    - structured_data_missing       — No structured data found (info)
    - structured_data_json_ld       — JSON-LD found (pass)
    - structured_data_microdata     — Microdata found (pass)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import StructuredDataInfo

logger = logging.getLogger(__name__)


@dataclass
class StructuredDataAuditResult:
    structured_data: StructuredDataInfo
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_structured_data(html: str) -> StructuredDataInfo:
    soup = BeautifulSoup(html, "html.parser")

    # JSON-LD
    json_ld_types: list[str] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            content = script.string or ""
            data = json.loads(content)
            if isinstance(data, dict):
                t = data.get("@type")
                if t:
                    json_ld_types.append(t if isinstance(t, str) else str(t))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        t = item.get("@type")
                        if t:
                            json_ld_types.append(t if isinstance(t, str) else str(t))
        except (json.JSONDecodeError, TypeError):
            continue

    # Microdata
    microdata_types: list[str] = []
    for el in soup.find_all(attrs={"itemscope": True}):
        itemtype = el.get("itemtype")
        if itemtype:
            microdata_types.append(str(itemtype).strip())

    return StructuredDataInfo(
        has_json_ld=len(json_ld_types) > 0,
        json_ld_types=json_ld_types,
        has_microdata=len(microdata_types) > 0,
        microdata_types=microdata_types,
    )


def audit_structured_data(html: str) -> StructuredDataAuditResult:
    data = _extract_structured_data(html)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    has_any = data.has_json_ld or data.has_microdata

    if not has_any:
        issues.append(AuditIssue(
            rule_id="structured_data_missing",
            category=CategoryName.STRUCTURED_DATA,
            severity=SeverityLevel.INFO,
            message="No structured data (JSON-LD or Microdata) detected on this page.",
        ))
        recs.append(AuditRecommendation(
            rule_id="structured_data_missing",
            category=CategoryName.STRUCTURED_DATA,
            severity=SeverityLevel.INFO,
            message="Add structured data (JSON-LD recommended) to help search engines understand your content and enable rich results.",
        ))
        return StructuredDataAuditResult(
            structured_data=data, score=50.0, issues=issues, recommendations=recs,
        )

    if data.has_json_ld:
        score += 60.0
        issues.append(AuditIssue(
            rule_id="structured_data_json_ld",
            category=CategoryName.STRUCTURED_DATA,
            severity=SeverityLevel.PASS,
            message=f"JSON-LD structured data found: {', '.join(data.json_ld_types)}.",
            value=", ".join(data.json_ld_types),
        ))

    if data.has_microdata:
        score += 40.0
        issues.append(AuditIssue(
            rule_id="structured_data_microdata",
            category=CategoryName.STRUCTURED_DATA,
            severity=SeverityLevel.PASS,
            message=f"Microdata found: {', '.join(data.microdata_types)}.",
            value=", ".join(data.microdata_types),
        ))

    score = round(max(0.0, min(100.0, score)), 1)
    logger.info("Structured data audit: json_ld=%s, microdata=%s → score %.1f",
                data.has_json_ld, data.has_microdata, score)
    return StructuredDataAuditResult(
        structured_data=data, score=score, issues=issues, recommendations=recs,
    )
