# SEO Audit Tool Specification

## 1. Project Summary

A stateless SEO Audit Tool that accepts a single publicly accessible website URL, fully renders the page using Python Playwright, analyzes on-page SEO factors, computes deterministic SEO scores, and returns a cleaned audit payload to a modern dashboard.

The system consists of a Python FastAPI backend and a Next.js frontend using the App Router, TypeScript, and Tailwind CSS.

---

## 2. Finalized Scope

### In Scope for Version 1

- Accept only valid public `http://` and `https://` URLs.
- Audit a single publicly accessible webpage per request.
- Fully render JavaScript before extracting page data.
- Audit the final redirected URL and include redirect information as an informational result.
- Analyze on-page SEO factors only.
- Generate deterministic, rules-based scores and recommendations.
- Return both summary SEO scores and extracted SEO data to the frontend.
- Expose a REST API with OpenAPI/Swagger documentation.

### Excluded from Version 1

- Multi-page crawling or site-wide audits.
- Authentication-protected pages.
- Pages requiring login, cookies, or consent handling beyond normal page rendering.
- Performance-related audits such as Core Web Vitals, page speed, or Lighthouse metrics.
- Any persistent storage or audit history.
- Any live LLM inference for recommendations.

---

## 3. Functional Requirements

### User Input and Validation

- Accept a single URL per request.
- Validate that the URL is well-formed and uses `http` or `https`.
- Reject local/private IP ranges, localhost, and internal network addresses.
- Return clear error responses for invalid, unreachable, or unsupported URLs.

### Backend Processing

- Use Python FastAPI for the REST API.
- Use Python Playwright Async API to:
  - Launch a headless browser.
  - Navigate to the provided URL.
  - Wait for the page to finish rendering.
  - Capture the final redirected URL, response metadata, and rendered HTML.
- Extract on-page SEO signals from the fully rendered DOM.
- Apply deterministic rules to compute scores and produce recommendations.
- Build a JSON audit payload containing:
  - Final URL and redirect trail.
  - Metadata and extracted SEO values.
  - Category scores and overall SEO score.
  - Rule-based issue list and actionable recommendations.

### SEO Factors to Analyze

- Page title
- Meta description
- Canonical tag
- Heading hierarchy (`H1` through `H6`)
- Open Graph tags
- Twitter Card tags
- Image `alt` attributes
- Internal and external links
- Robots directives (`robots.txt` and `meta robots`)
- Other key on-page HTML signals relevant to SEO

### API and Documentation

- Provide a REST API endpoint for submitting URLs and retrieving audit results.
- Return JSON responses with a consistent payload schema.
- Expose OpenAPI/Swagger documentation automatically via FastAPI.
- Include API documentation for request/response models and error cases.

### Frontend Display

- Build a clean dashboard in Next.js App Router.
- Display summary scores and category breakdowns.
- Show raw extracted SEO data and key signals.
- Present actionable recommendations alongside issues.
- Use Tailwind CSS for responsive styling.

---

## 4. Non-Functional Requirements

- Stateless architecture: no database, no persisted user or audit state.
- Deterministic audit output for the same page input.
- Production-grade design: clearly separated frontend/backend, clean data contracts, and documented API.
- Secure handling of arbitrary URLs to reduce SSRF and abuse risk.
- Reliable error handling for unreachable sites, timeouts, invalid input, and browser failures.
- Observability-ready design through standard API response codes and structured JSON error payloads.

---

## 5. High-Level Architecture

### Components

- Frontend: Next.js App Router + TypeScript + Tailwind CSS
- Backend: Python FastAPI
- SEO Engine: Python Playwright Async API

### Data Flow

1. User submits a URL via the frontend.
2. Frontend sends a POST request to the FastAPI audit endpoint.
3. Backend validates the URL and launches Playwright.
4. Playwright navigates to the URL, fully renders the page, and captures the final state.
5. Backend extracts SEO signals and applies deterministic scoring rules.
6. Backend returns a JSON audit report.
7. Frontend renders summary metrics, category scores, extracted data, and recommendations.

### Deployment Considerations

- Backend must run in an environment with browser dependencies installed for Playwright.
- Frontend and backend may be deployed separately or together behind a reverse proxy.
- No persistent storage means the backend can scale horizontally without sticky session constraints.

---

## 6. Technology Stack

- Frontend: Next.js App Router, TypeScript, Tailwind CSS
- Backend: Python 3.11+ (or latest stable Python 3.x)
- Web framework: FastAPI
- Browser automation: Playwright Async Python
- API docs: FastAPI OpenAPI/Swagger
- Task orchestration: native async/await
- Static typing: TypeScript for frontend, type hints for backend

---

## 7. Folder Structure

A recommended project layout:

- `/app` or `/frontend` — Next.js application
  - `app/` — App Router pages and layout
  - `components/` — UI components
  - `lib/` — frontend utilities and data models
- `/api` or `/backend` — FastAPI application
  - `main.py` — FastAPI entry point
  - `routers/` — endpoint routes
  - `schemas/` — request and response Pydantic models
  - `services/` — Playwright orchestration and SEO extraction
  - `engine/` — deterministic scoring and recommendation rules
  - `utils/` — validation and helpers
- `README.md` — developer onboarding and setup
- `seo_tool_specs.md` — project specification (this document)

> If the repository remains small, a single `backend/` and `frontend/` root can be used.

---

## 8. API Design Principles

- Keep the API RESTful and resource-oriented.
- Use HTTP status codes consistently:
  - `200` for successful audits
  - `400` for invalid input
  - `422` for schema validation failures
  - `500` for internal errors
- Keep request payloads minimal: only submit the target URL.
- Return a structured JSON response with clear sections for:
  - request metadata
  - audit summary
  - score breakdown
  - extracted SEO data
  - recommendations
  - warnings and informational notes
- Ensure the API documentation clearly describes each field.

### Example API contract

- `POST /audit`
  - Request body: `{ "url": "https://example.com" }`
  - Response body:
    - `input_url`
    - `final_url`
    - `redirects`
    - `scores`
    - `results`
    - `recommendations`
    - `raw_data`

---

## 9. UI/UX Guidelines

- Use a modern dashboard layout with clear sections:
  - URL input and audit trigger
  - Overall SEO score
  - Category score cards
  - Key on-page SEO findings
  - Raw extracted metadata and HTML signals
  - Actionable recommendations and issue list
- Keep the interface responsive and accessible.
- Use color and iconography to highlight pass/fail status.
- Avoid clutter by collapsing low-priority details behind expandable sections.
- Show API or audit status feedback during processing.
- Provide clear error messages when the audit cannot complete.

---

## 10. Coding Standards and Development Constraints

- Frontend:
  - Use TypeScript with strict mode enabled.
  - Prefer functional components and React hooks.
  - Keep styling via Tailwind CSS classes.
  - Break UI into reusable components.
- Backend:
  - Use Pydantic models for request and response validation.
  - Keep Playwright browser sessions scoped per request.
  - Apply async/await consistently.
  - Log errors with enough context for troubleshooting.
- Recommendation Engine:
  - Use deterministic rule-based logic only.
  - Avoid any external AI service for Version 1.
- Testing:
  - Include API contract tests and validation tests for core rules.
  - Write unit tests for scoring logic and schema validation.

---

## 11. Assumptions

- The audit engine can fully render all JavaScript-driven pages within a reasonable timeout.
- The system is designed for single-page audits only.
- The environment supports Playwright browser execution.
- The frontend and backend communicate over a JSON REST API.
- Recommendations are generic SEO guidance, not personalized consultancy.
- No persistent data means the system can be horizontally scaled without state replication.

---

## 12. Risks and Mitigations

- SSRF / arbitrary site scanning risk
  - Mitigate with strict URL validation and public-only URL checks.
- Browser execution failures
  - Use timeouts and fallback error handling.
- High latency for JS-heavy pages
  - Document expected audit response times and optimize wait strategy.
- Deterministic rule gaps
  - Keep rules explicit and document scoring rationale.

---

## 13. Next Steps

- Establish the repository structure for `frontend/` and `backend/`.
- Define detailed API schema in `backend/schemas`.
- Implement the FastAPI audit endpoint and Playwright orchestration.
- Build the deterministic scoring and recommendation engine.
- Create the Next.js dashboard to consume and display audit payloads.
- Add automated tests for validation, scoring, and API behavior.
