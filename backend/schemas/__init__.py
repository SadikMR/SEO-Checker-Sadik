# Backend Pydantic models — public API.

from schemas.audit import AuditRequest, AuditResponse, ErrorResponse, RedirectInfo
from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import (
    CategoryName,
    CategoryScore,
    ScoreSummary,
    SeverityLevel,
)
from schemas.seo_data import (
    HeadingData,
    ImageData,
    LinkData,
    MetaTagData,
    OpenGraphData,
    RawSEOData,
    RobotsData,
    TwitterCardData,
)

__all__ = [
    # Audit
    "AuditRequest",
    "AuditResponse",
    "ErrorResponse",
    "RedirectInfo",
    # Issues
    "AuditIssue",
    "AuditRecommendation",
    # Scores
    "CategoryName",
    "CategoryScore",
    "ScoreSummary",
    "SeverityLevel",
    # SEO Data
    "HeadingData",
    "ImageData",
    "LinkData",
    "MetaTagData",
    "OpenGraphData",
    "RawSEOData",
    "RobotsData",
    "TwitterCardData",
]
