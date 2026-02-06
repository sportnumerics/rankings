"""
Tests for Akamai interstitial bypass wrapper.
"""
import unittest
from unittest.mock import Mock, MagicMock
from .interstitial_bypass import InterstitialBypassSession


class TestInterstitialBypass(unittest.TestCase):
    
    def test_passthrough_normal_response(self):
        """Non-interstitial responses should pass through unchanged."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Normal content</html>"
        mock_session.get.return_value = mock_response
        
        session = InterstitialBypassSession(mock_session)
        result = session.get("https://example.com")
        
        self.assertEqual(result, mock_response)
        mock_session.get.assert_called_once_with("https://example.com")
    
    def test_detect_interstitial(self):
        """Should detect Akamai interstitial challenges."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
            <script>
            var config = {"bm-verify": "abc123"};
            var i = 10; var j = i + Number("20" + "30");
            </script>
            </html>
        '''
        
        # First call returns interstitial, second returns normal content
        mock_normal = Mock()
        mock_normal.status_code = 200
        mock_normal.text = "<html>Real content</html>"
        mock_session.get.side_effect = [mock_response, mock_normal]
        
        # Mock post for verification
        mock_verify = Mock()
        mock_verify.status_code = 200
        mock_verify.text = '{"success": true}'
        mock_session.post.return_value = mock_verify
        
        session = InterstitialBypassSession(mock_session)
        result = session.get("https://example.com")
        
        # Should have called get twice (initial + retry)
        self.assertEqual(mock_session.get.call_count, 2)
        
        # Should have posted verification
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        self.assertIn('bm-verify', call_args.kwargs['json'])
        self.assertEqual(call_args.kwargs['json']['pow'], 10 + 2030)
    
    def test_solve_pow_calculation(self):
        """Should correctly solve the proof-of-work challenge."""
        session = InterstitialBypassSession(Mock())
        
        mock_resp = Mock()
        mock_resp.text = 'var i = 5; var j = i + Number("10" + "20");'
        
        # Extract the calculation manually to verify
        import re
        pow_match = re.search(r'var i = (\d+); var j = i \+ Number\("(\d+)" \+ "(\d+)"\)', mock_resp.text)
        self.assertIsNotNone(pow_match)
        
        i = int(pow_match.group(1))
        num1 = pow_match.group(2)
        num2 = pow_match.group(3)
        j = i + int(num1 + num2)
        
        self.assertEqual(j, 5 + 1020)
    
    def test_post_delegation(self):
        """POST requests should delegate to base session."""
        mock_session = Mock()
        mock_response = Mock()
        mock_session.post.return_value = mock_response
        
        session = InterstitialBypassSession(mock_session)
        result = session.post("https://example.com/api", json={"test": "data"})
        
        self.assertEqual(result, mock_response)
        mock_session.post.assert_called_once_with("https://example.com/api", json={"test": "data"})
    
    def test_403_invalidates_cache(self):
        """Should invalidate cache and retry on 403."""
        mock_session = Mock()
        mock_cache = Mock()
        mock_session.cache = mock_cache
        
        # First call returns 403, second returns 200
        mock_403 = Mock()
        mock_403.status_code = 403
        mock_200 = Mock()
        mock_200.status_code = 200
        mock_200.text = "<html>Normal content</html>"
        mock_session.get.side_effect = [mock_403, mock_200]
        
        session = InterstitialBypassSession(mock_session)
        result = session.get("https://example.com")
        
        # Should have invalidated cache
        mock_cache.delete.assert_called_once_with(urls=["https://example.com"])
        
        # Should have called get twice (initial + retry)
        self.assertEqual(mock_session.get.call_count, 2)
        self.assertEqual(result, mock_200)


if __name__ == '__main__':
    unittest.main()
