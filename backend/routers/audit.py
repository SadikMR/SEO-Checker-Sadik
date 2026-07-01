"""Audit API router.

Provides the ``POST /audit`` endpoint that accepts a URL, renders the
page, runs the audit pipeline, and returns the structured result.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from engine.pipeline import run_audit
from schemas.audit import AuditRequest, AuditResponse, ErrorResponse
from services.renderer import (
    NavigationTimeoutError,
    PageUnreachableError,
    RenderError,
    render_page,
)
from utils.url_validator import InvalidURLError, validate_public_url

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Audit"])


@router.post(
    "/audit",
    response_model=AuditResponse,
    summary="Run an SEO audit on a URL",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or unreachable URL."},
        504: {"model": ErrorResponse, "description": "Page load timed out."},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
)
async def audit_url(body: AuditRequest) -> AuditResponse:
    """Accept a URL, render the page, and return an SEO audit report."""
    url = str(body.url)
    logger.info("Audit requested for: %s", url)

    # 1. Validate the URL is publicly accessible (SSRF protection)
    try:
        validate_public_url(url)
    except InvalidURLError as exc:
        logger.warning("URL validation rejected: %s — %s", url, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # 2. Render the page
    try:
        render_result = await render_page(url)
    except NavigationTimeoutError as exc:
        logger.warning("Timeout rendering %s: %s", url, exc)
        raise HTTPException(
            status_code=504,
            detail=str(exc),
        ) from exc
    except PageUnreachableError as exc:
        logger.warning("Unreachable %s: %s", url, exc)
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RenderError as exc:
        logger.error("Render error for %s: %s", url, exc)
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    # 2. Run the audit pipeline
    result = run_audit(render_result)

    logger.info(
        "Audit complete for %s — score: %.1f",
        url,
        result.scores.overall_score,
    )
    return result
