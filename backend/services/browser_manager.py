"""Reusable async Playwright browser manager.

Manages a single Chromium browser instance that persists for the lifetime of
the application.  Each audit request should obtain a *new browser context*
via ``new_context()`` so that cookies, cache, and other state are fully
isolated per request.
"""

from __future__ import annotations

import logging

from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages a long-lived headless Chromium browser instance."""

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Launch Playwright and a headless Chromium browser."""
        if self._browser is not None:
            return
        logger.info("Starting Playwright and launching Chromium…")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        logger.info("Chromium browser launched successfully.")

    async def stop(self) -> None:
        """Close the browser and stop Playwright."""
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
            logger.info("Chromium browser closed.")
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None
            logger.info("Playwright stopped.")

    # ------------------------------------------------------------------
    # Per-request helpers
    # ------------------------------------------------------------------

    async def new_context(self, **kwargs) -> BrowserContext:
        """Create a fresh, isolated browser context.

        Callers are responsible for closing the returned context when done.

        Raises:
            RuntimeError: If the browser has not been started yet.
        """
        if self._browser is None:
            raise RuntimeError(
                "BrowserManager has not been started. "
                "Call `await browser_manager.start()` first."
            )
        return await self._browser.new_context(**kwargs)

    @property
    def is_running(self) -> bool:
        """Return True when the browser instance is active."""
        return self._browser is not None


# Module-level singleton used across the application.
browser_manager = BrowserManager()
