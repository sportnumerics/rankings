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
            # Check if there's a running loop
            asyncio.get_running_loop()
            # If we get here, we're in an async context - create a new loop in a thread
            raise RuntimeError("Cannot use PlaywrightFetcher in async context")
        except RuntimeError as e:
            if "no running event loop" not in str(e).lower() and "cannot" not in str(e).lower():
                # There is a running loop, can't proceed
                raise
            # No running loop - safe to create one
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def start():
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.firefox.launch(headless=self.headless)
            self.page = await self._new_page()
        
        loop.run_until_complete(start())
        self._loop = loop
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser"""
        async def stop():
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        
        if hasattr(self, '_loop'):
            self._loop.run_until_complete(stop())
            self._loop.close()

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

    def fetch(self, url: str, wait_until: str = 'networkidle', timeout: int = 30000) -> str:
        """
        Fetch HTML from URL using Playwright.
        
        Args:
            url: URL to fetch
            wait_until: Load state to wait for ('load', 'domcontentloaded', 'networkidle')
            timeout: Timeout in milliseconds
        
        Returns:
            Rendered HTML content
        
        Raises:
            Exception if page fails to load or returns Access Denied
        """
        if not self.page:
            raise RuntimeError("Fetcher not initialized. Use 'with' context manager.")
        
        logger.debug(f"Fetching: {url}")
        start = time.time()
        
        async def fetch_async():
            last_error = None
            current_page = self.page

            for attempt in range(1, self.max_attempts + 1):
                try:
                    response = await current_page.goto(url, wait_until=wait_until, timeout=timeout)
                    status = response.status if response else None

                    if status != 200:
                        logger.warning(f"Non-200 status: {status} for {url} (attempt {attempt}/{self.max_attempts})")

                    html = await current_page.content()

                    if status == 200 and not self._is_blocked_or_busy_html(html):
                        if current_page is not self.page:
                            if self.page:
                                await self.page.close()
                            self.page = current_page
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

                    if current_page:
                        await current_page.close()
                    current_page = await self._new_page()
                    await current_page.wait_for_timeout(int((1.5 * attempt + random.uniform(0, 0.75)) * 1000))

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
        """
        Fetch multiple URLs sequentially with delay between requests.
        
        Args:
            urls: List of URLs to fetch
            delay: Seconds to wait between requests (default 1.0)
        
        Returns:
            List of HTML content (same order as input URLs)
        """
        results = []
        
        for i, url in enumerate(urls):
            try:
                html = self.fetch(url)
                results.append(html)
                
                # Add delay between requests (except after last one)
                if i < len(urls) - 1 and delay > 0:
                    time.sleep(delay)
            
            except Exception as e:
                logger.warning(f"Skipping {url} due to error: {e}")
                results.append(None)
        
        return results
