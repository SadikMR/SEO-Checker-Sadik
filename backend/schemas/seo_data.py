"""Raw SEO data extraction models.

These models represent the structured data extracted from a rendered page
before any scoring or rule evaluation is applied.  They map directly to
the SEO factors listed in the specification (§3).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Sub-models for extracted SEO signals
# ------------------------------------------------------------------


class MetaTagData(BaseModel):
    """Core meta tag information."""

    title: str | None = Field(None, description="Content of the <title> tag.")
    title_length: int | None = Field(
        None, description="Character length of the title."
    )
    description: str | None = Field(
        None, description="Content of the meta description tag."
    )
    description_length: int | None = Field(
        None, description="Character length of the meta description."
    )
    canonical: str | None = Field(
        None, description="Canonical URL specified in <link rel='canonical'>."
    )


class HeadingData(BaseModel):
    """Heading hierarchy information."""

    h1: list[str] = Field(default_factory=list, description="All H1 texts.")
    h2: list[str] = Field(default_factory=list, description="All H2 texts.")
    h3: list[str] = Field(default_factory=list, description="All H3 texts.")
    h4: list[str] = Field(default_factory=list, description="All H4 texts.")
    h5: list[str] = Field(default_factory=list, description="All H5 texts.")
    h6: list[str] = Field(default_factory=list, description="All H6 texts.")
    h1_count: int = Field(0, description="Number of H1 tags found.")


class OpenGraphData(BaseModel):
    """Open Graph meta tag data."""

    og_title: str | None = Field(None, description="og:title value.")
    og_description: str | None = Field(
        None, description="og:description value."
    )
    og_image: str | None = Field(None, description="og:image URL.")
    og_url: str | None = Field(None, description="og:url value.")
    og_type: str | None = Field(None, description="og:type value.")
    og_site_name: str | None = Field(None, description="og:site_name value.")


class TwitterCardData(BaseModel):
    """Twitter Card meta tag data."""

    card: str | None = Field(None, description="twitter:card value.")
    title: str | None = Field(None, description="twitter:title value.")
    description: str | None = Field(
        None, description="twitter:description value."
    )
    image: str | None = Field(None, description="twitter:image URL.")
    site: str | None = Field(None, description="twitter:site handle.")


class ImageData(BaseModel):
    """Summary of image analysis."""

    total_images: int = Field(0, description="Total number of <img> tags.")
    images_with_alt: int = Field(
        0, description="Number of images with non-empty alt attributes."
    )
    images_without_alt: int = Field(
        0, description="Number of images missing alt attributes."
    )
    alt_texts: list[str] = Field(
        default_factory=list,
        description="List of alt attribute values found.",
    )


class LinkData(BaseModel):
    """Summary of link analysis."""

    total_links: int = Field(0, description="Total number of <a> tags.")
    internal_links: int = Field(0, description="Number of internal links.")
    external_links: int = Field(0, description="Number of external links.")
    nofollow_links: int = Field(
        0, description="Number of links with rel='nofollow'."
    )


class RobotsData(BaseModel):
    """Robots directives extracted from the page."""

    meta_robots: str | None = Field(
        None,
        description="Content of the <meta name='robots'> tag.",
    )
    x_robots_tag: str | None = Field(
        None,
        description="Value of the X-Robots-Tag HTTP header, if present.",
    )


class StructuredDataInfo(BaseModel):
    """Basic structured data detection results."""

    has_json_ld: bool = Field(
        False, description="Whether JSON-LD script tags were found."
    )
    json_ld_types: list[str] = Field(
        default_factory=list,
        description="List of @type values found in JSON-LD blocks.",
    )
    has_microdata: bool = Field(
        False, description="Whether microdata (itemscope) attributes were found."
    )
    microdata_types: list[str] = Field(
        default_factory=list,
        description="List of itemtype values found in microdata.",
    )


# ------------------------------------------------------------------
# Aggregate raw data model
# ------------------------------------------------------------------


class RawSEOData(BaseModel):
    """Complete raw SEO data extracted from a rendered page.

    This model is included verbatim in the audit response so the
    frontend can display the underlying data alongside scores.
    """

    meta: MetaTagData = Field(
        default_factory=MetaTagData, description="Core meta tag data."
    )
    headings: HeadingData = Field(
        default_factory=HeadingData, description="Heading hierarchy data."
    )
    open_graph: OpenGraphData = Field(
        default_factory=OpenGraphData, description="Open Graph tag data."
    )
    twitter_card: TwitterCardData = Field(
        default_factory=TwitterCardData, description="Twitter Card tag data."
    )
    images: ImageData = Field(
        default_factory=ImageData, description="Image analysis data."
    )
    links: LinkData = Field(
        default_factory=LinkData, description="Link analysis data."
    )
    robots: RobotsData = Field(
        default_factory=RobotsData, description="Robots directive data."
    )
    structured_data: StructuredDataInfo = Field(
        default_factory=StructuredDataInfo,
        description="Basic structured data detection.",
    )
