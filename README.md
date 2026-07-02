# SEO Checker

> A production-grade, stateless SEO Audit Tool. Submit any publicly accessible URL and receive a comprehensive SEO report — complete with a weighted overall score, category breakdowns, extracted metadata, detected issues, and actionable recommendations.

**Live demo:** [seo-checker-sadik-w3.vercel.app](https://seo-checker-sadik-w3.vercel.app)  
**API:** [seo-checker-backend-x38s.onrender.com](https://seo-checker-backend-x38s.onrender.com)  
**API Docs:** [seo-checker-backend-x38s.onrender.com/docs](https://seo-checker-backend-x38s.onrender.com/docs)  
**Repo:** [github.com/SadikMR/SEO-Checker-Sadik](https://github.com/SadikMR/SEO-Checker-Sadik)

> ⏱️ **Note:** The backend runs on Render's free tier and may take 30–50 seconds to wake up after a period of inactivity. Subsequent requests are fast.

---

## Features

- **10 SEO audit checks:** Title tag, meta description, canonical URL, heading structure (H1–H6), Open Graph tags, Twitter Card tags, image alt attributes, internal/external links, robots directives (meta + robots.txt), and structured data (JSON-LD / Microdata)
- **Weighted scoring engine:** Overall SEO score (0–100) computed from 7 categories with configurable weights
- **Deterministic recommendations:** Rules-based, no AI or external services
- **Full-page JavaScript rendering** via Playwright (Chromium)
- **SSRF protection:** Blocks private IPs, localhost, and internal hostnames
- **robots.txt checking:** Verifies Googlebot access at the URL level
- **Modern dashboard:** Score ring with grade, per-category mini-charts, tabbed raw data explorer
- **Stateless design:** No database, no auth, horizontally scalable
- **Interactive API docs** at `/docs` (FastAPI OpenAPI/Swagger)

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | Python 3.13+, FastAPI |
| Browser automation | Playwright (Chromium, Async API) |
| HTML parsing | BeautifulSoup4 |
| API docs | FastAPI OpenAPI / Swagger UI |
| Frontend hosting | Vercel (free) |
| Backend hosting | Render (free, Docker) |

---

## Project Structure

```
SEO-Checker-Sadik/
├── backend/
│   ├── main.py                   # FastAPI entry point, CORS, lifespan
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Production Docker image (for Render)
│   ├── .dockerignore
│   ├── engine/
│   │   ├── pipeline.py           # Orchestrates all audit modules
│   │   ├── scorer.py             # Weighted scoring engine
│   │   └── rules/                # Individual audit rule modules
│   │       ├── title.py
│   │       ├── description.py
│   │       ├── canonical.py
│   │       ├── headings.py
│   │       ├── open_graph.py
│   │       ├── twitter_card.py
│   │       ├── images.py
│   │       ├── links.py
│   │       ├── robots.py
│   │       └── structured_data.py
│   ├── routers/
│   │   └── audit.py              # POST /audit endpoint
│   ├── schemas/
│   │   ├── audit.py              # Request / response models
│   │   ├── issues.py             # Issue and recommendation models
│   │   ├── scores.py             # Score and category models
│   │   └── seo_data.py           # Raw SEO signal models
│   ├── services/
│   │   ├── browser_manager.py    # Singleton Playwright browser
│   │   └── renderer.py           # Page rendering service
│   └── utils/
│       └── url_validator.py      # SSRF protection / URL validation
├── frontend/
│   ├── app/
│   │   ├── layout.tsx            # Root layout and metadata
│   │   ├── page.tsx              # Main page (URL form + states)
│   │   ├── globals.css           # Global styles
│   │   ├── components/
│   │   │   ├── AuditSummary.tsx  # Full results dashboard
│   │   │   ├── UrlForm.tsx       # URL input form component
│   │   │   └── useAudit.ts       # Audit state hook
│   │   └── lib/
│   │       ├── api.ts            # Typed API client
│   │       └── types.ts          # TypeScript interfaces
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
├── render.yaml                   # Render deployment config
├── vercel.json                   # Vercel deployment config
├── seo_tool_specs.md             # Project specification
├── DEVELOPMENT_WORKFLOW.md       # Git and development guidelines
└── README.md
```

---

## Screenshots

A selection of dashboard and audit screenshots is available in the [screenshots](screenshots) folder:

- [Homepage](screenshots/Homepage.png)
- [Audit Analysis](screenshots/Audit_Analyzing.png)
- [Audit Report 1](screenshots/Audit-Report-1.png)
- [Audit Report 2](screenshots/Audit_Report-2.png)
- [Audit Report Moderate 1](screenshots/Audit_Report_Moderate-1.png)
- [Audit Report Moderate 2](screenshots/Audit_Report_Moderate-2.png)

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11 or later |
| Node.js | 18 or later |
| npm | 9 or later |

> **macOS note:** Playwright requires certain system libraries. Run `playwright install-deps chromium` if you encounter missing dependency errors.

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/SadikMR/SEO-Checker-Sadik.git
cd SEO-Checker-Sadik
```

### 2. Backend setup

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser binaries (Chromium only)
playwright install chromium
```

### 3. Frontend setup

```bash
cd ../frontend
npm install
```

---

## Environment Variables

### Backend

The backend uses no environment variables. CORS origins and timeouts are configured in source code.

To change the allowed frontend origin, edit `allow_origins` in `backend/main.py`.

### Frontend

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Base URL of the backend API |

Create a `.env.local` file in the `frontend/` directory to override:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running Locally

### Start the backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**.  
Interactive API docs: **http://localhost:8000/docs**

### Start the frontend

Open a second terminal:

```bash
cd frontend
npm run dev
```

The frontend will be available at **http://localhost:3000**.

---

## Installing Playwright Browser Binaries

Playwright requires the Chromium browser binary to be installed separately from the Python package:

```bash
# Inside the backend virtual environment
source venv/bin/activate
playwright install chromium
```

To also install system-level OS dependencies (Linux/CI environments):

```bash
playwright install-deps chromium
```

> The backend will fail to start if Chromium is not installed. You will see a `BrowserType.launch: Executable doesn't exist` error.

---

## Deployment

The project is deployed for free using **Vercel** (frontend) and **Render** (backend).

### Live URLs

| Service | URL |
|---|---|
| Frontend | https://seo-checker-sadik-w3.vercel.app |
| Backend API | https://seo-checker-backend-x38s.onrender.com |
| API Docs | https://seo-checker-backend-x38s.onrender.com/docs |

### Deploy your own instance

#### Backend → Render (free)

1. Go to [render.com](https://render.com) and connect your GitHub repo
2. Create a new **Web Service**
3. Set **Root Directory** to `backend`, **Runtime** to `Docker`, **Plan** to `Free`
4. Render will build the `backend/Dockerfile` automatically

#### Frontend → Vercel (free)

1. Go to [vercel.com/new](https://vercel.com/new) and import `SadikMR/SEO-Checker-Sadik`
2. In the **Configure Project** screen, set **Root Directory** to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-render-backend-url.onrender.com`
4. Click **Deploy**

> **Important:** `NEXT_PUBLIC_API_URL` is baked into the Next.js build at compile time. If you change it after deploying, you must **redeploy** (not just save the env var).

---

## API Endpoints

### `GET /health`

Health check — confirms the API is running.

**Response `200`:**
```json
{ "status": "ok" }
```

---

### `POST /audit`

Run a full SEO audit on a publicly accessible URL.

**Request body:**
```json
{
  "url": "https://example.com"
}
```

**Response `200` — `AuditResponse`:**
```json
{
  "input_url": "https://example.com",
  "final_url": "https://example.com",
  "redirects": [],
  "scores": {
    "overall_score": 51.3,
    "categories": [
      { "category": "meta", "label": "Meta Tags", "score": 24.4, "max_score": 100.0 },
      { "category": "headings", "label": "Headings", "score": 100.0, "max_score": 100.0 }
    ]
  },
  "results": [
    {
      "rule_id": "title_too_short",
      "category": "meta",
      "severity": "warning",
      "message": "Title is only 14 characters. Recommended minimum is 30.",
      "value": "Example Domain"
    }
  ],
  "recommendations": [
    {
      "rule_id": "title_too_short",
      "category": "meta",
      "severity": "warning",
      "message": "Expand the title to at least 30 characters to improve search visibility."
    }
  ],
  "raw_data": {
    "meta": { "title": "Example Domain", "title_length": 14, "description": null, "canonical": null },
    "headings": { "h1": ["Example Domain"], "h1_count": 1, "h2": [], ... },
    "open_graph": { "og_title": null, "og_description": null, "og_image": null, ... },
    "twitter_card": { "card": null, "title": null, ... },
    "images": { "total_images": 0, "images_with_alt": 0, "images_without_alt": 0 },
    "links": { "total_links": 1, "internal_links": 0, "external_links": 1, "nofollow_links": 0 },
    "robots": { "meta_robots": null, "x_robots_tag": null, "robots_txt_disallowed": false },
    "structured_data": { "has_json_ld": false, "json_ld_types": [], "has_microdata": false, "microdata_types": [] }
  }
}
```

**Error responses:**

| Status | Cause |
|---|---|
| `400` | Invalid URL, private IP, unreachable page |
| `422` | Malformed request body (Pydantic validation) |
| `504` | Page load timed out (default: 30 seconds) |
| `500` | Internal rendering or processing error |

---

## Scoring Methodology

The overall SEO score (0–100) is a weighted average of 7 categories:

| Category | Weight | Checks Included |
|---|---|---|
| Meta Tags | **30%** | Title tag, meta description, canonical URL |
| Social Tags | **15%** | Open Graph (og:title/description/image), Twitter Card |
| Headings | **15%** | H1 presence and uniqueness, heading hierarchy |
| Images | **10%** | Alt attribute coverage |
| Links | **10%** | Internal and external link presence |
| Robots | **10%** | noindex/nofollow directives, robots.txt access |
| Structured Data | **10%** | JSON-LD and Microdata presence |

Category scores are averaged from their constituent rule scores. The overall score is a weighted sum, normalised if any category is absent.

---

## Usage Guide

1. Open [seo-checker-sadik-w3.vercel.app](https://seo-checker-sadik-w3.vercel.app) or **http://localhost:3000** locally
2. Enter a full URL including the scheme (e.g. `https://example.com`)
3. Click **Analyse** — the audit typically takes 10–30 seconds
4. Review the results dashboard:
   - **Score banner** — overall score (0–100) with letter grade (A–F)
   - **Category cards** — per-category scores with mini donut charts
   - **Issues** — grouped by severity (Critical → Warning → Info)
   - **Recommendations** — numbered, prioritised action items
   - **Extracted SEO Data** — tabbed panel covering all audited signals

---

## Development Workflow

The project follows a phase-by-phase development process defined in [`DEVELOPMENT_WORKFLOW.md`](./DEVELOPMENT_WORKFLOW.md).

### Git branching

```bash
# Create a feature branch before starting any task
git checkout -b feature/your-feature-name

# Make atomic commits following Conventional Commits
git commit -m "feat: add canonical tag audit rule"
git commit -m "fix: correct robots.txt URL parser"

# Merge back to main when complete
git checkout main
git merge feature/your-feature-name
```

### Adding a new audit rule

1. Create `backend/engine/rules/your_rule.py` — return a dataclass with `score`, `issues`, `recommendations`
2. Add your category to `CategoryName` in `backend/schemas/scores.py` (if new)
3. Add a weight for the new category in `backend/engine/scorer.py` → `CATEGORY_WEIGHTS` (ensure weights still sum to 1.0)
4. Register the rule in `backend/engine/pipeline.py`
5. Add the raw data model to `backend/schemas/seo_data.py` and `RawSEOData`
6. Update the TypeScript types in `frontend/app/lib/types.ts`
7. Display the new data in `frontend/app/components/AuditSummary.tsx`

### Type checking

```bash
# Frontend
cd frontend && npx tsc --noEmit

# Backend (optional, requires mypy)
cd backend && mypy . --ignore-missing-imports
```

---

## Troubleshooting

### `playwright._impl._errors.Error: Executable doesn't exist`

Chromium is not installed. Run:

```bash
source backend/venv/bin/activate
playwright install chromium
```

### `Cannot find module 'pydantic'` or `ModuleNotFoundError`

The virtual environment is not activated or dependencies are not installed:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend shows "API Offline" badge

**Locally:** Ensure the backend is running (`uvicorn main:app --reload` in `backend/`).

**On Vercel:** The `NEXT_PUBLIC_API_URL` env var was not set before the build ran. Fix:
1. Vercel → Settings → Environment Variables → add `NEXT_PUBLIC_API_URL`
2. Deployments → Redeploy (a new build is required — env vars are baked in at build time)

### Audit returns `504 Gateway Timeout`

The target page took longer than 30 seconds to load. The timeout is configurable in `backend/services/renderer.py` → `DEFAULT_TIMEOUT_MS`.

### First request on Render is very slow (30–50 seconds)

This is expected on the free tier. Render spins down the service after 15 minutes of inactivity. The first request wakes it up. Subsequent requests are fast.

### CORS errors in browser console

Update `allow_origin_regex` in `backend/main.py` to include your frontend's origin.

### `http://localhost` returns 400

This is expected. The URL validator blocks `localhost`, private IP addresses, and internal hostnames to prevent SSRF attacks.

---

## Future Enhancements

- **API contract and unit tests** — pytest for backend rules and scoring; Jest/Vitest for frontend components
- **PDF / shareable report export** — generate a downloadable audit report
- **Page speed metrics** — Core Web Vitals, LCP, CLS integration
- **Multi-page crawling** — site-wide SEO audit mode
- **Robots.txt async check** — replace synchronous fetch with async HTTP client
- **Configurable scoring weights** — expose `CATEGORY_WEIGHTS` via API or environment variables
- **AI-assisted recommendations** — optional LLM suggestions as a post-processing layer
- **CI/CD pipeline** — GitHub Actions for linting, type-checking, and test runs

---

## License

This project is unlicensed. All rights reserved.
