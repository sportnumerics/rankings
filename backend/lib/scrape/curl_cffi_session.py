"""
Optional curl_cffi wrapper for browser impersonation.
Wraps any session to add TLS fingerprinting resistance.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from curl_cffi import requests as cffi_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False


class CurlCffiSession:
    """
    Wrapper that uses curl_cffi for TLS fingerprinting resistance.
    Falls back to base session if curl_cffi is not available.
    """
    
    def __init__(self, base_session=None, impersonate="chrome120"):
        """
        Args:
            base_session: Fallback session if curl_cffi not available
            impersonate: Browser to impersonate (chrome120, safari, firefox, etc.)
        """
        self.base_session = base_session
        self.impersonate = impersonate
        
        if CURL_CFFI_AVAILABLE:
            self.cffi_session = cffi_requests.Session()
            logger.info(f"Using curl_cffi with {impersonate} impersonation")
        else:
            self.cffi_session = None
            if base_session:
                logger.warning("curl_cffi not available, falling back to base session")
            else:
                raise ImportError("curl_cffi not available and no fallback session provided")
    
    def get(self, url: str, headers=None, **kwargs):
        """
        Fetch URL with curl_cffi impersonation if available.
        """
        if self.cffi_session:
            # Use curl_cffi with browser impersonation
            # Note: impersonation sets complete headers, custom headers may be ignored
            return self.cffi_session.get(url, impersonate=self.impersonate, **kwargs)
        else:
            # Fall back to base session
            return self.base_session.get(url, headers=headers, **kwargs)
    
    def post(self, url: str, headers=None, **kwargs):
        """
        POST with curl_cffi impersonation if available.
        """
        if self.cffi_session:
            return self.cffi_session.post(url, impersonate=self.impersonate, headers=headers, **kwargs)
        else:
            return self.base_session.post(url, headers=headers, **kwargs)
