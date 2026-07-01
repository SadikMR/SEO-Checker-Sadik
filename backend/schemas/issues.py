"""Issue and recommendation models for the audit engine.

Each audit rule can produce an issue (something wrong or sub-optimal)
and an accompanying recommendation (actionable fix guidance).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.scores import CategoryName, SeverityLevel


class AuditIssue(BaseModel):
    """A single issue discovered during an SEO audit."""

    rule_id: str = Field(
        ...,
        description="Unique machine-readable identifier for the rule "
        "(e.g. 'meta_title_missing').",
    )
    category: CategoryName = Field(
        ..., description="The audit category this issue belongs to."
    )
    severity: SeverityLevel = Field(
        ..., description="How severe the issue is."
    )
    message: str = Field(
        ..., description="Human-readable description of the issue."
    )
    value: str | None = Field(
        None,
        description="The actual value found (e.g. the current title text), "
        "or None if the element is missing entirely.",
    )

    model_config = {"json_schema_extra": {"examples": [
        {
            "rule_id": "meta_title_missing",
            "category": "meta",
            "severity": "critical",
            "message": "Page is missing a <title> tag.",
            "value": None,
        }
    ]}}


class AuditRecommendation(BaseModel):
    """An actionable recommendation linked to one or more issues."""

    rule_id: str = Field(
        ...,
        description="The rule_id of the issue this recommendation addresses.",
    )
    category: CategoryName = Field(
        ..., description="The audit category this recommendation belongs to."
    )
    severity: SeverityLevel = Field(
        ..., description="Severity inherited from the related issue."
    )
    message: str = Field(
        ..., description="Actionable guidance on how to fix the issue."
    )

    model_config = {"json_schema_extra": {"examples": [
        {
            "rule_id": "meta_title_missing",
            "category": "meta",
            "severity": "critical",
            "message": "Add a descriptive <title> tag between 30 and 60 characters.",
        }
    ]}}
