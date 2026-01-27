# Sportnumerics Rankings

**Lacrosse team and player rankings powered by data.**

Sportnumerics provides predictive rankings and detailed statistics for college lacrosse teams and players. Currently supporting NCAA and MCLA divisions.

🌐 **Live site**: [sportnumerics.com](https://sportnumerics.com)

---

## What It Does

1. **Scrapes** game schedules, rosters, and stats from NCAA and MCLA
2. **Analyzes** performance data using predictive algorithms
3. **Ranks** teams based on strength of schedule and game outcomes
4. **Presents** rankings, stats, and predictions via a fast Next.js frontend

---

## Architecture

```
sportnumerics-rankings/
├── backend/          # Python: web scraping, data processing, ranking algorithms
│   ├── lib/
│   │   ├── scrape/   # NCAA & MCLA scrapers
│   │   ├── all/      # Ranking algorithm
│   │   └── shared/   # Common types and utilities
│   └── README.md     # Backend setup and usage
│
├── frontend/         # Next.js: UI for displaying rankings and stats
│   ├── app/
│   │   ├── [year]/   # Dynamic routes for years, divisions, teams, players
│   │   └── server/   # Server-side data fetching from S3
│   └── README.md     # Frontend setup
│
└── infrastructure/   # AWS infrastructure (not yet public)
    ├── backend/      # ECS task definitions, EventBridge schedules
    └── frontend/     # S3 + CloudFront CDN
```

**Data Flow:**
1. Backend runs nightly via ECS (scrapes → processes → ranks)
2. Outputs Parquet files to S3
3. Frontend fetches from S3 on-demand (server-side rendering)
4. CloudFront CDN caches pages globally

---

## Getting Started

### Prerequisites

- **Backend**: Python 3.11+, [uv](https://github.com/astral-sh/uv)
- **Frontend**: Node.js 20+, npm

### Backend Setup

See [backend/README.md](backend/README.md) for full details.

**Quick start:**
```bash
cd backend
uv sync  # Install dependencies
uv run scrape --help  # View scraping options
```

### Frontend Setup

See [frontend/README.md](frontend/README.md) for full details.

**Quick start:**
```bash
cd frontend
npm install
npm run dev  # Start dev server at http://localhost:3000
```

---

## Key Features

### Currently Supported
- **NCAA Division I, II, III** (men's lacrosse)
- **MCLA Division I, II, III** (men's club lacrosse)
- Team rankings and predictions
- Player stats: Goals, Assists, Ground Balls
- Game-by-game breakdowns
- Historical data (multiple seasons)

### Data Captured (Backend)
The scrapers collect more data than currently displayed:
- Face-off wins/losses (FO-W, FO-L)
- Goalie saves (SV) and goals against (GA)
- Player positions, rosters, coaches

See [PRODUCT-IDEAS.md](PRODUCT-IDEAS.md) for expansion plans.

---

## Development

### Running Tests

**Backend:**
```bash
cd backend
uv run python -m unittest discover
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run build  # Type-check and build
```

### Project Goals

- **Maintainability**: Clean separation between scraping, processing, and presentation
- **Flexibility**: Easy to experiment with ranking algorithms
- **Performance**: Fast static rendering + CDN for global speed
- **Extensibility**: Add new data sources (PLL, high school, international)

---

## How It Works

### 1. Scraping (`backend/lib/scrape/`)
- Fetch team lists, schedules, rosters from NCAA/MCLA websites
- Parse HTML into structured data models
- Cache responses to avoid hammering source sites
- Output: JSON + Parquet files

### 2. Ranking (`backend/lib/all/`)
- Predict game outcomes using Elo-like algorithm
- Adjust for strength of schedule
- Rank teams by predicted performance
- Output: Ranked team lists with confidence scores

### 3. Presentation (`frontend/`)
- Next.js fetches data from S3 at request time
- Server-side rendering for fast initial loads
- Client-side navigation for smooth UX
- Responsive design (mobile-friendly)

---

## Contributing

We welcome contributions! Focus areas:
- **Bug fixes**: Scrapers break when sites change structure
- **New data sources**: PLL, high school leagues, international
- **UI improvements**: Better mobile experience, accessibility
- **Analytics**: Advanced stats, prediction accuracy tracking

Before starting work on a feature, please check [PRODUCT-IDEAS.md](PRODUCT-IDEAS.md) or open an issue to discuss.

### Code Style
- **Backend**: Follow PEP 8, use type hints
- **Frontend**: TypeScript strict mode, ESLint config

---

## Deployment

Deployment is automated via GitHub Actions:
- **Backend**: Build Docker image → Push to ECR → Deploy to ECS
- **Frontend**: Build Next.js → Upload to S3 → Invalidate CloudFront cache

See `.github/workflows/` for CI/CD configuration.

---

## FAQ

**Q: Why not use an official API?**  
A: NCAA and MCLA don't provide public APIs. We scrape responsibly with rate limiting and caching.

**Q: Can I use this data for my own project?**  
A: The code is private, but feel free to reach out if you have a specific use case.

**Q: How often is data updated?**  
A: Backend runs nightly during the season. Off-season updates are less frequent.

**Q: Why lacrosse?**  
A: Because it's a great sport with limited analytics tools. We're fixing that.

---

## License

Private repository. Contact the maintainer for usage inquiries.

---

## Links

- **Live site**: [sportnumerics.com](https://sportnumerics.com)
- **Product roadmap**: [PRODUCT-IDEAS.md](PRODUCT-IDEAS.md)
- **Maintenance log**: [MAINTENANCE-2026.md](MAINTENANCE-2026.md)
