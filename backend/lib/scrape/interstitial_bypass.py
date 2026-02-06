"""
Akamai interstitial bypass wrapper for any HTTP session.
Detects and solves interstitial challenges, delegates to underlying session.
"""
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


class InterstitialBypassSession:
    """
    Wrapper that automatically solves Akamai interstitial challenges.
    Can wrap any session object with a get() method.
    """
    
    def __init__(self, base_session):
        """
        Args:
            base_session: Any session with a get() method (requests.Session, 
                         CachedSession, LimitedCachedSession, etc.)
        """
        self.session = base_session
    
    def get(self, url: str, **kwargs) -> Any:
        """
        Fetch a URL, automatically solving Akamai challenges if encountered.
        Invalidates cache on 403 to ensure fresh interstitial challenges.
        """
        # Make initial request through the base session
        resp = self.session.get(url, **kwargs)
        
        # If we got a 403, invalidate cache and retry (might be cached block)
        if resp.status_code == 403:
            logger.info(f"Got 403 for {url}, invalidating cache and retrying...")
            self._invalidate_cache(url)
            resp = self.session.get(url, **kwargs)
        
        # Check if we got an Akamai interstitial
        if self._is_interstitial(resp):
            logger.info(f"Akamai interstitial detected for {url}, solving...")
            
            if self._solve_interstitial(resp):
                # Invalidate cache before retry to force fresh request
                self._invalidate_cache(url)
                
                # Retry the original URL
                resp = self.session.get(url, **kwargs)
                
                if not self._is_interstitial(resp):
                    logger.info("Akamai challenge solved successfully")
                else:
                    logger.warning("Failed to solve Akamai challenge")
            else:
                logger.error("Could not parse Akamai challenge")
        
        return resp
    
    def _invalidate_cache(self, url: str):
        """Invalidate cached response for a URL if session has a cache."""
        if hasattr(self.session, 'cache') and hasattr(self.session.cache, 'delete'):
            try:
                self.session.cache.delete(urls=[url])
                logger.debug(f"Invalidated cache for {url}")
            except Exception as e:
                logger.debug(f"Could not invalidate cache: {e}")
    
    def _is_interstitial(self, resp) -> bool:
        """Check if response is an Akamai interstitial challenge."""
        try:
            return resp.status_code == 200 and 'bm-verify' in resp.text
        except:
            return False
    
    def _solve_interstitial(self, resp) -> bool:
        """
        Solve the Akamai interstitial challenge by computing PoW and submitting.
        Returns True if verification was submitted successfully.
        """
        html = resp.text
        
        # Extract bm-verify token from the inline JSON
        verify_match = re.search(r'"bm-verify": "([^"]+)"', html)
        if not verify_match:
            logger.error("Could not find bm-verify token in interstitial")
            return False
        
        bm_verify = verify_match.group(1)
        
        # Extract and solve proof-of-work
        pow_match = re.search(r'var i = (\d+); var j = i \+ Number\("(\d+)" \+ "(\d+)"\)', html)
        if not pow_match:
            logger.error("Could not find PoW calculation in interstitial")
            return False
        
        i = int(pow_match.group(1))
        num1 = pow_match.group(2)
        num2 = pow_match.group(3)
        j = i + int(num1 + num2)
        
        # Submit verification using the same session
        try:
            verify_resp = self.session.post(
                'https://stats.ncaa.org/_sec/verify?provider=interstitial',
                json={"bm-verify": bm_verify, "pow": j},
                headers={'Content-Type': 'application/json'}
            )
            
            if verify_resp.status_code == 200:
                logger.debug(f"Verification response: {verify_resp.text}")
                return True
            else:
                logger.error(f"Verification failed with status {verify_resp.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error submitting verification: {e}")
            return False
    
    def post(self, url: str, **kwargs) -> Any:
        """Delegate POST to base session."""
        return self.session.post(url, **kwargs)
