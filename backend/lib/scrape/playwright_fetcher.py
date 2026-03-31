"""
Playwright-based HTML fetcher for stats.ncaa.org.

Uses Firefox to bypass Akamai bot detection that blocks Chromium.
"""

import logging
from playwright.sync_api import sync_playwright, Browser, Page
from typing import Optional
import time

logger = logging.getLogger(__name__)


class PlaywrightFetcher:
    """
    Fetches HTML using Playwright with Firefox.
    
    Firefox is used instead of Chromium because Akamai bot detection
    blocks Chromium but allows Firefox through.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def __enter__(self):
        """Context manager entry - launch browser"""
        self.playwright = sync_playwright().start()
        
        logger.info("Launching Firefox browser (headless=%s)", self.headless)
        self.browser = self.playwright.firefox.launch(headless=self.headless)
        
        # Create page with realistic settings
        self.page = self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            viewport={'width': 1920, 'height': 1080}
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
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
        
        try:
            response = self.page.goto(url, wait_until=wait_until, timeout=timeout)
            
            if response.status != 200:
                logger.warning(f"Non-200 status: {response.status} for {url}")
            
            # Get rendered HTML
            html = self.page.content()
            
            # Check for Akamai blocking
            if 'Access Denied' in html or 'access denied' in html.lower():
                raise Exception(f"Akamai blocked request to {url} (Access Denied in HTML)")
            
            elapsed = time.time() - start
            logger.debug(f"Fetched {url} in {elapsed:.2f}s (status={response.status})")
            
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
