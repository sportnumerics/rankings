"""
Akamai interstitial bypass using curl_cffi with Chrome impersonation.
"""
import re
import logging
from curl_cffi import requests

logger = logging.getLogger(__name__)


class AkamaiSession:
    """
    Session that can solve Akamai interstitial challenges.
    Uses curl_cffi to impersonate Chrome and bypass TLS fingerprinting.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.impersonate = "chrome120"
    
    def get(self, url: str, headers=None, **kwargs) -> requests.Response:
        """
        Fetch a URL, automatically solving Akamai challenges if encountered.
        Note: headers parameter is accepted but ignored since impersonation sets its own headers.
        """
        # Make initial request with Chrome impersonation
        # Note: We ignore custom headers since Chrome impersonation provides complete headers
        resp = self.session.get(url, impersonate=self.impersonate, **kwargs)
        
        # Check if we got an Akamai interstitial
        if resp.status_code == 200 and 'bm-verify' in resp.text:
            logger.info(f"Akamai interstitial detected for {url}, solving...")
            
            if self._solve_interstitial(resp.text):
                # Retry the original URL
                resp = self.session.get(url, impersonate=self.impersonate, **kwargs)
                
                if 'bm-verify' not in resp.text:
                    logger.info("Akamai challenge solved successfully")
                else:
                    logger.warning("Failed to solve Akamai challenge")
            else:
                logger.error("Could not parse Akamai challenge")
        
        return resp
    
    def _solve_interstitial(self, html: str) -> bool:
        """
        Solve the Akamai interstitial challenge by computing PoW and submitting.
        Returns True if verification was submitted successfully.
        """
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
        
        # Submit verification
        try:
            verify_resp = self.session.post(
                'https://stats.ncaa.org/_sec/verify?provider=interstitial',
                json={"bm-verify": bm_verify, "pow": j},
                impersonate=self.impersonate,
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
