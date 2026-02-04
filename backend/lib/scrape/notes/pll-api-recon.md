# PLL Stats API Reconnaissance

**Date**: 2026-02-04  
**Purpose**: Document PLL stats endpoints for potential scraping  
**Site**: https://stats.premierlacrosseleague.com/

## Summary

The PLL stats site is a React SPA that uses a GraphQL API backend. The API appears to require authentication and has Cloudflare bot protection, making direct scraping challenging.

## API Endpoints Discovered

### GraphQL Endpoint
- **URL**: `https://api.stats.premierlacrosseleague.com/graphql`
- **Method**: POST
- **Auth**: Required (returns 403 Forbidden / Cloudflare error 1010 without auth)
- **Protection**: Cloudflare bot detection active

### REST API Base
- **URL**: `https://api.stats.premierlacrosseleague.com/api`
- **Status**: Not fully explored yet (GraphQL appears to be primary interface)

## GraphQL Queries Identified

From analyzing the site's JavaScript bundle (`/static/js/main.92a8b685.js`):

### `allPlayers` Query
```graphql
query allPlayers(
  $season: Int!,
  $includeZPP: Boolean!,
  $includeReg: Boolean!,
  $includePost: Boolean!,
  $limit: Int,
  $league: String
) {
  allPlayers(
    season: $season,
    includeZPP: $includeZPP,
    limit: $limit,
    league: $league
  ) {
    officialId
    collegeYear
    country
    countryCode
    firstName
    lastName
    lastNameSuffix
    # ... more fields
  }
}
```

### `allTeams` Query
- Referenced in bundle, exact schema TBD

### Other Likely Queries
- `teamById`
- `playerById`
- `allGames`

## robots.txt Analysis

**URL**: https://stats.premierlacrosseleague.com/robots.txt

```
Content-Signal: search=yes,ai-train=no
User-agent: *
Allow: /

# Specific bot restrictions:
User-agent: ClaudeBot
Disallow: /
```

**Key Points**:
- Search indexing allowed
- AI training disallowed
- ClaudeBot explicitly blocked
- No rate limit information

## Authentication

- **Status**: Required for GraphQL endpoint
- **Type**: Unknown (likely Bearer token)
- **Extraction**: Token not found in client-side bundle (may be dynamically generated or session-based)
- **Protection**: Cloudflare WAF/bot detection active

## Test Results

### GraphQL Introspection (No Auth)
```bash
curl -X POST https://api.stats.premierlacrosseleague.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```
**Result**: `403 Forbidden` (Cloudflare error 1010)

### REST /api/v4/teams Endpoint
```bash
curl https://api.stats.premierlacrosseleague.com/api/v4/teams
```
**Result**: `404 Not Found`

### REST /api/v4/events Endpoint
```bash
curl https://api.stats.premierlacrosseleague.com/api/v4/events?year=2024
```
**Result**: `400 Bad Request` - "Missing authorization in header"

## Challenges for Scraping

1. **Authentication Required**: All API endpoints require auth headers
2. **Bot Protection**: Cloudflare actively blocks automated requests (error 1010)
3. **Token Extraction**: Auth token not visible in client bundle (likely server-generated or session-based)
4. **robots.txt**: ClaudeBot explicitly disallowed
5. **Rate Limits**: Unknown (not documented in robots.txt or API responses)

## Alternative Approaches

1. **Browser automation**: Use headless browser to capture authenticated requests (Playwright/Puppeteer)
2. **HTML scraping**: Check if public-facing pages (team/player profiles) have embedded JSON-LD or structured data
3. **Official API**: Contact PLL to request official API access or partnership
4. **Manual data collection**: Small-scale manual exports for MVP validation

## Next Steps

- [ ] Test browser automation to capture auth token from legitimate session
- [ ] Analyze HTML pages for structured data (JSON-LD, meta tags)
- [ ] Check for public CSV/Excel exports on stats pages
- [ ] Review PLL's terms of service regarding data usage
- [ ] Consider reaching out to PLL for official data access

## Conclusion

**Feasibility**: Low-to-Medium for automated scraping  
**Recommendation**: Investigate browser automation or pursue official API partnership

The PLL stats API uses modern bot protection and requires authentication, making direct HTTP scraping infeasible. Browser automation may work but requires maintenance and may violate terms of service. Official API access would be the most sustainable approach.
