# Session Architecture

## Design Principles

The scraper uses a **composable session architecture** to separate concerns:

1. **Base session**: Rate limiting + caching (`LimitedCachedSession` or `CachedSession`)
2. **Interstitial bypass**: Detects and solves Akamai challenges (`InterstitialBypassSession`)
3. **Browser impersonation**: Optional TLS fingerprinting resistance (`CurlCffiSession`)

Each layer wraps the previous one, delegating calls down the chain.

## Composition Order

```python
# 1. Start with rate-limited + cached base
session = LimitedCachedSession(
    cache_name='cache',
    expire_after=timedelta(days=1),
    per_second=2  # Rate limiting
)

# 2. Add interstitial bypass if needed (NCAA)
session = InterstitialBypassSession(session)

# 3. Optionally add browser impersonation (for testing)
session = CurlCffiSession(base_session=session)
```

## Why Separate?

### Interstitial Bypass
- Works with **any** HTTP session (requests, cached, rate-limited)
- No dependency on curl_cffi
- Can be tested independently
- Preserves rate limiting and caching

### curl_cffi Wrapper
- **Optional** - only needed if regular requests get blocked
- Can be enabled/disabled for A/B testing
- Falls back to base session if not available
- Adds ~100KB dependency

### Rate Limiting + Caching
- Core functionality for all scrapers
- Works whether or not interstitial bypass is enabled
- Reduces load on source sites

## Testing Strategy

1. **Default**: Interstitial bypass only (no curl_cffi)
   - Lighter dependency footprint
   - Preserves rate limiting and caching
   - Works if sites don't check TLS fingerprints

2. **If blocked**: Enable curl_cffi
   - Uncomment the CurlCffiSession wrapper in scrape.py
   - Adds browser TLS fingerprinting
   - Still preserves other layers

## Files

- `interstitial_bypass.py`: Core interstitial detection + solving
- `curl_cffi_session.py`: Optional browser impersonation wrapper
- `scrape.py`: Composes sessions together in `ScrapeRunner.__init__`
- `akamai_bypass.py`: **DEPRECATED** - old monolithic approach

## Migration from Old Code

Old (monolithic):
```python
if source == 'ncaa' and AKAMAI_AVAILABLE:
    self.cache = AkamaiSession()  # No rate limiting or caching!
```

New (composable):
```python
session = LimitedCachedSession(...)  # Rate limiting + caching
if source == 'ncaa':
    session = InterstitialBypassSession(session)  # Add bypass
# Optional: session = CurlCffiSession(session)
self.cache = session
```

## Benefits

✅ Each concern is isolated and testable  
✅ Can enable/disable curl_cffi without losing other features  
✅ Rate limiting and caching always work  
✅ Easier to debug (clear layer boundaries)  
✅ Can compose in different orders for different needs
