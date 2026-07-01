"""Images & alt attribute audit rule module.

Rules:
    - images_no_alt            — Images found without alt attributes (warning)
    - images_all_have_alt      — All images have alt attributes (pass)
    - images_none_found        — No images on the page (info)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

from schemas.issues import AuditIssue, AuditRecommendation
from schemas.scores import CategoryName, SeverityLevel
from schemas.seo_data import ImageData

logger = logging.getLogger(__name__)


@dataclass
class ImagesAuditResult:
    image_data: ImageData
    score: float
    issues: list[AuditIssue]
    recommendations: list[AuditRecommendation]


def _extract_images(html: str) -> ImageData:
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.find_all("img")
    total = len(imgs)
    with_alt = 0
    without_alt = 0
    alt_texts: list[str] = []

    for img in imgs:
        alt = img.get("alt")
        if alt is not None and alt.strip():
            with_alt += 1
            alt_texts.append(alt.strip())
        else:
            without_alt += 1

    return ImageData(
        total_images=total,
        images_with_alt=with_alt,
        images_without_alt=without_alt,
        alt_texts=alt_texts,
    )


def audit_images(html: str) -> ImagesAuditResult:
    data = _extract_images(html)
    issues: list[AuditIssue] = []
    recs: list[AuditRecommendation] = []
    score = 0.0

    if data.total_images == 0:
        issues.append(AuditIssue(
            rule_id="images_none_found", category=CategoryName.IMAGES,
            severity=SeverityLevel.INFO,
            message="No images found on this page.",
        ))
        score = 100.0  # No images = no issues with alt text
        return ImagesAuditResult(
            image_data=data, score=score, issues=issues, recommendations=recs,
        )

    if data.images_without_alt > 0:
        ratio = data.images_with_alt / data.total_images
        issues.append(AuditIssue(
            rule_id="images_no_alt", category=CategoryName.IMAGES,
            severity=SeverityLevel.WARNING,
            message=(
                f"{data.images_without_alt} of {data.total_images} images "
                f"are missing alt attributes."
            ),
            value=f"{data.images_without_alt}/{data.total_images}",
        ))
        recs.append(AuditRecommendation(
            rule_id="images_no_alt", category=CategoryName.IMAGES,
            severity=SeverityLevel.WARNING,
            message="Add descriptive alt attributes to all images for accessibility and SEO.",
        ))
        score = round(ratio * 100.0, 1)
    else:
        issues.append(AuditIssue(
            rule_id="images_all_have_alt", category=CategoryName.IMAGES,
            severity=SeverityLevel.PASS,
            message=f"All {data.total_images} images have alt attributes.",
        ))
        score = 100.0

    logger.info("Images audit: %d total, %d without alt → score %.1f",
                data.total_images, data.images_without_alt, score)
    return ImagesAuditResult(
        image_data=data, score=score, issues=issues, recommendations=recs,
    )
