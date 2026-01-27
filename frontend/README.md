# Sportnumerics Frontend

Next.js application for displaying lacrosse rankings and statistics.

## Tech Stack

- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Deployment**: AWS S3 + CloudFront CDN
- **Data Source**: Server-side fetch from S3 (Parquet files)

---

## Development

### Prerequisites
- Node.js 20+
- npm

### Setup
```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Environment Variables

Create `.env.local` for local development:
```bash
# AWS credentials for fetching data from S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-west-2
```

**Note**: In production, credentials are managed via IAM roles (no env vars needed).

---

## Project Structure

```
app/
├── [year]/                    # Dynamic routes by season
│   ├── page.tsx               # Rankings landing page
│   ├── [div]/                 # Division-specific pages
│   │   ├── teams/page.tsx     # Team list
│   │   └── players/page.tsx   # Player list
│   ├── teams/[team]/page.tsx  # Individual team page
│   ├── players/[player]/page.tsx  # Individual player page
│   └── games/[game]/page.tsx  # Game details
│
├── components/                # Reusable UI components
│   ├── Link.tsx               # Internal navigation
│   ├── Opponent.tsx           # Opponent display
│   └── TeamList.tsx           # Ranked team table
│
├── server/                    # Server-side data fetching
│   ├── source.ts              # S3 client and data loading
│   ├── teams.ts               # Team rankings logic
│   ├── players.ts             # Player stats logic
│   └── years.ts               # Available seasons
│
├── shared.tsx                 # Common UI components (H1, Card, Table)
├── formatting.tsx             # Date/number formatting utilities
└── layout.tsx                 # Root layout (header, nav)
```

---

## Key Features

### Server-Side Rendering (SSR)
- All pages use `async` components to fetch data server-side
- Data loaded from S3 Parquet files on each request
- No client-side JavaScript needed for initial render

### Dynamic Routes
- `/[year]` - Season selector (e.g., `/2025`)
- `/[year]/[div]/teams` - Division teams (e.g., `/2025/ncaa1/teams`)
- `/[year]/teams/[team]` - Team page (e.g., `/2025/ml-ncaa-duke`)
- `/[year]/players/[player]` - Player page

### Caching
- CloudFront caches pages globally
- S3 data files include `Last-Modified` headers
- `lastModified` displayed on pages for transparency

---

## Data Flow

1. User requests page (e.g., `/2025/ncaa1/teams`)
2. Next.js server-side component runs
3. `server/source.ts` fetches Parquet from S3
4. Data parsed and rendered to HTML
5. HTML sent to client (fast first paint)
6. CloudFront caches response (subsequent requests instant)

---

## Building for Production

```bash
npm run build
npm start  # Test production build locally
```

**Output**: `.next/` directory with optimized static + server assets.

### Deployment

GitHub Actions handles deployment:
1. `npm run build` in CI
2. Upload `.next/` to S3
3. Invalidate CloudFront cache

See `../.github/workflows/deploy-frontend.yml` for details.

---

## Common Tasks

### Add a New Page
1. Create `app/[route]/page.tsx`
2. Make component `async` for SSR
3. Fetch data via `server/source.ts`
4. Return JSX using `shared.tsx` components

Example:
```tsx
'use server';
import { getTeamStats } from "@/app/server/teams";
import { H1, Card } from "@/app/shared";

export default async function Page({ params }: { params: { team: string } }) {
    const { body: team } = await getTeamStats(params);
    return <>
        <H1>{team.name}</H1>
        <Card title="Stats">
            {/* ... */}
        </Card>
    </>
}
```

### Add New Data Field
1. Update backend to include field in Parquet output
2. Update type in `server/source.ts` (or create new interface)
3. Display in relevant page component

### Styling
- Use Tailwind classes: `className="text-lg font-bold"`
- Shared components in `shared.tsx` handle common patterns
- Tables: Use `<Table>`, `<TableHeader>` for consistency

---

## Performance

**Current metrics** (from build output):
- First Load JS: ~96 KB (shared chunks)
- Page-specific JS: ~9 KB
- All pages server-rendered (no client-side data fetching)

**Optimization tips**:
- Keep client components minimal
- Use Next.js `<Image>` for images (auto-optimization)
- Leverage CloudFront caching (invalidate after deploys)

---

## Troubleshooting

### "Cannot connect to S3"
- Check AWS credentials in `.env.local`
- Ensure IAM role has `s3:GetObject` permission
- Verify bucket name in `server/source.ts`

### "Module not found"
- Run `npm install`
- Check import paths (use `@/app/...` for absolute imports)

### Build errors
- Run `npm run lint` to catch issues
- Check TypeScript errors: `npx tsc --noEmit`

---

## Contributing

- Follow TypeScript strict mode (no `any` types)
- Use ESLint config: `npm run lint`
- Test locally before pushing: `npm run build`
- Keep pages server-side rendered (avoid `'use client'` unless necessary)

See [../PRODUCT-IDEAS.md](../PRODUCT-IDEAS.md) for feature roadmap.
