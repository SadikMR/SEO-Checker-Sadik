"""Page rendering service using Playwright.

Navigates to a URL in a fresh browser context, waits for the page to finish
rendering (including JavaScript), and returns the final URL, response metadata,
and fully rendered HTML.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from services.browser_manager import browser_manager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT_MS: int = 30_000
"""Maximum time (ms) Playwright will wait for page navigation & rendering."""

DEFAULT_WAIT_UNTIL: str = "networkidle"
"""Navigation wait strategy — waits until there are no network connections
for at least 500 ms, ensuring JS-driven content has finished loading."""

USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class RedirectEntry:
    """A single hop in a redirect chain."""

    url: str
    status: int


@dataclass
class RenderResult:
    """Encapsulates the output of a page render."""

    input_url: str
    final_url: str
    status_code: int
    redirects: list[RedirectEntry] = field(default_factory=list)
    html: str = ""


# ---------------------------------------------------------------------------
# Rendering errors
# ---------------------------------------------------------------------------


class RenderError(Exception):
    """Base class for rendering failures."""


class NavigationTimeoutError(RenderError):
    """Raised when page navigation exceeds the timeout."""


class PageUnreachableError(RenderError):
    """Raised when the target page cannot be reached at all."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


async def render_page(
    url: str,
    *,
    timeout_ms: int = DEFAULT_TIMEOUT_MS,
    wait_until: str = DEFAULT_WAIT_UNTIL,
) -> RenderResult:
    """Render a page and return its final state.

    Args:
        url: The target URL to render.
        timeout_ms: Navigation timeout in milliseconds.
        wait_until: Playwright wait-until strategy
                    (``"load"`` | ``"domcontentloaded"`` | ``"networkidle"``).

    Returns:
        A :class:`RenderResult` containing the rendered HTML, final URL,
        status code, and redirect chain.

    Raises:
        NavigationTimeoutError: If the page does not load within *timeout_ms*.
        PageUnreachableError: If the page cannot be reached (DNS, connection
            refused, etc.).
        RenderError: For any other unexpected rendering failure.
    """
    context = await browser_manager.new_context(user_agent=USER_AGENT)

    try:
        page = await context.new_page()
        page.set_default_navigation_timeout(timeout_ms)

        # Track redirects via the response chain.
        redirects: list[RedirectEntry] = []

        def _on_response(response):
            """Collect redirect hops (3xx responses)."""
            if 300 <= response.status < 400:
                redirects.append(
                    RedirectEntry(url=response.url, status=response.status)
                )

        page.on("response", _on_response)

        try:
            response = await page.goto(url, wait_until=wait_until)
        except Exception as exc:
            exc_msg = str(exc).lower()
            if "timeout" in exc_msg:
                raise NavigationTimeoutError(
                    f"Page did not load within {timeout_ms}ms: {url}"
                ) from exc
            raise PageUnreachableError(
                f"Could not reach page: {url} — {exc}"
            ) from exc

        if response is None:
            raise PageUnreachableError(
                f"Navigation returned no response for: {url}"
            )

        final_url = page.url
        status_code = response.status
        html = await page.content()

        logger.info(
            "Rendered %s → %s (status %d, %d redirect(s), %d bytes HTML)",
            url,
            final_url,
            status_code,
            len(redirects),
            len(html),
        )

        return RenderResult(
            input_url=url,
            final_url=final_url,
            status_code=status_code,
            redirects=redirects,
            html=html,
        )

    except RenderError:
        raise
    except Exception as exc:
        raise RenderError(
            f"Unexpected error while rendering {url}: {exc}"
        ) from exc
    finally:
        await context.close()
