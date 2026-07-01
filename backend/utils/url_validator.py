"""URL validation utilities.

Enforces the security requirements from the spec (§3, §4):
- URL must be well-formed and use http or https.
- Reject private/local IP ranges and loopback addresses to prevent SSRF.
- Reject localhost and reserved hostnames.
"""

from __future__ import annotations

import ipaddress
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blocked hostname patterns
# ---------------------------------------------------------------------------

_BLOCKED_HOSTNAMES: frozenset[str] = frozenset({
    "localhost",
    "localhost.localdomain",
})

_BLOCKED_TLDS: frozenset[str] = frozenset({
    ".local",
    ".internal",
    ".corp",
    ".lan",
    ".intranet",
})


class InvalidURLError(ValueError):
    """Raised when a URL fails validation."""


def validate_public_url(url: str) -> str:
    """Validate that *url* is a well-formed, publicly accessible URL.

    Args:
        url: The raw URL string to validate.

    Returns:
        The original URL string if valid.

    Raises:
        InvalidURLError: If the URL is malformed, uses a disallowed
            scheme, or resolves to a private/local address.
    """
    try:
        parsed = urlparse(url)
    except Exception as exc:
        raise InvalidURLError(f"Malformed URL: {url}") from exc

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(
            f"URL must use http or https. Got scheme: '{parsed.scheme or '(none)'}'"
        )

    hostname = (parsed.hostname or "").lower().strip()

    if not hostname:
        raise InvalidURLError("URL is missing a hostname.")

    # Blocked hostnames
    if hostname in _BLOCKED_HOSTNAMES:
        raise InvalidURLError(
            f"Access to '{hostname}' is not allowed."
        )

    # Blocked TLDs / suffixes
    for tld in _BLOCKED_TLDS:
        if hostname.endswith(tld):
            raise InvalidURLError(
                f"Access to '{hostname}' is not allowed (internal TLD)."
            )

    # IP address check — reject private/reserved ranges.
    # IMPORTANT: InvalidURLError subclasses ValueError, so we must re-raise
    # it explicitly to prevent the except branch from swallowing it.
    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        # Not an IP address — hostname-based, no further IP check needed.
        addr = None

    if addr is not None and (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_unspecified
    ):
        raise InvalidURLError(
            f"Access to private/reserved IP address '{hostname}' is not allowed."
        )

    logger.debug("URL validated as public: %s", url)
    return url
