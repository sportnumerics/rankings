"""
Playwright-based HTML fetcher for stats.ncaa.org.

Uses Firefox to bypass Akamai bot detection that blocks Chromium.
Uses async API to avoid conflicts with pytest-asyncio in CI.
"""

import logging
import asyncio
from playwright.async_api import async_playwright, Browser, Page
from typing import Optional
import random
import time

logger = logging.getLogger(__name__)


class PlaywrightFetcher:
    """
    Fetches HTML using Playwright with Firefox.
    
    Firefox is used instead of Chromium because Akamai bot detection
    blocks Chromium but allows Firefox through.
    """

    BLOCK_INDICATORS = (
        'Access Denied',
        'access denied',
        'queue full',
        'under heavy load',
        'too many people are accessing this website',
    )
    CLOSED_TARGET_INDICATORS = (
        'target page, context or browser has been closed',
        'browser has been closed',
        'context has been closed',
        'page has been closed',
    )
    
    def __init__(self, headless: bool = True, max_attempts: int = 4):
        self.headless = headless
        self.max_attempts = max_attempts
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def __enter__(self):
        """Context manager entry - launch browser"""
        logger.info("Launching Firefox browser (headless=%s)", self.headless)
        
        # Get or create event loop
        try:
            asyncio.get_running_loop()
            raise RuntimeError("Cannot use PlaywrightFetcher in async context")
        except RuntimeError as e:
            if "no running event loop" not in str(e).lower() and "cannot" not in str(e).lower():
                raise
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def start():
            self.playwright = await async_playwright().start()
            await self._launch_browser()
            self.page = await self._new_page()
        
        loop.run_until_complete(start())
        self._loop = loop
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser"""
        async def stop():
            await self._close_page()
            await self._close_browser()
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        
        if hasattr(self, '_loop'):
            self._loop.run_until_complete(stop())
            self._loop.close()

    async def _launch_browser(self):
        if not self.playwright:
            raise RuntimeError("Playwright not initialized")
        self.browser = await self.playwright.firefox.launch(headless=self.headless)

    async def _close_page(self):
        if self.page:
            try:
                await self.page.close()
            except Exception:
                pass
            self.page = None

    async def _close_browser(self):
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
            self.browser = None

    async def _relaunch_browser(self):
        await self._close_page()
        await self._close_browser()
        await self._launch_browser()
        self.page = await self._new_page()

    async def _new_page(self) -> Page:
        if not self.browser:
            raise RuntimeError("Browser not initialized")
        page = await self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            viewport={'width': 1920, 'height': 1080}
        )
        await page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Upgrade-Insecure-Requests': '1',
        })
        return page

    def _is_blocked_or_busy_html(self, html: str) -> bool:
        lowered = html.lower()
        return any(indicator.lower() in lowered for indicator in self.BLOCK_INDICATORS)

    def _is_closed_target_error(self, error: Exception) -> bool:
        text = str(error).lower()
        return any(indicator in text for indicator in self.CLOSED_TARGET_INDICATORS)

    def fetch(self, url: str, wait_until: str = 'networkidle', timeout: int = 30000) -> str:
        """
        Fetch HTML from URL using Playwright.
        """
        if not self.page:
            raise RuntimeError("Fetcher not initialized. Use 'with' context manager.")
        
        logger.debug(f"Fetching: {url}")
        start = time.time()
        
        async def fetch_async():
            last_error = None

            for attempt in range(1, self.max_attempts + 1):
                current_page = self.page
                try:
                    if not current_page:
                        await self._relaunch_browser()
                        current_page = self.page

                    response = await current_page.goto(url, wait_until=wait_until, timeout=timeout)
                    status = response.status if response else None

                    if status != 200:
                        logger.warning(f"Non-200 status: {status} for {url} (attempt {attempt}/{self.max_attempts})")

                    html = await current_page.content()

                    if status == 200 and not self._is_blocked_or_busy_html(html):
                        return html, status

                    if self._is_blocked_or_busy_html(html):
                        reason = 'blocked or queue-full html'
                    else:
                        reason = f'unexpected status {status}'
                    raise Exception(f"Transient NCAA fetch failure for {url}: {reason}")
                except Exception as e:
                    last_error = e
                    logger.warning(
                        "Fetch attempt %s/%s failed for %s: %s",
                        attempt,
                        self.max_attempts,
                        url,
                        e,
                    )
                    if attempt == self.max_attempts:
                        break

                    if self._is_closed_target_error(e):
                        await self._relaunch_browser()
                    else:
                        await self._close_page()
                        self.page = await self._new_page()

                    await self.page.wait_for_timeout(int((1.5 * attempt + random.uniform(0, 0.75)) * 1000))

            raise last_error or Exception(f"Failed to fetch {url}")
        
        try:
            html, status = self._loop.run_until_complete(fetch_async())
            
            elapsed = time.time() - start
            logger.debug(f"Fetched {url} in {elapsed:.2f}s (status={status})")
            
            return html
        
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise
    
    def fetch_multiple(self, urls: list[str], delay: float = 1.0) -> list[str]:
        results = []
        
        for i, url in enumerate(urls):
            try:
                html = self.fetch(url)
                results.append(html)
                
                if i < len(urls) - 1 and delay > 0:
                    time.sleep(delay)
            
            except Exception as e:
                logger.warning(f"Skipping {url} due to error: {e}")
                results.append(None)
        
        return results
