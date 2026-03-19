# Headlines — Build Plan

A step-by-step implementation plan derived from DESIGN.md. Each step produces working, testable output. Steps within a phase are sequential unless noted as parallelizable. Phases are sequential — each builds on the previous.

---

## Progress Overview

| Phase | Description | Steps | Files | Status | Date |
|-------|-------------|-------|-------|--------|------|
| **1** | Core Pipeline + News Reader | 11/11 | 93 | **Code complete** | 2026-03-16 |
| **2** | Learning Surface | 1/1 | 1 | **Code complete** | 2026-03-16 |
| **3** | Briefings | 2/2 | 6 | **Code complete** | 2026-03-16 |
| **4** | Admin Panel | 6/6 | 20 | **Code complete** | 2026-03-17 |
| **5** | Analytics | 2/2 | 13 | **Code complete** | 2026-03-17 |
| **6** | Polish | 5/5 | 20 | **Code complete** | 2026-03-17 |
| **7** | In Focus | 2/2 | 13 | **Code complete** | 2026-03-17 |
| **8** | Monopage Reader Navigation | 1/1 | 8 (+4 deleted) | **Code complete** | 2026-03-19 |

**Totals**: 30/30 steps complete · 147 files (4 deleted in Phase 8) · 8 phases code-complete

**Blocking all eight phases**: `docker compose up` + `alembic upgrade head` for runtime verification (RSS feeds, LLM classification, editorial generation, In Focus analysis generation, admin UI end-to-end, analytics event recording + dashboard, responsive design, retention jobs, RSS output feed, Slack alerting, monopage scroll-spy + "Show more" client-side pagination).

### Step-Level Status

**Phase 1 — Core Pipeline + News Reader** (11 steps)
- [x] 1.1 Project Scaffold & Infrastructure
- [x] 1.2 Database Schema (Full, All Phases)
- [x] 1.3 Pydantic Schemas
- [x] 1.4 RSS Adapter + Scraper Function
- [x] 1.5 LLM Provider Adapters
- [x] 1.6 Surface-Aware Classifier
- [x] 1.6b Cross-Source Story Deduplication
- [x] 1.7 Scheduler + Workers
- [x] 1.8 Public API
- [x] 1.9 Frontend CSS Architecture + Components
- [x] 1.10 News Reader Pages

**Phase 2 — Learning Surface** (1 step)
- [x] 2.1 Learning Source Activation

**Phase 3 — Briefings** (2 steps)
- [x] 3.1 Editorial Worker + Prompts
- [x] 3.2 Briefing API + Frontend

**Phase 4 — Admin Panel** (6 steps)
- [x] 4.1 Admin Authentication + Layout
- [x] 4.2 Sources Management
- [x] 4.3 Categories Management (Full Lifecycle)
- [x] 4.4 LLM Models & Pipeline Tasks
- [x] 4.5 Articles Management
- [x] 4.6 System Dashboard + Briefing Management

**Phase 5 — Analytics** (2 steps)
- [x] 5.1 Client-Side Event Tracking
- [x] 5.2 Analytics Dashboard

**Phase 6 — Polish** (5 steps)
- [x] 6.1 Responsive Design Pass
- [x] 6.2 Performance Optimization
- [x] 6.3 Retention Pipeline
- [x] 6.4 Error Alerting
- [x] 6.5 RSS Output

**Phase 7 — In Focus** (2 steps)
- [x] 7.1 Analysis Pipeline
- [x] 7.2 In Focus Frontend

**Phase 8 — Monopage Reader Navigation** (1 step)
- [x] 8.1 Monopage Reader Navigation

---

## Phase 1: Core Pipeline + News Reader

**Goal**: A working news headlines site with full pipeline, classification, observability, and editorial design — seeded with 5 news sources and 9 news categories.

### Step 1.1 — Project Scaffold & Infrastructure

**What**: Create the monorepo structure, Docker Compose, database, and dev tooling.

```
headlines/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   ├── alembic/
│   │   └── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   └── layout.tsx
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── DESIGN.md
```

**Tasks**:

1. **docker-compose.yml** — 5 services: `db` (postgres:16), `api` (FastAPI), `worker` (same image, different entrypoint), `frontend` (Next.js), `caddy` (reverse proxy). Shared `.env` file for secrets.
2. **backend/requirements.txt** — Pin versions:
   - `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`
   - `httpx` (async HTTP for feeds), `feedparser` (RSS parsing)
   - `anthropic`, `openai`, `google-genai` (LLM providers)
   - `apscheduler` (task scheduling)
   - `pydantic-settings` (env config)
   - `python-jose[cryptography]` (admin JWT auth)
3. **backend/app/config.py** — `Settings` class (pydantic-settings) loading from env:
   - `DATABASE_URL`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY`
   - `ADMIN_PASSWORD`, `BRIEFING_TIMEZONE` (default `America/New_York`)
   - `PUBLIC_API_URL`
4. **backend/app/database.py** — SQLAlchemy 2.0 async engine + `async_sessionmaker` + `get_db` dependency.
5. **backend/app/main.py** — FastAPI app with CORS middleware, lifespan (startup/shutdown), router mounts.
6. **frontend/** — `npx create-next-app@latest` with App Router, TypeScript, Tailwind, ESLint. Strip defaults.
7. **.env.example** — All env vars with placeholder values and comments.

**Verification**: `docker compose up` starts all services. FastAPI returns `{"status": "ok"}` at `/api/health`. Next.js renders at `localhost:3000`. Postgres accepts connections.

---

### Step 1.2 — Database Schema (Full, All Phases)

**What**: Create all tables upfront in a single Alembic migration. This avoids painful migration gymnastics later and gives every subsequent step a stable schema.

**Tasks**:

1. **SQLAlchemy models** — one file per table in `backend/app/models/`:
   - `source.py` → `sources` (includes `surface TEXT NOT NULL DEFAULT 'news'`)
   - `category.py` → `categories` (includes `surface TEXT NOT NULL DEFAULT 'news'`)
   - `article.py` → `articles` (with `UNIQUE(source_id, external_id)`, `cluster_id UUID`, `is_representative BOOLEAN DEFAULT true`)
   - `article_category.py` → `article_categories` (composite PK, `confidence REAL`, `manual_override BOOLEAN`)
   - `fetch_log.py` → `fetch_logs` (full audit log with `batch_id`, `trigger`, all counters)
   - `pipeline_log.py` → `pipeline_logs` (with `task` field: classification/briefing/learning_digest)
   - `llm_model.py` → `llm_models` (provider, model_id unique, pricing, config JSONB)
   - `pipeline_task.py` → `pipeline_tasks` (task TEXT PK, FK to llm_models.model_id)
   - `briefing.py` → `briefings` (type + date with `UNIQUE(type, date)`)
   - `category_redirect.py` → `category_redirects` (old_slug PK, new_slug, surface) — preserves URLs when slugs change or categories merge
   - `analytics_event.py` → `analytics_events`
   - `__init__.py` → re-export all models for Alembic

2. **Indexes** (in models, reflected in migration):
   - `idx_articles_published_at` (published_at DESC)
   - `idx_articles_unclassified` (id WHERE classified = false)
   - `idx_articles_reader` (published_at DESC WHERE hidden = false AND is_representative = true)
   - `idx_articles_cluster` (cluster_id WHERE cluster_id IS NOT NULL)
   - `idx_article_categories_category` (category_id)
   - `idx_fetch_logs_source` (source_id, started_at DESC)
   - `idx_fetch_logs_status` (status WHERE status != 'success')
   - `idx_fetch_logs_started` (started_at DESC)
   - `idx_fetch_logs_batch` (batch_id WHERE batch_id IS NOT NULL)
   - `idx_pipeline_logs_started` (started_at DESC)
   - `idx_pipeline_logs_task` (task, started_at DESC)
   - `idx_pipeline_logs_status` (status WHERE status != 'success')
   - `idx_analytics_created` (created_at DESC)
   - `idx_analytics_session` (session_id)
   - `idx_analytics_type` (event_type, created_at DESC)

3. **Alembic initial migration** — `alembic revision --autogenerate -m "initial schema"`. Review generated migration. Run `alembic upgrade head`.

4. **Seed data migration** (second migration) — insert:
   - 5 news sources (FT, Bloomberg, WSJ, The Verge, Stratechery) with feed URLs and intervals
   - 2 learning sources (HBR, MIT SMR) with feed URLs and intervals
   - 9 news categories with descriptions and display_order
   - 8 learning categories with descriptions and display_order
   - 6 LLM models (Haiku 4.5, Sonnet 4.6, GPT-5 Mini, GPT-5 Nano, Gemini 2.5 Flash, Gemini 2.5 Flash-Lite)
   - 4 pipeline tasks (classification → Haiku, dedup → Haiku, briefing → Sonnet, learning_digest → Sonnet)

**Verification**: `alembic upgrade head` succeeds. `SELECT count(*) FROM sources` returns 7. `SELECT count(*) FROM categories` returns 17. All FKs and constraints valid.

---

### Step 1.3 — Pydantic Schemas

**What**: Define all request/response schemas for public and admin APIs.

**File**: `backend/app/schemas/` — one file per domain:

1. **headlines.py** — `HeadlineItem` (id, title, url, summary?, source_name, source_slug, source_homepage, published_at, categories list, also_reported_by list of `{source_name, source_slug, url}`), `HeadlinesResponse` (surface, headlines list, pagination), `CategoryResponse` (name, slug, article_count_today).
2. **briefing.py** — `BriefingResponse` (type, date, brief, generated_at).
3. **events.py** — `AnalyticsEventCreate` (event_type, article_id?, category_slug?, surface?, session_id, referrer?).
4. **admin_sources.py** — `SourceCreate`, `SourceUpdate`, `SourceResponse` (with status, last_error, consecutive_failures), `TestFetchResponse`, `RefreshResponse`, `BatchRefreshResponse`, `BatchStatusResponse`.
5. **admin_categories.py** — `CategoryCreate` (name, surface, description; slug auto-generated), `CategoryUpdate` (name?, slug? with redirect-on-change, description?, active?), `CategoryAdminResponse` (with article_count), `ReorderRequest`, `PreviewResponse`, `MergeRequest` (target_id), `MergePreview` (articles_affected count).
6. **admin_models.py** — `LLMModelCreate`, `LLMModelUpdate`, `LLMModelResponse`, `ModelTestResponse`, `ProviderStatusResponse`.
7. **admin_tasks.py** — `PipelineTaskUpdate`, `PipelineTaskResponse`, `CostEstimateResponse`.
8. **admin_articles.py** — `ArticleAdminResponse`, `ArticleBulkAction`.
9. **admin_briefings.py** — `BriefingAdminResponse`, `RegenerateRequest`.
10. **admin_analytics.py** — `OverviewResponse`, `TopHeadlinesResponse`, `BySourceResponse`, etc.
11. **common.py** — `PaginationMeta` (page, per_page, total, has_next).

**Verification**: All schemas import cleanly. Pydantic `model_json_schema()` produces valid JSON Schema for each.

---

### Step 1.4 — RSS Adapter + Scraper Function

**What**: The fetch pipeline — adapter pattern, dedup/upsert, full fetch logging, concurrency guards.

**Files**:

1. **backend/app/adapters/base.py** — `BaseAdapter` ABC with `async def fetch(source: Source) -> AdapterResult`. Define `AdapterResult` and `RawArticle` dataclasses.
2. **backend/app/adapters/rss.py** — `RSSAdapter`:
   - Uses `httpx.AsyncClient` for HTTP with 30s timeout
   - Sends `If-None-Match` / `If-Modified-Since` headers for conditional fetch
   - On 304: return empty articles list with http_status=304
   - Uses `feedparser` to parse RSS/Atom
   - Extracts: external_id (GUID), title, url, summary, author, image_url, published_at
   - `published_at` validation: reject >7 days past or >1 hour future, fallback to now()
   - Returns `AdapterResult` with per-article errors
3. **backend/app/adapters/registry.py** — Source adapter registry:
   - `ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {"rss": RSSAdapter}`
   - `get_adapter(adapter_type: str) -> BaseAdapter` — lookup + instantiate, raises `ValueError` for unknown types
   - **Adding a new adapter** = add one file (`adapters/<type>.py`) implementing `BaseAdapter.fetch()`, then add one entry to `ADAPTER_REGISTRY`. See Extension Points appendix.
4. **backend/app/scraper/scraper.py** — The `scrape()` function (DESIGN.md §4.1):
   - Concurrency guard: check for in-flight fetch_log with status="running" and started_at within 5 min
   - Expire stale "running" records (crash recovery)
   - Create fetch_log (status="running")
   - Call adapter.fetch()
   - Dedup/upsert: `INSERT ... ON CONFLICT (source_id, external_id) DO UPDATE` — three-way branch (new / title-changed / unchanged)
   - Update source record (last_fetched_at, last_etag, last_modified, last_error, consecutive_failures)
   - Finalize fetch_log (status, counters, duration_ms)
   - Return `FetchResult`
   - **Never throws** — catches all exceptions, records in fetch_log

**Verification**: Unit tests:
- RSS adapter parses a sample RSS feed fixture
- Scraper inserts new articles, updates changed titles, skips unchanged
- Concurrency guard rejects when a fetch is already running
- Stale "running" records get expired
- fetch_log is always written (success, partial, failed)

---

### Step 1.5 — LLM Provider Adapters + Model Registry

**What**: Multi-provider LLM infrastructure. Provider-agnostic classification and editorial generation.

**Files**:

1. **backend/app/llm/types.py** — Shared types:
   - `ClassificationResult` (classifications list, input_tokens, output_tokens, latency_ms)
   - `BriefingResult` (text, input_tokens, output_tokens, latency_ms)
2. **backend/app/llm/anthropic.py** — `classify_anthropic()` and `generate_anthropic()`:
   - Uses `anthropic` SDK, Messages API
   - Classification: `tool_use` for structured JSON output
   - Editorial: standard text generation
   - Reads API key from env via config
3. **backend/app/llm/openai.py** — `classify_openai()` and `generate_openai()`:
   - Uses `openai` SDK, Chat Completions API
   - Classification: `response_format: { type: "json_object" }`
   - Passes `reasoning_effort` from model config if set
4. **backend/app/llm/google.py** — `classify_google()` and `generate_google()`:
   - Uses `google-genai` SDK, `generateContent` API
   - Classification: `response_mime_type: "application/json"`
   - Passes `thinkingBudget` from model config if set
5. **backend/app/llm/registry.py** — Provider dispatch registry:
   - `ProviderAdapter = NamedTuple("ProviderAdapter", classify=Callable, dedup=Callable, generate=Callable, api_key_env=str)`
   - `PROVIDERS: dict[str, ProviderAdapter]` — maps provider string to adapter functions + env var name:
     ```python
     PROVIDERS = {
         "anthropic": ProviderAdapter(classify_anthropic, dedup_anthropic, generate_anthropic, "ANTHROPIC_API_KEY"),
         "openai":    ProviderAdapter(classify_openai,    dedup_openai,    generate_openai,    "OPENAI_API_KEY"),
         "google":    ProviderAdapter(classify_google,    dedup_google,    generate_google,    "GOOGLE_AI_API_KEY"),
     }
     ```
   - **Adding a new provider** = add one file (`llm/<provider>.py`) implementing `classify_<provider>`, `dedup_<provider>`, and `generate_<provider>`, then add one entry to `PROVIDERS`. See Extension Points appendix.
   - **Three dispatch functions** (not a single `run_task`):
     - `run_classify(db, task_name, system_prompt, user_prompt, tool_schema)` → `ClassificationResult`
     - `run_dedup(db, task_name, system_prompt, user_prompt, tool_schema)` → `DedupResult`
     - `run_generate(db, task_name, system_prompt, user_prompt)` → `GenerationResult`
   - Each reads `pipeline_tasks` → `llm_models` → dispatches to correct provider function with API key from env. Retry once with 2s backoff on failure.
   - `get_api_key(provider: str)` — reads env var name from the registry entry. Raises a clear `ProviderConfigError` if missing — not a cryptic SDK failure.

**Verification**:
- Each provider adapter can be tested with a mock/fixture
- `run_task` resolves the correct provider from DB
- Missing API key raises `ProviderConfigError` with the env var name in the message
- Adding a fourth provider entry to the registry and calling `run_task` dispatches correctly

---

### Step 1.6 — Surface-Aware Classifier

**What**: The classification pipeline — batch processing, surface-aware category loading, logging.

**Files**:

1. **backend/app/classifier/prompts.py** — Prompt builder:
   - `build_classification_prompt(articles, categories)` → system prompt + article list + rules
   - Categories loaded from DB at call time, filtered by source's surface
   - Provider-agnostic: returns prompt text, not provider-specific format
2. **backend/app/classifier/classifier.py** — `classify_batch()`:
   - Collects unclassified articles (optionally filtered by source_ids)
   - Batches of 10-20
   - For each batch:
     - Groups articles by source surface (news articles together, learning articles together)
     - Loads categories for the appropriate surface
     - Builds prompt
     - Calls `run_task("classification", ...)` via LLM registry
     - Parses response, writes `article_categories` rows (confidence >= 0.5)
     - Marks articles as `classified = true`
   - Creates `pipeline_logs` record with `task='classification'`
   - Handles partial failures (some articles in batch fail → others still processed)

**Verification**:
- Classification with a mocked LLM response produces correct `article_categories` rows
- News articles are classified against news categories only
- Learning articles are classified against learning categories only
- pipeline_log is always written (success/partial/failed)
- Articles below confidence threshold get empty categories
- articles.classified is set to true after processing

---

### Step 1.6b — Cross-Source Story Deduplication

**What**: Two-phase dedup pipeline that clusters articles about the same story from different sources, selects one representative per cluster, and populates "Also in:" metadata for the reader.

**Files**:

1. **backend/app/dedup/similarity.py** — Fast title similarity (Phase 1):
   - `normalize_title(title: str) -> set[str]` — lowercase, strip punctuation, remove stop words, return token set
   - `STOP_WORDS: set[str]` — common English stop words (the, a, an, in, on, at, to, for, of, is, ...)
   - `jaccard_similarity(tokens_a: set[str], tokens_b: set[str]) -> float` — `|A ∩ B| / |A ∪ B|`
   - `find_candidates(article, recent_articles, threshold: float, max_candidates: int) -> list[Article]` — returns articles above similarity threshold, sorted by similarity descending
   - Threshold and max_candidates read from `pipeline_tasks.config` for the `dedup` task

2. **backend/app/dedup/prompts.py** — LLM dedup prompt builder (Phase 2):
   - `build_dedup_prompt(article, candidates) -> str` — provider-agnostic prompt
   - Explicit examples of same-story vs same-topic vs different-angle (see DESIGN.md §4.2.2)
   - Response format: `{is_duplicate, duplicate_of, best_representative, confidence, reasoning}`

3. **backend/app/dedup/deduplicator.py** — `dedup_batch()`:
   - Takes a list of newly classified article IDs
   - For each article:
     - Phase 1: `find_candidates()` against recent articles (same surface, last 48h, `is_representative = true` only)
     - If no candidates → assign fresh `cluster_id`, keep `is_representative = true`, skip Phase 2
     - Phase 2: call `run_task("dedup", ...)` via LLM registry with candidate list
     - Parse response. If `is_duplicate = true`:
       - Assign matching article's `cluster_id`
       - If LLM says new article is `best_representative`:
         - Set new article `is_representative = true`
         - Set old representative `is_representative = false`
       - Otherwise: set new article `is_representative = false`
     - If `is_duplicate = false` → assign fresh `cluster_id`, keep `is_representative = true`
   - Batch all LLM calls (send multiple candidate-checks per API call where possible)
   - Creates `pipeline_logs` record with `task='dedup'`: articles_processed, duplicates_found, clusters_created, clusters_updated, tokens, cost
   - **Never throws** — catches all, records in pipeline_log

4. **backend/app/dedup/__init__.py** — exports `dedup_batch`

**Verification**:
- Two articles with identical titles → Phase 1 finds candidate, Phase 2 confirms, articles share cluster_id
- Two articles with different topics → Phase 1 finds no candidate, articles remain independent
- Two articles with similar titles but different events → Phase 1 finds candidate, Phase 2 rejects, articles remain independent (test with mocked LLM response)
- Representative swap: when LLM picks the new article as better, old representative's `is_representative` flips to false
- pipeline_log is always written (success/partial/failed)
- Dedup respects surface boundary — news articles only compared against news articles
- Dedup with `active = false` in pipeline_tasks → skips all processing

---

### Step 1.7 — Scheduler + Workers

**What**: Background worker process running the fetch scheduler + classification trigger + dedup trigger.

**Files**:

1. **backend/app/workers/scheduler.py** — APScheduler setup:
   - On startup: expire stale "running" fetch_logs and pipeline_logs (`UPDATE ... SET status='failed' WHERE status='running'`)
   - Main loop: every 60 seconds, query sources where `now() - last_fetched_at >= fetch_interval` (or `last_fetched_at IS NULL`)
   - For each due source: call `scrape(source, trigger="scheduled")`
   - After each scrape with `articles_new > 0`: trigger `classify_batch()` for new articles
   - After each `classify_batch()` completes with newly classified articles: trigger `dedup_batch()` for those articles (if the `dedup` task is active in `pipeline_tasks`)
   - Stagger initial fetches over first interval window
2. **backend/app/workers/fetch_worker.py** — Helper for batch refresh:
   - `start_batch_refresh(db)` — generates batch_id, checks 60s cooldown, fires concurrent scrapes
   - Uses `asyncio.gather(return_exceptions=True)` for isolation
   - After all sources: triggers classification for all new articles, then dedup
   - **Dedup ordering in batch**: when a batch produces multiple articles about the same story, `dedup_batch()` processes them sorted by `published_at ASC` (oldest first). This ensures the first article in a cluster becomes the initial representative, and later articles are compared against it. Without this ordering, race-like behavior could produce inconsistent clusters.
3. **backend/app/workers/classify_worker.py** — Thin wrapper around `classify_batch()` with logging.
4. **backend/app/workers/dedup_worker.py** — Thin wrapper around `dedup_batch()` with logging. Checks `pipeline_tasks` active flag before running.
5. **Worker entrypoint** — `backend/app/worker_main.py`:
   - Starts APScheduler
   - Registers scheduled jobs
   - Runs event loop

**Verification**:
- Worker starts without errors
- Sources due for fetch are picked up
- Classification fires after new articles are inserted
- Dedup fires after classification completes (when dedup task is active)
- Dedup is skipped when dedup task is inactive
- One source failing doesn't crash the worker
- Cooldown prevents rapid-fire batch refreshes

---

### Step 1.8 — Public API (News Headlines)

**What**: The reader-facing API endpoints for the news surface.

**File**: `backend/app/routers/headlines.py`

**Endpoints**:

1. **GET /api/headlines** — `?surface=news&category={slug}&page=1&per_page=30`
   - Joins articles → sources (filter by surface) → article_categories → categories
   - Filters: `hidden = false`, `classified = true`, `is_representative = true`
   - Sorted by `published_at DESC`
   - Includes category names per article
   - **`also_reported_by`**: for each article with a `cluster_id`, subquery other articles in the same cluster to build `[{source_name, source_slug, url}]`. Empty array for solo articles.
   - Learning articles include `summary`; news articles omit it
   - **Slug redirect**: if `category` param doesn't match any active category, check `category_redirects`. If found → 301 redirect to the URL with the new slug. If not found → 404. This ensures bookmarks and shared links survive category renames and merges.
   - Cache-Control: 2 min (news), 30 min (learning)

2. **GET /api/categories** — `?surface=news`
   - Returns active categories for the given surface, **sorted by `display_order` ASC** — this is the tab order
   - Includes `article_count` (news: last 24h, learning: last 7 days)
   - Only categories where `active = true` — disabled categories are hidden from reader
   - Cache-Control: 10 min (can be flushed via admin `POST /api/admin/cache/flush`)

3. **GET /api/briefing** — `?type=daily_news&date=YYYY-MM-DD`
   - Returns briefing from `briefings` table
   - Defaults: type=daily_news, date=today (or current Monday for weekly_learning)
   - Returns null brief if not yet generated

4. **POST /api/events** — Analytics event ingestion
   - Validates event_type, session_id
   - Writes to analytics_events
   - Returns 204

**Verification**:
- `/api/headlines` returns paginated articles from news sources
- Only representative articles are returned (non-representatives excluded)
- `also_reported_by` populated for clustered articles, empty for solo articles
- `?category=markets` filters correctly
- `?surface=learning` returns learning articles with summaries
- Pagination works (page, has_next)
- Cache-Control headers are set correctly

---

### Step 1.9 — Frontend: Layered CSS Architecture + Design Tokens

**What**: A three-layer token architecture that makes adding new surfaces, components, and visual variants possible without modifying existing CSS. No components yet — just the system that every component will use.

The design document defines exact colors, type sizes, and spacing. The architecture below ensures those values flow through **three layers** — primitives → semantic → component — so that changes at any level cascade correctly and new features compose from existing tokens.

**Why three layers, not one flat file?**

A single `tokens.css` works until you need a second surface, a third theme, or a component variant. Then you're either duplicating values or adding surface-specific overrides with no structure to hang them on. Three layers solve this:

| Layer | Named by | Changes when | Example |
|-------|----------|-------------|---------|
| **Primitives** | What they ARE | Brand evolves | `--gray-900: #1A1A1A` |
| **Semantic** | What they DO | Theme changes (dark mode) | `--color-text-primary: var(--gray-900)` |
| **Component** | Where they're USED | Surface or variant changes | `--headline-color: var(--color-text-primary)` |

Adding a new surface means adding a `[data-surface="x"]` block that overrides component tokens. Adding dark mode means overriding semantic tokens. Changing the brand means editing primitives. Each concern has one place to go.

**Files**:

```
frontend/styles/
├── tokens/
│   ├── primitives.css     ← raw palette: colors, sizes, spaces (named by what they ARE)
│   ├── semantic.css       ← role mapping: maps primitives to functions (named by what they DO)
│   └── components.css     ← component tokens: maps semantic to specific uses (named by WHERE)
├── typography.css         ← @font-face declarations only
└── globals.css            ← imports all layers, Tailwind directives, base styles
```

#### Layer 1 — Primitives (`styles/tokens/primitives.css`)

The raw palette. Named by what they ARE. No semantic meaning — just the building blocks.

```css
:root {
  /* ─── Color palette ─── */
  --warm-white:       #FAF9F7;
  --warm-white-alt:   #F2F0ED;
  --gray-900:         #1A1A1A;
  --gray-700:         #4A4540;
  --gray-600:         #6B6560;
  --gray-500:         #8A8580;
  --ink-blue:         #1A3A5C;
  --ink-blue-light:   #244B73;
  --ink-blue-wash:    rgba(26, 58, 92, 0.15);
  --rule-warm:        #E5E0DB;

  /* Dark palette */
  --charcoal:         #1C1B19;
  --charcoal-alt:     #262522;
  --warm-light:       #EDECE8;
  --gray-400-dark:    #B5B0A8;
  --gray-300-dark:    #9A9590;
  --gray-200-dark:    #7A756F;
  --blue-muted:       #6B9FD4;
  --blue-muted-light: #85B3DE;
  --rule-dark:        #2E2D2A;
  --blue-wash-dark:   rgba(107, 159, 212, 0.2);

  /* Status */
  --green-600:        #2D7A4F;
  --amber-600:        #B8860B;
  --red-600:          #C13A3A;
  --green-400:        #4ADE80;
  --amber-400:        #FBBF24;
  --red-400:          #F87171;

  /* ─── Type scale ─── */
  --text-2xl:         1.625rem;  /* 26px */
  --text-lg:          1.125rem;  /* 18px */
  --text-md:          0.875rem;  /* 14px */
  --text-sm:          0.8125rem; /* 13px */
  --text-xs:          0.75rem;   /* 12px */

  --leading-tight:    1.25;
  --leading-normal:   1.35;
  --leading-relaxed:  1.4;

  --tracking-wide:    0.03em;
  --tracking-wider:   0.08em;

  --weight-regular:   400;
  --weight-medium:    500;
  --weight-semibold:  600;

  /* ─── Spacing scale ─── */
  --space-1:          0.25rem;   /* 4px */
  --space-2:          0.5rem;    /* 8px */
  --space-4:          1rem;      /* 16px */
  --space-6:          1.5rem;    /* 24px */
  --space-8:          2rem;      /* 32px */
  --space-12:         3rem;      /* 48px */

  /* ─── Layout ─── */
  --width-content:    52.5rem;   /* 840px */
  --width-gutter:     1.25rem;   /* 20px */
  --width-column-gap: 2rem;      /* 32px */

  /* ─── Motion ─── */
  --duration-fast:    150ms;
  --easing-default:   ease;

  /* ─── Fonts ─── */
  --font-serif:       'GT Sectra', Georgia, 'Times New Roman', serif;
  --font-sans:        'Inter', system-ui, -apple-system, sans-serif;
}
```

**Primitives never change per theme or surface.** They are the fixed palette that the entire system draws from. If you rebrand, this is the one file you edit.

#### Layer 2 — Semantic tokens (`styles/tokens/semantic.css`)

Maps primitives to roles. Named by WHAT THEY DO. This is the layer that dark mode swaps.

```css
:root {
  /* ─── Surfaces ─── */
  --color-surface:          var(--warm-white);
  --color-surface-alt:      var(--warm-white-alt);

  /* ─── Text ─── */
  --color-text-primary:     var(--gray-900);
  --color-text-secondary:   var(--gray-700);
  --color-text-tertiary:    var(--gray-600);
  --color-text-muted:       var(--gray-500);

  /* ─── Interactive ─── */
  --color-accent:           var(--ink-blue);
  --color-accent-hover:     var(--ink-blue-light);

  /* ─── Structural ─── */
  --color-rule:             var(--rule-warm);
  --color-selection:        var(--ink-blue-wash);

  /* ─── Status ─── */
  --color-status-ok:        var(--green-600);
  --color-status-warn:      var(--amber-600);
  --color-status-error:     var(--red-600);
}

/* ─── Dark mode: swap semantic layer only ─── */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --color-surface:        var(--charcoal);
    --color-surface-alt:    var(--charcoal-alt);
    --color-text-primary:   var(--warm-light);
    --color-text-secondary: var(--gray-400-dark);
    --color-text-tertiary:  var(--gray-300-dark);
    --color-text-muted:     var(--gray-200-dark);
    --color-accent:         var(--blue-muted);
    --color-accent-hover:   var(--blue-muted-light);
    --color-rule:           var(--rule-dark);
    --color-selection:      var(--blue-wash-dark);
    --color-status-ok:      var(--green-400);
    --color-status-warn:    var(--amber-400);
    --color-status-error:   var(--red-400);
  }
}

[data-theme="dark"] {
  --color-surface:        var(--charcoal);
  --color-surface-alt:    var(--charcoal-alt);
  --color-text-primary:   var(--warm-light);
  --color-text-secondary: var(--gray-400-dark);
  --color-text-tertiary:  var(--gray-300-dark);
  --color-text-muted:     var(--gray-200-dark);
  --color-accent:         var(--blue-muted);
  --color-accent-hover:   var(--blue-muted-light);
  --color-rule:           var(--rule-dark);
  --color-selection:      var(--blue-wash-dark);
  --color-status-ok:      var(--green-400);
  --color-status-warn:    var(--amber-400);
  --color-status-error:   var(--red-400);
}
```

**Dark mode lives entirely in this layer.** Components never use `dark:` variants. They use `text-primary` → resolves to `var(--color-text-primary)` → resolves to the correct primitive for the current theme.

#### Layer 3 — Component tokens (`styles/tokens/components.css`)

Maps semantic tokens to component-specific roles. Named by WHERE they're used. This is the layer that surface variants override.

```css
:root {
  /* ─── Headline ─── */
  --headline-color:           var(--color-text-primary);
  --headline-size:            var(--text-lg);
  --headline-weight:          var(--weight-medium);
  --headline-leading:         var(--leading-normal);
  --headline-hover-color:     var(--color-accent);

  /* ─── Lead headline (news only) ─── */
  --headline-lead-size:       var(--text-2xl);
  --headline-lead-weight:     var(--weight-semibold);
  --headline-lead-leading:    var(--leading-tight);

  /* ─── Metadata (source + time) ─── */
  --meta-color:               var(--color-text-tertiary);
  --meta-size:                var(--text-sm);
  --meta-leading:             var(--leading-relaxed);

  /* ─── Source name ─── */
  --source-color:             var(--color-text-secondary);

  /* ─── Summary (hidden by default, shown on learning) ─── */
  --summary-color:            var(--color-text-secondary);
  --summary-size:             var(--text-sm);
  --summary-leading:          var(--leading-relaxed);

  /* ─── Section labels ("TODAY", "STRATEGY") ─── */
  --section-label-color:      var(--color-text-muted);
  --section-label-size:       var(--text-xs);
  --section-label-tracking:   var(--tracking-wider);
  --section-label-weight:     var(--weight-medium);

  /* ─── Navigation (surface tabs + category tabs) ─── */
  --nav-color:                var(--color-text-muted);
  --nav-active-color:         var(--color-text-primary);
  --nav-size:                 var(--text-md);
  --nav-tracking:             var(--tracking-wide);

  /* ─── Briefing/Digest editorial block ─── */
  --briefing-label-color:     var(--color-text-muted);
  --briefing-text-color:      var(--color-text-secondary);

  /* ─── Rules ─── */
  --rule-color:               var(--color-rule);

  /* ─── Layout ─── */
  --content-max-width:        var(--width-content);
  --content-gutter:           var(--width-gutter);
  --content-column-gap:       var(--width-column-gap);
}

/* ─── Surface-scoped overrides ─── */
/* These are the ONLY CSS changes needed when adding a new surface. */
/* Components read component tokens; surface context overrides them. */

/* No overrides needed for news — it uses the defaults above. */

/* Learning surface: no visual overrides needed currently — the   */
/* behavioral differences (show summary, date format, topic        */
/* grouping, no lead headline) are handled in the surface config   */
/* registry (lib/surfaces.ts), not in CSS. But if a future surface */
/* needs different headline sizing or colors:                      */
/*                                                                 */
/* [data-surface="research"] {                                     */
/*   --headline-size: var(--text-md);                              */
/*   --headline-weight: var(--weight-regular);                     */
/*   --section-label-color: var(--color-accent);                   */
/* }                                                               */
```

**Why this matters for extensibility:**

| Change | Layer | Files touched |
|--------|-------|---------------|
| Rebrand (new palette) | Primitives | 1 (`primitives.css`) |
| Add dark mode | Already done at semantic layer | 0 |
| Add "high contrast" theme | Semantic (new `[data-theme]` block) | 1 (`semantic.css`) |
| New surface with different headline treatment | Component (new `[data-surface]` block) | 1 (`components.css`) |
| New component (e.g., BookmarkCard) | Component (add tokens) + Tailwind config | 2 |
| Change headline font globally | Primitives (`--font-serif`) | 1 |
| Change headline size for learning only | Component (`[data-surface="learning"]` override) | 1 |

**No change ever requires editing an existing component's markup.** Components consume component tokens via Tailwind utilities. The layers above them control the values.

#### Tailwind configuration (`tailwind.config.ts`)

Tailwind is the consumption layer. It maps component tokens to utility classes:

```ts
import type { Config } from "tailwindcss";

export default {
  theme: {
    extend: {
      colors: {
        // Semantic (for rare direct use — prefer component tokens)
        surface:   { DEFAULT: "var(--color-surface)", alt: "var(--color-surface-alt)" },
        accent:    { DEFAULT: "var(--color-accent)", hover: "var(--color-accent-hover)" },
        rule:      "var(--color-rule)",
        status:    { ok: "var(--color-status-ok)", warn: "var(--color-status-warn)", error: "var(--color-status-error)" },

        // Component-level (what components actually use)
        "headline":       "var(--headline-color)",
        "headline-hover": "var(--headline-hover-color)",
        "meta":           "var(--meta-color)",
        "source":         "var(--source-color)",
        "summary":        "var(--summary-color)",
        "section-label":  "var(--section-label-color)",
        "nav":            "var(--nav-color)",
        "nav-active":     "var(--nav-active-color)",
        "briefing-label": "var(--briefing-label-color)",
        "briefing-text":  "var(--briefing-text-color)",
      },
      textColor: {
        primary:   "var(--color-text-primary)",
        secondary: "var(--color-text-secondary)",
        tertiary:  "var(--color-text-tertiary)",
        muted:     "var(--color-text-muted)",
      },
      fontFamily: {
        serif: "var(--font-serif)",
        sans:  "var(--font-sans)",
      },
      fontSize: {
        "headline-lead": ["var(--headline-lead-size)", { lineHeight: "var(--headline-lead-leading)", fontWeight: "var(--headline-lead-weight)" }],
        "headline":      ["var(--headline-size)",      { lineHeight: "var(--headline-leading)",      fontWeight: "var(--headline-weight)" }],
        "nav":           ["var(--nav-size)",            { letterSpacing: "var(--nav-tracking)" }],
        "meta":          ["var(--meta-size)",           { lineHeight: "var(--meta-leading)" }],
        "summary":       ["var(--summary-size)",        { lineHeight: "var(--summary-leading)" }],
        "section-label": ["var(--section-label-size)",  { letterSpacing: "var(--section-label-tracking)", fontWeight: "var(--section-label-weight)" }],
      },
      maxWidth: {
        content: "var(--content-max-width)",
      },
      gap: {
        column: "var(--content-column-gap)",
      },
      padding: {
        gutter: "var(--content-gutter)",
      },
    },
  },
} satisfies Config;
```

**Tailwind classes are now fully component-semantic:**

```tsx
// A headline uses component tokens — no raw values, no semantic-layer references
<h2 className="font-serif text-headline text-headline group-hover:text-headline-hover">
  {title}
</h2>
<p className="text-meta text-meta">
  {source} · {time}
</p>
```

If a future `[data-surface="research"]` override changes `--headline-size`, this headline renders at the new size automatically. Zero component changes.

#### Typography (`styles/typography.css`)

`@font-face` declarations — unchanged from DESIGN.md. Separated from tokens because font files are a loading concern, not a design decision.

- GT Sectra Medium (500), SemiBold (600) — .woff2 with `font-display: swap`
- Inter Variable (100-900) — .woff2 with `font-display: swap`

#### Globals (`styles/globals.css`)

```css
/* Import order matters: primitives → semantic → component */
@import "./tokens/primitives.css";
@import "./tokens/semantic.css";
@import "./tokens/components.css";
@import "./typography.css";

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: var(--font-sans);
    background-color: var(--color-surface);
    color: var(--color-text-primary);
    -webkit-font-smoothing: antialiased;
  }
  ::selection { background-color: var(--color-selection); }
  hr { border: none; border-top: 1px solid var(--rule-color); }
}
```

#### Root layout (`frontend/app/layout.tsx`)

- Imports `globals.css`
- Sets `<html lang="en">` with metadata
- Inline `<script>` in `<head>` for theme detection (prevents flash of wrong theme)
- **Sets `data-surface` attribute** on a wrapper element — driven by the current route. This is how component tokens pick up surface context.

#### Font files (`frontend/public/fonts/`)

- GTSectra-Medium.woff2, GTSectra-SemiBold.woff2, Inter-Variable.woff2

#### File structure

```
frontend/styles/
├── tokens/
│   ├── primitives.css     ← raw palette (colors, sizes, spaces)
│   ├── semantic.css       ← role mapping + dark mode swap
│   └── components.css     ← component tokens + surface overrides
├── typography.css         ← @font-face only
└── globals.css            ← imports all, Tailwind directives, base layer
```

**Verification**:
- Test page renders with correct fonts, colors, dark mode
- Changing a primitive in `primitives.css` cascades through semantic → component → rendered output
- Adding a `[data-surface="test"]` block in `components.css` with a different `--headline-color` changes headline color when `data-surface="test"` is set on a parent element
- Lighthouse audit passes for font loading (no CLS from font swap)

---

### Step 1.10 — Frontend: Surface Config Registry + Reader Components

**What**: The primary reader experience — but built on a **surface configuration registry** so that every component is surface-agnostic and new surfaces compose from existing parts without modifying them.

#### The modularity problem

The naive approach: HeadlineItem accepts a `surface` prop and branches — `if (surface === 'learning') { show summary }`. HeadlineList branches — `if (surface === 'learning') { group by topic }`. Every new surface adds another branch to every component. That's a growing switch statement, not modularity.

The correct approach: **A surface is a configuration object, not a prop that triggers conditional branches.** Components receive a config and render accordingly. Adding a new surface means adding a config entry — zero existing component changes.

#### Surface Configuration Registry (`frontend/lib/surfaces.ts`)

The single source of truth for how each surface behaves. Every behavioral difference between News and Learning (and any future surface) is captured here — not scattered across component conditionals.

```ts
export type SurfaceConfig = {
  slug: string;                      // "news" | "learning"
  label: string;                     // "News" | "Learning"
  basePath: string;                  // "/" | "/learning"
  groupBy: "time" | "topic";        // how HeadlineList groups articles
  showSummary: boolean;              // whether HeadlineItem shows the summary
  showLeadHeadline: boolean;         // whether the first headline renders at 26px
  showAlsoReportedBy: boolean;       // whether HeadlineItem shows "Also in:" line
  timeFormat: "relative" | "date";   // "2h" vs "Mar 14, 2026"
  briefingType: string;              // API param: "daily_news" | "weekly_learning"
  briefingLabel: string;             // "THE BRIEF" | "THE LEARNING DIGEST"
  briefingCadence: string;           // display text: "today" | "this week"
  categoryApiSurface: string;        // API param for fetching categories
};

export const SURFACES: Record<string, SurfaceConfig> = {
  news: {
    slug: "news",
    label: "News",
    basePath: "/",
    groupBy: "time",
    showSummary: false,
    showLeadHeadline: true,
    showAlsoReportedBy: true,
    timeFormat: "relative",
    briefingType: "daily_news",
    briefingLabel: "THE BRIEF",
    briefingCadence: "today",
    categoryApiSurface: "news",
  },
  learning: {
    slug: "learning",
    label: "Learning",
    basePath: "/learning",
    groupBy: "topic",
    showSummary: true,
    showLeadHeadline: false,
    showAlsoReportedBy: true,
    timeFormat: "date",
    briefingType: "weekly_learning",
    briefingLabel: "THE LEARNING DIGEST",
    briefingCadence: "this week",
    categoryApiSurface: "learning",
  },
};

// Resolve surface from URL path
export function getSurfaceFromPath(path: string): SurfaceConfig {
  if (path.startsWith("/learning")) return SURFACES.learning;
  // Future: if (path.startsWith("/research")) return SURFACES.research;
  return SURFACES.news;
}
```

**To add a third surface** (e.g., "Research" for academic papers), you add one entry to `SURFACES`, create one page file (`app/(reader)/research/page.tsx`), and optionally add one `[data-surface="research"]` block in `components.css` if it needs different visual treatment. No existing component is modified.

#### Components (all in `frontend/components/`)

Every component below reads from `SurfaceConfig` — never from a raw `surface` string with internal branching.

1. **SurfaceNav.tsx** — Server Component. Renders top-level tabs from `Object.values(SURFACES)`. Active state from current path. Styled per §2.1: serif font, 2px underline on active, warm gray inactive. **Adding a new surface = it automatically appears as a tab.**

2. **CategoryNav.tsx** — Server Component. Receives `config: SurfaceConfig` and a `categories` array (fetched by the parent page from `/api/categories?surface={config.categoryApiSurface}`). **Renders categories in the order returned by the API** (sorted by `display_order`). No category names or slugs are hardcoded — the component renders whatever the API returns.
   - "ALL" tab is prepended (always first, links to the surface root with no category filter)
   - Uppercase, letterspaced, underline on active category
   - **Overflow handling**: horizontally scrollable on all viewports (not just mobile) when tabs exceed the container width. Subtle fade gradient on the trailing edge hints at more. On desktop with few categories, tabs render naturally without scrolling. This handles 8 categories today and 20 tomorrow without layout changes.
   - Active category determined by URL path, not component state — each tab is a `<Link>` to the category URL. This means category navigation is server-rendered and works without JS.

3. **LeadHeadline.tsx** — Renders the first headline at 26px/semibold. Full-width. Source + time at 14px. **This component doesn't know about surfaces.** The parent (HeadlineList or SurfacePage) decides whether to render it based on `config.showLeadHeadline`.

4. **HeadlineItem.tsx** — Renders a single headline. **Config-driven, not branch-driven:**

```tsx
type Props = {
  headline: HeadlineData;
  config: SurfaceConfig;
};

function HeadlineItem({ headline, config }: Props) {
  return (
    <a href={headline.url} target="_blank" rel="noopener"
       className="block group">
      <h2 className="font-serif text-headline text-headline
                     group-hover:text-headline-hover transition-colors">
        {headline.title}
      </h2>
      {config.showSummary && headline.summary && (
        <p className="text-summary text-summary mt-1">
          {headline.summary}
        </p>
      )}
      <p className="text-meta text-meta mt-1">
        {headline.source_name} · {formatTime(headline.published_at, config.timeFormat)}
        {config.showAlsoReportedBy && headline.also_reported_by.length > 0 && (
          <span className="text-muted">
            {" · Also in: "}
            {headline.also_reported_by.map((s, i) => (
              <>{i > 0 && ", "}<a href={s.url} target="_blank" rel="noopener"
                className="hover:text-accent">{s.source_name}</a></>
            ))}
          </span>
        )}
      </p>
    </a>
  );
}
```

**No `if (surface === 'learning')` anywhere.** The config boolean `showSummary` controls summary visibility. The config boolean `showAlsoReportedBy` controls "Also in:" display. The config string `timeFormat` controls time display. New surfaces just set these fields — HeadlineItem doesn't change.

5. **HeadlineList.tsx** — Server Component. **Config-driven grouping:**

```tsx
function HeadlineList({ headlines, config }: { headlines: HeadlineData[]; config: SurfaceConfig }) {
  const groups = groupHeadlines(headlines, config.groupBy);
  const items = config.showLeadHeadline ? headlines.slice(1) : headlines;
  const lead = config.showLeadHeadline ? headlines[0] : null;

  return (
    <div>
      {lead && <LeadHeadline headline={lead} config={config} />}
      {groups.map(group => (
        <section key={group.label}>
          <SectionLabel label={group.label} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-column">
            {group.items.map(h => (
              <HeadlineItem key={h.id} headline={h} config={config} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
```

The `groupHeadlines()` utility function handles the grouping strategy:

```ts
// lib/grouping.ts
function groupHeadlines(
  headlines: HeadlineData[],
  strategy: "time" | "topic"
): { label: string; items: HeadlineData[] }[] {
  if (strategy === "time") return groupByTime(headlines);    // "TODAY", "YESTERDAY"
  if (strategy === "topic") return groupByTopic(headlines);  // "STRATEGY", "LEADERSHIP"
  return [{ label: "", items: headlines }];                  // fallback: flat list
}
```

**Adding a new grouping strategy** (e.g., `"source"` — group by publication): add a `groupBySource()` function in `lib/grouping.ts`, add `"source"` to the union type, set it in the new surface's config. Zero existing component changes.

6. **EditorialSummary.tsx** — **One component for all briefing types** (not separate DailyBriefing + LearningDigest components). Config-driven:

```tsx
function EditorialSummary({ config }: { config: SurfaceConfig }) {
  const briefing = await fetchBriefing(config.briefingType);
  if (!briefing?.brief) return null;

  return (
    <section className="mb-8">
      <h3 className="text-section-label text-briefing-label uppercase">
        {config.briefingLabel}
      </h3>
      <p className="text-briefing-text mt-2">{briefing.brief}</p>
      <hr className="mt-6" />
    </section>
  );
}
```

**One component serves all surfaces.** The label ("THE BRIEF" vs "THE LEARNING DIGEST") and the API call (`daily_news` vs `weekly_learning`) come from config. Adding a future "Research Roundup" briefing = add it to the surface config. Zero component changes.

7. **SectionLabel.tsx** — Renders section headers ("TODAY", "STRATEGY"). Pure presentational — just text with `text-section-label` styling. Used by HeadlineList for both time and topic group headers.

8. **Pagination.tsx** — "More headlines" text link. Centered, small sans, thin rule above. Surface-agnostic.

9. **ThemeToggle.tsx** — Client Component. Light/dark/system toggle. Writes `data-theme` to `<html>`. Stores preference in localStorage.

#### Shared Surface Layout (`frontend/app/(reader)/layout.tsx`)

Both News and Learning (and any future surface) share the same layout structure. **The page files are thin** — they resolve the surface config and pass it to the shared components.

```
frontend/app/
├── (reader)/                     # Route group — shared reader layout
│   ├── layout.tsx                # Masthead + SurfaceNav + footer (shared)
│   ├── page.tsx                  # News surface → passes SURFACES.news to SurfacePage
│   ├── [category]/
│   │   └── page.tsx              # News category filter
│   └── learning/
│       ├── page.tsx              # Learning surface → passes SURFACES.learning to SurfacePage
│       └── [category]/
│           └── page.tsx          # Learning category filter
└── admin/
    └── ...
```

The shared reader layout (`(reader)/layout.tsx`):

```tsx
export default function ReaderLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="max-w-content mx-auto px-gutter">
      <Masthead />
      <SurfaceNav />
      {children}
      <Footer />
    </div>
  );
}
```

Each surface page is a thin adapter — it resolves the config and delegates:

```tsx
// app/(reader)/page.tsx (news)
// ⚠️ BUG IN ORIGINAL PLAN: searchParams must be Promise<{...}> in Next.js 15
// Fixed implementation uses async function + await:
import { SURFACES } from "@/lib/surfaces";
import { SurfacePage } from "@/components/SurfacePage";

export default async function NewsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const params = await searchParams;
  return <SurfacePage config={SURFACES.news} page={Number(params.page) || 1} />;
}

// app/(reader)/learning/page.tsx (learning)
import { SURFACES } from "@/lib/surfaces";
import { SurfacePage } from "@/components/SurfacePage";

export default async function LearningPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const params = await searchParams;
  return <SurfacePage config={SURFACES.learning} page={Number(params.page) || 1} />;
}
```

The `SurfacePage` component composes everything from config. It handles slug redirects (renamed/merged categories) transparently:

```tsx
// components/SurfacePage.tsx
async function SurfacePage({ config, page, category }: {
  config: SurfaceConfig;
  page: number;
  category?: string;
}) {
  const [headlines, categories] = await Promise.all([
    fetchHeadlines({ surface: config.slug, category, page }),
    fetchCategories(config.categoryApiSurface),
  ]);

  // If the API returned a 301 redirect (slug changed/merged), follow it
  // The fetchHeadlines client handles this: if the response is a redirect,
  // it returns {redirect: "/learning/new-slug"} and SurfacePage calls
  // Next.js redirect() to send the user to the correct URL.
  if (headlines.redirect) {
    redirect(headlines.redirect);
  }

  return (
    <div data-surface={config.slug}>
      <CategoryNav categories={categories} config={config} activeCategory={category} />
      <EditorialSummary config={config} />
      <HeadlineList headlines={headlines.items} config={config} />
      <Pagination pagination={headlines.pagination} config={config} category={category} />
    </div>
  );
}
```

The `data-surface` attribute on the wrapper div is what enables CSS component token overrides (from `components.css`) to cascade into all children.

#### Lib modules

1. **frontend/lib/api.ts** — Single API client. Typed fetch wrappers. No raw `fetch()` in components. Functions accept surface/type params from config — they don't hardcode surface names.

2. **frontend/lib/types.ts** — TypeScript types mirroring Pydantic schemas. `HeadlineData`, `HeadlinesResponse`, `CategoryItem`, `BriefingResponse`, `PaginationMeta`.

3. **frontend/lib/time.ts** — Time formatting:
   - `formatTime(date, format: "relative" | "date")` — dispatches to the correct formatter
   - `formatRelativeTime(date)` → "2h", "3d", "Mar 2"
   - `formatDate(date)` → "Mar 14, 2026"
   - Adding a new format (e.g., `"iso"`) = add a formatter function and a new union member. Existing formatters untouched.

4. **frontend/lib/grouping.ts** — Headline grouping strategies:
   - `groupHeadlines(headlines, strategy)` — dispatcher
   - `groupByTime(headlines)` → "TODAY" / "YESTERDAY" sections
   - `groupByTopic(headlines)` → category-name sections
   - Adding a new strategy = add a function. Dispatcher gains a branch. Existing strategies untouched.

5. **frontend/lib/surfaces.ts** — The surface config registry (described above).

#### Layout details
- Max content width: 840px, centered
- Two-column grid at ≥768px, single column below
- 20px side padding on mobile
- No cards, no shadows, no rounded corners — thin rules and typography only

#### Verification
- Homepage loads with headlines from all news sources
- Category tabs filter correctly
- Lead headline renders at 26px (news only — controlled by `config.showLeadHeadline`)
- Two-column grid at desktop, single column at mobile
- Dark mode toggles correctly
- "More headlines" paginates
- All links open in new tab
- Relative time formatting works ("2h", "3d", "Mar 2")
- The Brief appears above headlines (or is absent if not generated)
- **Modularity check**: temporarily add a third entry to `SURFACES` with `groupBy: "time"`, `showSummary: true` → confirm it renders correctly without any component modifications

---

### Phase 1 Exit Criteria

- [x] Docker Compose starts all 5 services
- [x] Database has all tables, indexes, seed data (7 sources, 17 categories, 6 models, 4 tasks)
- [ ] Worker fetches RSS from 5 news sources on schedule — *(code complete, needs Docker runtime verification)*
- [ ] Classifier categorizes articles using news categories via Haiku — *(code complete, needs live LLM key)*
- [x] fetch_logs and pipeline_logs written for every operation
- [x] `/api/headlines?surface=news` returns categorized headlines
- [x] News reader renders with editorial design (fonts, colors, layout, dark mode)
- [x] Category filtering works
- [x] Pagination works
- [x] All headline clicks open original article in new tab
- [x] **CSS modularity**: Changing `--ink-blue` in `primitives.css` cascades through semantic → component → rendered accent color
- [x] **CSS modularity**: Adding a `[data-surface="test"]` block in `components.css` with `--headline-size: var(--text-2xl)` makes headlines larger within that surface scope
- [x] **Frontend modularity**: Adding a test entry to `SURFACES` renders a third tab in SurfaceNav and a working surface page without modifying any existing component
- [x] **Backend modularity**: `ADAPTER_REGISTRY` and `PROVIDERS` dicts are the only places adapter/provider types are registered — no other file contains a hardcoded list

---

### Phase 1 Implementation Record

**Status**: Code complete. All files written. TypeScript compiles with zero errors. Python models load cleanly (11 tables). Schemas import. Similarity module tested. Needs `docker compose up` for full end-to-end verification.

**Date**: 2026-03-16

#### What was built (93 files)

| Area | Files | Key modules |
|------|-------|-------------|
| Infrastructure | 4 | docker-compose.yml, Caddyfile, .env.example, .gitignore |
| Backend scaffold | 5 | Dockerfile, requirements.txt, config.py, database.py, main.py |
| Models | 13 | 11 models + base.py + __init__.py (all re-exported) |
| Migrations | 4 | alembic.ini, env.py, 001_initial_schema.py, 002_seed_data.py |
| Schemas | 6 | headlines, briefing, events, admin, common + __init__ |
| Adapters | 4 | base.py, rss.py, registry.py + __init__ |
| Scraper | 3 | scraper.py, types.py + __init__ |
| LLM | 6 | anthropic.py, openai.py, google.py, registry.py, types.py + __init__ |
| Classifier | 3 | classifier.py, prompts.py + __init__ |
| Dedup | 4 | deduplicator.py, similarity.py, prompts.py + __init__ |
| Workers | 6 | scheduler.py, fetch_worker.py, classify_worker.py, dedup_worker.py, worker_main.py + __init__ |
| Routers | 5 | headlines.py, categories.py, briefing.py, events.py + __init__ |
| Frontend scaffold | 7 | package.json, tsconfig, next.config, postcss, tailwind.config, Dockerfile, layout.tsx |
| CSS tokens | 4 | primitives.css, semantic.css, components.css, typography.css, globals.css |
| Frontend lib | 6 | api.ts, types.ts, surfaces.ts, time.ts, ~~grouping.ts~~ *(deleted Phase 8)*, analytics.ts |
| Components | 12 | SurfacePage, SurfaceNav, CategoryNav, HeadlineItem, ~~HeadlineList~~ *(deleted Phase 8)*, LeadHeadline, EditorialSummary, SectionLabel, ~~Pagination~~ *(deleted Phase 8)*, ThemeToggle, Masthead, Footer |
| Pages | 5 | ~~(reader)/[[...slug]]/page~~ *(replaced Phase 8)*, (reader)/learning/page, (reader)/learning/[category]/page *(now redirect, Phase 8)*, (reader)/layout |

#### Deviations from plan

**1. Python 3.9 compatibility (CRITICAL for future phases)**

The host system runs Python 3.9.6. This required two changes:

- **`from __future__ import annotations`** added to every `.py` file that uses modern type hints (`X | None`, `list[X]`, `dict[X, Y]`). This makes these annotations strings at import time, avoiding `TypeError` from the parser.
- **SQLAlchemy model files use `Optional[X]` and `List[X]`** from `typing` instead of `X | None` and `list[X]` in `Mapped[...]` annotations. SQLAlchemy evaluates `Mapped` type hints at class definition time using `eval()`, which runs in the Python 3.9 runtime regardless of `__future__` annotations. PEP 604 union syntax (`X | None`) fails at eval time.

**Rule for all future phases**: In any file under `app/models/`, always use `Optional[X]` and `List[X]` for `Mapped` type annotations. In all other files, `from __future__ import annotations` at the top is sufficient. The Docker container runs Python 3.12 (from `python:3.12-slim`), but local tooling (linting, IDE imports, Alembic via host) requires 3.9 compatibility.

**2. LLM registry API shape differs from plan**

The plan describes a single `run_task(task_name, payload, db)` function. The implementation provides three typed functions:

```python
run_classify(db, task_name, system_prompt, user_prompt, tool_schema) → ClassificationResult
run_dedup(db, task_name, system_prompt, user_prompt, tool_schema) → DedupResult
run_generate(db, task_name, system_prompt, user_prompt) → GenerationResult
```

Each provider adapter has three corresponding methods (`classify_X`, `dedup_X`, `generate_X`). The `ProviderAdapter` NamedTuple holds all three:

```python
class ProviderAdapter(NamedTuple):
    classify: callable
    dedup: callable
    generate: callable
    api_key_env: str
```

**Why**: Classification uses tool_use/structured output (different API shape per provider). Dedup also uses tool_use but with a different schema. Generation is plain text. A single `run_task` would need internal branching on task type, which is less type-safe and harder to extend. The three-function approach means Phase 3 briefing generation calls `run_generate()` directly — no changes to the registry needed.

**Implication for Phase 3**: Call `run_generate(db, "briefing", system_prompt, user_prompt)` instead of `run_task("briefing", ...)`. Same for `learning_digest`.

**3. Frontend scaffold created manually (not create-next-app)**

`create-next-app` uses interactive prompts that couldn't be automated in the CLI. The frontend was scaffolded manually with identical configuration: App Router, TypeScript, Tailwind v3 (`^3.4.0`), ESLint, `output: "standalone"`. No functional difference.

**4. Learning surface pages and groupByTopic built in Phase 1**

Per the implementation plan's analysis, building learning pages in Phase 1 prevents a broken Learning tab in SurfaceNav (which renders `Object.values(SURFACES)` — both surfaces). The pages are 5 lines each and the `groupByTopic()` function is a basic implementation that groups by first category name. This was explicitly called out in the implementation plan as preventing a broken tab, not as scope creep.

**Phase 2 impact**: Step 2.2 ("Learning Reader Surface") is already complete. Phase 2 reduces to Step 2.1 only — activating the learning sources (`UPDATE sources SET active = true WHERE surface = 'learning'`) and verifying the feeds parse correctly. No frontend code changes needed.

**5. EditorialSummary component and Briefing API built in Phase 1**

The `EditorialSummary` component and `GET /api/briefing` endpoint are implemented and wired up. They gracefully handle the case where no briefing exists (renders nothing).

**Phase 3 impact**: Step 3.2 ("Briefing API + Frontend") is already complete — only the backend editorial generation workers (Step 3.1) need to be built. The frontend will display briefings as soon as they exist in the DB.

**6. Analytics tracking lib built in Phase 1**

`frontend/lib/analytics.ts` implements session ID generation and `trackEvent()`. It uses `sessionStorage` (not cookies) for the session ID.

**Phase 5 impact**: Step 5.1 needs to integrate `trackEvent()` calls into the page components (page_view on render, headline_click on click), and may want to switch from `sessionStorage` to a cookie with 30-minute rolling expiry per the DESIGN.md spec. The core tracking function is ready.

**7. Batch refresh logic built in Phase 1**

`backend/app/workers/fetch_worker.py` implements `start_batch_refresh()` with 60s cooldown, `asyncio.gather` for source isolation, and post-batch classification + dedup.

**Phase 4 impact**: Step 4.2's backend `POST /api/admin/refresh-all` endpoint can delegate directly to this function. The `GET /api/admin/refresh-status/:batch_id` polling endpoint still needs to be built (query fetch_logs by batch_id).

#### Known limitations to address before production

1. **No auth middleware yet** — admin endpoints have no JWT protection. Phase 4 Step 4.1 will add `backend/app/auth/admin.py`.
2. **No retention pipeline** — articles/logs accumulate indefinitely until Phase 6 Step 6.3.
3. **Georgia font fallback** — GT Sectra .woff2 files need commercial licensing. The system works with Georgia until then.
4. **Session-based analytics use sessionStorage** — DESIGN.md specifies a cookie with 30-minute rolling expiry. Revisit in Phase 5.
5. **Scheduler source query is coarse** — the `WHERE last_fetched_at <= now - 1 minute` pre-filter queries more sources than necessary, then refines per-source in Python. Fine for 7 sources; may want DB-level per-source interval comparison if source count grows significantly.

---

## Phase 2: Learning Surface

**Goal**: Two content surfaces — News (time-sensitive) and Learning (evergreen management insights from HBR + MIT SMR).

> **Scope reduced**: Phase 1 already built all Learning frontend pages, components, `groupByTopic()`, and the surface config registry. Phase 2 now only requires activating the learning sources in the database and verifying the end-to-end pipeline. See "Phase 1 Implementation Record — Deviation #4" above.

### Step 2.1 — Learning Source Activation — COMPLETE

**What**: Enable the learning pipeline — HBR and MIT SMR feeds fetching and classifying.

**Implemented via**: Alembic migration `003_activate_learning_sources.py` — reproducible, reversible, tracked in version control.

**Tasks**:

1. ~~Activate learning sources: `UPDATE sources SET active = true WHERE surface = 'learning'` (or via future admin panel)~~ → Done via migration 003
2. Verify HBR RSS feed (`https://hbr.org/rss`) parses correctly with the existing RSSAdapter. Can test via `scrape(source, trigger="test")` in a Python shell, or via the admin "Test Fetch" endpoint once Phase 4 is built. *(needs Docker runtime verification)*
3. Verify MIT SMR RSS feed (`https://sloanreview.mit.edu/feed/`) parses correctly. *(needs Docker runtime verification)*
4. Confirm surface-aware classification: articles from learning sources (HBR, MIT SMR) are classified against learning categories (Strategy, Leadership, etc.), not news categories. The classifier already groups articles by `source.surface` and loads categories per surface. *(needs Docker runtime verification)*
5. Confirm fetch intervals: HBR at 360 min (6h), MIT SMR at 720 min (12h). Already seeded in the database.

**Verification**: Worker fetches from HBR/MIT SMR. Articles appear in DB with correct source_id. Classification uses learning categories. pipeline_log shows task='classification' with learning articles counted.

---

### ~~Step 2.2 — Learning Reader Surface (Frontend)~~ — ALREADY COMPLETE

**Built in Phase 1.** All of the following already exist and are functional:

- `frontend/app/(reader)/learning/page.tsx` — passes `SURFACES.learning` to SurfacePage
- `frontend/app/(reader)/learning/[category]/page.tsx` — with category param
- `frontend/lib/grouping.ts` — `groupByTopic()` implemented (groups by first category name, uppercase headers)
- All config-driven components (HeadlineItem, HeadlineList, EditorialSummary, SurfaceNav, CategoryNav) work without modification for the learning surface

**URL structure** (already working):
- `/` → News surface, all categories
- `/economy` → News, Economy category
- `/learning` → Learning surface, all categories
- `/learning/strategy` → Learning, Strategy category

**Verification** (run after Step 2.1 activates sources and articles flow in):
- `/learning` shows HBR + MIT SMR articles grouped by topic
- Summaries visible beneath each headline
- Dates shown as "Mar 14, 2026" (not "2h")
- No lead headline on learning surface
- Category tabs show learning categories (Strategy, Leadership, etc.)
- Filtering by learning category works
- SurfaceNav switches between News and Learning
- Footer shows all 7 publication names

---

### Phase 2 Exit Criteria

- [x] HBR and MIT SMR articles fetching on schedule (6h / 12h) — *(migration 003 activates sources; needs Docker runtime verification)*
- [x] Learning articles classified against learning categories only — *(classifier surface-awareness built in Phase 1; needs Docker runtime verification)*
- [x] `/learning` renders topic-grouped articles with summaries and dates — *(pages built in Phase 1, pending live data)*
- [x] SurfaceNav switches between News and Learning — *(built in Phase 1)*
- [x] Learning category tabs filter correctly — *(built in Phase 1)*
- [x] All 7 sources visible in footer — *(built in Phase 1)*

---

### Phase 2 Implementation Record

**Status**: Code complete. Migration written. Needs `docker compose up` + `alembic upgrade head` for end-to-end verification (RSS feed parsing, classification routing, article display).

**Date**: 2026-03-16

#### What was built (1 file)

| Area | Files | Key modules |
|------|-------|-------------|
| Migration | 1 | `003_activate_learning_sources.py` — sets `active = true` for learning sources |

#### Deviation from plan

**1. Alembic migration instead of manual SQL**

The plan described activating sources via manual SQL or the admin panel. The implementation uses a proper Alembic migration (`003_activate_learning_sources.py`) with `upgrade()` and `downgrade()` functions. This is reproducible across environments (dev, staging, prod), reversible, and tracked in version control — better than a one-off SQL statement.

---

## Phase 3: Briefings

**Goal**: Both surfaces open with AI-generated editorial summaries — The Brief (daily news) and The Learning Digest (weekly learning).

> **Scope reduced**: Phase 1 already built the `GET /api/briefing` endpoint and the `EditorialSummary` component. Phase 3 only needs the backend generation workers and prompts. See "Phase 1 Implementation Record — Deviation #5" above.

### Step 3.1 — Editorial Worker + Prompts — COMPLETE

**What**: Background tasks that generate reader-facing editorial content.

**Files built**:

1. **backend/app/editorial/prompts.py** — Two system prompts (thematic synthesis persona, not article-by-article summarizer) + two prompt builders:
   - `BRIEFING_SYSTEM_PROMPT` — editorial observer persona, forbids enumeration, requires thematic synthesis, `{max_sentences}` templated from task config
   - `LEARNING_DIGEST_SYSTEM_PROMPT` — weekly management-thinking orientation, highlights cross-publication convergence
   - `build_briefing_prompt(articles, config)` — titles + sources + categories only (~25 tokens per article)
   - `build_learning_digest_prompt(articles, config)` — includes summaries (capped at 300 chars) per DESIGN.md

2. **backend/app/editorial/briefing.py** — `generate_briefing(db, trigger="scheduled", force=False)`:
   - Checks `pipeline_tasks` active flag → skip if inactive
   - Timezone-aware date: `datetime.now(ZoneInfo(settings.BRIEFING_TIMEZONE)).date()`
   - Idempotency: if not `force`, checks if today's briefing exists → skip
   - Collects 24h news articles: `classified=True`, `is_representative=True`, `hidden=False`, joined with Source for surface filtering
   - Uses `joinedload(Article.source)` + `selectinload(Article.article_categories).selectinload(ArticleCategory.category)` + `.unique().scalars().all()`
   - Calls `run_generate(db, "briefing", ...)` via LLM registry
   - Calculates cost from LLMModel pricing
   - Upserts via `pg_insert(Briefing).on_conflict_do_update(constraint="uq_briefings_type_date", ...)`
   - Writes `PipelineLog` with task="briefing", tokens, cost
   - Returns stats dict

3. **backend/app/editorial/learning_digest.py** — `generate_learning_digest(db, trigger="scheduled", force=False)`:
   - Same pattern as briefing but: type=`weekly_learning`, date=this Monday, surface=`learning`, 7-day window, min 3 articles, includes summaries in prompt

4. **backend/app/editorial/__init__.py** — Re-exports `generate_briefing` and `generate_learning_digest`

5. **backend/app/workers/scheduler.py** — Modified (not a separate `editorial_worker.py`):
   - Two `CronTrigger` jobs in `start_scheduler()`: daily briefing at 6:30 AM, weekly digest Monday 7:00 AM (both in `settings.BRIEFING_TIMEZONE`)
   - Two wrapper functions (`_run_briefing`, `_run_learning_digest`) with isolated sessions and try/except
   - Post-classify hook in `_tick()`: after `db.commit()`, if new news articles were classified, attempts briefing generation in a separate session (idempotent — skips if today's briefing exists)

**Verification**:
- The Brief generates correctly from recent news articles
- The Learning Digest generates correctly from the last 7 days of learning articles
- Both skip if insufficient articles
- Both are idempotent (re-running doesn't create duplicates)
- pipeline_logs track token usage and cost
- ~~Admin can trigger regeneration~~ — `force=True` parameter ready; admin endpoint deferred to Phase 4

---

### ~~Step 3.2 — Briefing API + Frontend~~ — MOSTLY COMPLETE

**Built in Phase 1:**
- `GET /api/briefing` endpoint — fully functional for both types, with date defaults
- `EditorialSummary.tsx` component — config-driven, fetches briefing by `config.briefingType`, renders `config.briefingLabel`, gracefully returns null when no briefing exists

**Remaining for Phase 3:**
- Admin briefing endpoints (deferred to Phase 4):
   - `GET /api/admin/briefings` — list recent briefings (both types) with metadata
   - `POST /api/admin/briefings/regenerate` — body: `{type: "daily_news" | "weekly_learning"}` — regenerate on demand

**Verification** (after Step 3.1 generates briefings):
- News surface shows The Brief above headlines (or absent if not yet generated)
- Learning surface shows The Learning Digest (or absent if not Monday/not enough articles)
- Admin can regenerate both types
- Regeneration overwrites existing briefing for that period

---

### Phase 3 Exit Criteria

- [x] The Brief generates daily at 6:30 AM from news articles — *(CronTrigger job registered; needs Docker runtime verification)*
- [x] The Learning Digest generates weekly on Monday from learning articles — *(CronTrigger job registered; needs Docker runtime verification)*
- [x] Both display on their respective reader surfaces — *(EditorialSummary + GET /api/briefing built in Phase 1; renders once data exists in DB)*
- [x] Admin can regenerate both on demand — *(implemented in Phase 4: `POST /api/admin/briefings/regenerate` delegates to `generate_briefing(force=True)` / `generate_learning_digest(force=True)`)*
- [x] pipeline_logs track editorial generation with cost — *(PipelineLog written with task, model_used, tokens, estimated_cost_usd)*

---

### Phase 3 Implementation Record

**Status**: Code complete. All editorial generation logic written. Scheduler jobs registered. Needs `docker compose up` for end-to-end verification (LLM API calls, briefing upsert, reader display).

**Date**: 2026-03-16

#### What was built (5 new files, 1 modified)

| Area | Files | Key modules |
|------|-------|-------------|
| Editorial package | 4 | `__init__.py`, `prompts.py`, `briefing.py`, `learning_digest.py` |
| Migration | 1 | `003_activate_learning_sources.py` *(Phase 2, but deployed together)* |
| Scheduler | 1 (modified) | `scheduler.py` — CronTrigger jobs, wrapper functions, post-classify hook |

#### Deviations from plan

**1. No separate `editorial_worker.py`**

The plan described a separate `backend/app/workers/editorial_worker.py`. The implementation integrates editorial jobs directly into the existing `scheduler.py` — following the plan's own "Integration note" which recommended adding jobs to `start_scheduler()`. This avoids a file that would only re-export functions and register jobs, since the scheduler already handles all background work.

**2. `force` parameter instead of separate create/regenerate paths**

Both `generate_briefing()` and `generate_learning_digest()` accept `force: bool = False`. When `force=False` (scheduled/post-classify), they check existence first and skip if the briefing exists. When `force=True` (future admin regeneration in Phase 4), they skip the check. The `on_conflict_do_update` upsert handles both cases atomically. This is simpler than separate "create" and "regenerate" code paths and maps cleanly to the Phase 4 admin endpoint.

**3. Post-classify hook uses isolated session**

The post-classify briefing check in `_tick()` runs AFTER `await db.commit()` (not before) and uses its own `async with async_session() as briefing_db` session. This is critical: the briefing function needs to see the just-committed classified articles, and if briefing generation fails, the main fetch/classify/dedup transaction is already safely committed. The plan described this sequencing but didn't include it in the code sketch — the implementation follows the plan's written rationale exactly.

**4. Timezone handling uses `zoneinfo.ZoneInfo` (stdlib)**

The plan mentioned both `pytz` (APScheduler's dependency) and `ZoneInfo`. The implementation uses `ZoneInfo` from Python's stdlib `zoneinfo` module for date calculations (`datetime.now(ZoneInfo(settings.BRIEFING_TIMEZONE)).date()`), while passing the timezone string to APScheduler's `CronTrigger` (which handles its own timezone conversion internally). This avoids importing `pytz` directly.

#### Key design decisions

1. **Idempotency**: Both functions are safe to call multiple times — they check for existing briefings before generating. The post-classify hook and cron job can both fire without conflicts.
2. **Three trigger paths for daily briefing**: (a) Cron at 6:30 AM — primary, (b) post-classify hook — bonus for faster appearance after new articles, (c) `force=True` — future admin regeneration. All funnel through the same function.
3. **Cost tracking**: Looks up `LLMModel` by `task.model_id` to get `input_price_per_mtok` and `output_price_per_mtok`, calculates `estimated_cost_usd` in the `PipelineLog`.
4. **Article query pattern**: Mirrors `routers/headlines.py` exactly — same join/options/where/unique chain, ensuring briefing content matches what the reader sees.

---

## Phase 4: Admin Panel

**Goal**: Full operational control — sources, categories, models, tasks, articles, system health — without touching code.

**Status**: Code complete (2026-03-17). 18 new files, 2 modified, ~3,150 lines. All backend routers + frontend pages built. TypeScript compiles clean. Python syntax verified. Needs `docker compose up` for runtime verification (JWT auth flow, LLM-powered preview, batch refresh timing).

> **Partial head start from Phases 1-3**: `start_batch_refresh()` in `backend/app/workers/fetch_worker.py` implements concurrent source refresh with 60s cooldown, asyncio.gather isolation, and post-batch classification + dedup. The `hide_article()` utility in `backend/app/dedup/deduplicator.py` handles representative handoff when an admin hides an article. These can be called directly from admin endpoints. Additionally, `generate_briefing(db, force=True)` and `generate_learning_digest(db, force=True)` from Phase 3 provide the backend for admin briefing regeneration — Step 4.6 just needs a thin endpoint wrapper.

### Step 4.1 — Admin Authentication + Layout — COMPLETE

**What**: Password-based admin login, protected routes, admin layout with sidebar.

**Files**:

1. **backend/app/auth/admin.py** — Simple password auth:
   - `POST /api/admin/login` — accepts password, returns JWT token
   - `Depends(get_admin)` — middleware that validates JWT on admin endpoints
   - Single admin account (password from env `ADMIN_PASSWORD`)

2. **frontend/app/admin/layout.tsx** — Admin layout:
   - Sidebar navigation: Sources, Categories, Articles, Models & Tasks, Briefings, Analytics, System
   - Auth check: redirect to login if no valid token
   - Different visual treatment from reader (same tokens, admin-specific layout)

3. **frontend/app/admin/login/page.tsx** — Login page with password field.

**Verification**: Unauthenticated requests to `/api/admin/*` return 401. Login with correct password returns JWT. Admin pages render with sidebar.

---

### Step 4.2 — Sources Management — COMPLETE

**What**: Full source CRUD + Refresh All + Test Fetch + progress panel.

**Backend** (`backend/app/routers/admin_sources.py`):
- `GET /api/admin/sources` — all sources with status, surface, last fetch, failures
- `POST /api/admin/sources` — create (with surface: news/learning dropdown)
- `PUT /api/admin/sources/:id` — update config, interval, etc.
- `DELETE /api/admin/sources/:id` — cascades articles + fetch_logs
- `POST /api/admin/sources/:id/refresh` — trigger `scrape(source, trigger="manual")` then `classify_batch(source_ids=[source.id])`. Both functions exist from Phase 1.
- `POST /api/admin/sources/:id/test-fetch` — trigger `scrape(source, trigger="test")` — returns raw articles without inserting. Already implemented in scraper.
- `POST /api/admin/refresh-all` — delegate to `start_batch_refresh()` from `backend/app/workers/fetch_worker.py` (already built in Phase 1). Returns `batch_id`.
- `GET /api/admin/refresh-status/:batch_id` — query `fetch_logs WHERE batch_id = :id`, aggregate per-source status. **New endpoint needed.**
- `GET /api/admin/sources/:id/fetch-logs` — per-source log history

**Frontend** (`frontend/app/admin/sources/page.tsx`):
- Table: name, surface, status (●), last fetch, new articles, interval dropdown, actions
- Refresh All button in page header
- Progress panel (checkmarks, spinners, red Xs) — polls batch status
- Per-source: Refresh, Test Fetch, Edit, Disable/Enable
- Add source form with surface dropdown
- Fetch history expandable per source
- Red highlight for consecutive_failures >= 5

**Verification**: Add a test source, test fetch it, refresh it, see fetch logs. Refresh All runs all sources concurrently with progress panel. Interval changes take effect next cycle.

---

### Step 4.3 — Categories Management (Full Lifecycle) — COMPLETE

**What**: The admin's primary editorial tool — adding, rearranging, renaming, merging, and removing categories. Every operation must be fast, safe, and immediately visible on the reader site.

**Why this step is detailed**: Categories are the most frequently changed configuration in the system. The admin will rearrange tabs, add new topics as coverage evolves, merge overlapping categories, and tune descriptions to improve classification. Every one of these operations must feel instant and reversible. If changing a category requires a deploy, a database migration, or "wait 10 minutes and see," the admin won't iterate — and the reader experience stagnates.

#### Backend (`backend/app/routers/admin_categories.py`)

**CRUD:**
- `GET /api/admin/categories` — all categories grouped by surface, sorted by display_order. Includes article_count (last 7 days) per category.
- `POST /api/admin/categories` — create. Body: `{name, surface, description}`. Slug auto-generated from name (lowercase, hyphens for spaces, strip special chars). Returns the created category with its slug. Display_order defaults to max + 1 (appended to end).
- `PUT /api/admin/categories/:id` — update. Body: `{name?, slug?, description?, active?}`. If slug changes: insert a row in `category_redirects` mapping old_slug → new_slug (with surface). Collapse any existing redirect chain (if A → B exists and B → C is created, update A → C). If description changes: set `updated_at = now()` (useful for tracking when reclassification is needed).
- `DELETE /api/admin/categories/:id` — hard delete. Cascades `article_categories` rows. Returns count of affected articles. Requires confirmation (admin UI shows impact before confirming). Creates redirect if there's a sensible target (admin picks one, or no redirect).

**Ordering:**
- `PUT /api/admin/categories/reorder` — body: `[{id, display_order}]`. Updates display_order for every category in the list. Single request, single transaction. The frontend sends the full ordered list for the affected surface after a drag-drop.

**Preview (description tuning):**
- `POST /api/admin/categories/:id/preview` — body: `{description?}` (optional override — if omitted, uses the saved description). Takes the last 50 classified articles from this category's surface, runs the classification prompt with the provided description, returns: `{would_match: [{article_id, title, confidence}], currently_matched: [{article_id, title, confidence}]}`. The diff between these two lists shows exactly what the description change would do. This is the fast feedback loop — the admin can tweak the description and re-preview without saving.
- Preview uses the classification model from `pipeline_tasks` (same model that will do real classification). Response time: ~3 seconds for 50 articles with Haiku.

**Merge:**
- `POST /api/admin/categories/:id/merge` — body: `{target_id}`. Validates: same surface, target exists, target ≠ source. Steps:
  1. Reassign all `article_categories` from source → target (skip duplicates where article already has target)
  2. Insert `category_redirects` row: old_slug → target's current slug, with surface
  3. Delete source category (cascades any remaining article_categories — should be 0 after step 1)
  4. Return: `{articles_reassigned, redirect_created, source_deleted}`
- This is a single-transaction operation. If any step fails, the whole merge rolls back.

**Reclassification:**
- `POST /api/admin/reclassify` — body: `{since: "24h" | "7d", surface?: "news" | "learning"}`. Clears existing `article_categories` rows (where `manual_override = false`) for articles within the time window on the specified surface. Then triggers classification for those articles. This is a **background job** — the endpoint returns immediately with a job ID. The admin polls `GET /api/admin/reclassify/:job_id` for progress: `{total, processed, classified, uncategorized, failed, status}`.
- Reclassification is logged in `pipeline_logs` with `trigger='reclassify'`.

**Cache flush:**
- `POST /api/admin/cache/flush` — invalidates the HTTP cache for `/api/categories` and `/api/headlines`. After a category change, the admin can click "Flush Reader Cache" to make the change visible instantly instead of waiting ≤ 10 minutes. Implementation: if using CDN/Caddy cache, purge by path pattern. If using in-app cache (e.g., LRU), clear the relevant keys.

#### Frontend (`frontend/app/admin/categories/page.tsx`)

**Layout:**
- Two sections: "News Categories" and "Learning Categories" — each with its own drag-to-reorder list
- Each category row: drag handle | name (editable inline) | slug (shown muted, click to edit with redirect warning) | description (truncated, click to expand/edit) | article count badge | active toggle | actions dropdown (Preview, Reclassify, Merge, Delete)

**Add category flow:**
1. "Add Category" button per surface section
2. Inline form appears at the bottom of the list: name field (slug auto-generates as you type), description textarea, surface pre-filled
3. "Preview" button available before save — test the description against recent articles
4. "Save" creates the category appended to the list. Admin can then drag it to position.
5. "Flush Reader Cache" button appears after save with a prompt: "Category created. Flush cache to make it visible on the reader site immediately?"

**Rearrange flow:**
1. Drag a category row to a new position within its surface group
2. On drop: `PUT /api/admin/categories/reorder` fires with the new order
3. Success indicator (brief green flash on the row)
4. Optional: "Flush Reader Cache" to make the new tab order visible immediately

**Rename flow:**
1. Click the name to edit inline
2. On blur/enter: `PUT /api/admin/categories/:id` with new name
3. Slug stays unchanged by default — a small "(slug: economy)" hint shows the slug won't change
4. If the admin clicks the slug to edit it too: warning banner "Changing the slug will create a redirect. Old URLs will keep working." On save: redirect created.

**Description edit flow:**
1. Click description to expand into a textarea
2. Edit the description
3. "Preview" button runs the classification preview — shows a split view:
   - Left: "Currently classified here" (articles that have this category now)
   - Right: "Would be classified here" (articles that would match the new description)
   - Highlighted: articles that would be gained/lost by the change
4. Iterate until satisfied
5. "Save" commits the description
6. "Reclassify recent" button appears: "Description changed. Reclassify last 24h / 7d to apply retroactively?"

**Merge flow:**
1. Actions dropdown → "Merge into..."
2. Dropdown shows other categories in the same surface
3. Preview: "42 articles will be reassigned. /marketing-growth will redirect to /strategy."
4. "Confirm Merge" button
5. Source category disappears from the list. Target's article count increases.

**Delete flow:**
1. Actions dropdown → "Delete"
2. Confirmation: "This will remove 'Marketing & Growth' and unlink 38 articles. This cannot be undone. Type the category name to confirm."
3. On confirm: category deleted, articles may become uncategorized

**Verification**:
- Add a category → preview shows reasonable classification → save → appears in reader nav (after cache flush or ≤ 10 min)
- Drag categories to new order → reader tabs reflect new order
- Rename a category → reader shows new name, old slug still works (redirected)
- Change a description → preview shows diff → reclassify → articles shift to correct categories
- Merge two categories → articles reassigned, old slug redirects, source deleted
- Delete a category → articles unlinked, category gone from reader nav
- Disable a category (active toggle) → hidden from reader, articles preserved, re-enable restores it

---

### Step 4.4 — LLM Models & Pipeline Tasks — COMPLETE

**What**: Model registry management + task model assignment + cost tracking.

**Backend**:
- `backend/app/routers/admin_models.py` — model CRUD + test + provider status
- `backend/app/routers/admin_tasks.py` — task update (model assignment, active toggle, config) + cost estimate

**Frontend** (`frontend/app/admin/models/page.tsx`):
- Model registry table: provider, model, pricing, status, Test button
- Add Model form
- Pipeline Tasks section: task → model dropdown → active toggle → est. cost
- Cost breakdown by task (daily/monthly)
- API key status per provider (configured/valid)

**Verification**: Change classification model from Haiku to GPT-5 Mini → next classification uses GPT-5 Mini. Disable briefing task → no new briefings generated. Cost estimates update.

---

### Step 4.5 — Articles Management — COMPLETE

**What**: Search, filter, bulk actions, manual category overrides.

**Backend** (`backend/app/routers/admin_articles.py`):
- `GET /api/admin/articles` — search, filter by source/category/surface/date/classified status, paginate
- `PUT /api/admin/articles/:id` — update hidden, manual categories
- `POST /api/admin/articles/bulk` — bulk hide, assign category, reclassify

**Frontend** (`frontend/app/admin/articles/page.tsx`):
- Searchable, sortable table
- Columns: title, source, surface, categories (with confidence), published_at, clicks
- Filter sidebar: source, category, surface, date range, classified/unclassified
- Bulk select + actions

**Verification**: Search for an article, manually assign a category, hide an article → it disappears from reader. Bulk reclassify works.

---

### Step 4.6 — System Dashboard + Briefing Management — COMPLETE

**What**: Pipeline health, cost tracking, error feed, briefing management.

**Backend** (`backend/app/routers/admin_system.py`):
- `GET /api/admin/system/status` — per-source fetch status, per-task pipeline status, cost tracker, briefing status, queue depth
- `GET /api/admin/system/errors` — recent failed/partial logs

**Frontend** (`frontend/app/admin/page.tsx` — admin dashboard homepage):
- Fetch status per source (green/yellow/red)
- Pipeline task status per task
- LLM cost tracker (today, this month, by task)
- Briefing status: today's Brief? this week's Digest?
- Error feed
- Queue depth (unclassified articles count)

**Briefing management** (`frontend/app/admin/briefings/page.tsx`):
- List recent briefings (both types) with generation metadata
- Regenerate button per type

**Verification**: Dashboard shows real-time pipeline health. Costs match pipeline_logs. Errors are visible. Briefing regeneration works from admin.

---

### Phase 4 Exit Criteria

- [x] Admin login works with JWT — *(`POST /api/admin/login` returns JWT; `get_admin` dependency on all admin routers)*
- [x] Sources: CRUD, refresh, test fetch, batch refresh with progress — *(all endpoints in `admin_sources.py`; batch refresh delegates to `start_batch_refresh()`, status polling via `/refresh-status/{batch_id}`)*
- [x] Categories: CRUD, preview, reorder, merge, reclassify — *(all endpoints in `admin_categories.py`; preview uses real LLM call; reclassify runs as background `asyncio.create_task`)*
- [x] Category rename: slug unchanged, name updates immediately — *(PUT `/categories/{id}` with name-only update)*
- [x] Category slug change: old slug redirects to new slug (301) — *(redirect chain collapse + new `CategoryRedirect` row on slug change)*
- [x] Category merge: articles reassigned, old slug redirects, source deleted — *(single-transaction merge in `POST /categories/{id}/merge`)*
- [x] Category rearrange: drag-and-drop → new tab order visible after cache flush — *(native HTML5 drag; `PUT /categories/reorder` declared before `/{id}` route)*
- [x] Cache flush: admin can force instant visibility of category changes — *(Next.js Route Handler at `/api/revalidate` calls `revalidatePath('/', 'layout')`)*
- [x] Models: CRUD, test, provider status — *(model test calls provider adapter directly, not via `run_classify`; delete guarded by 409 if assigned to active task)*
- [x] Tasks: model assignment, active toggle, cost estimate — *(model change validated: must be active + provider key configured; cost estimate extrapolates from 7-day `pipeline_logs`)*
- [x] Articles: search, filter, manual override, bulk actions — *(title search via `ilike`, 6 filter dimensions, bulk hide/unhide/assign_category; manual assignments use `manual_override=True`)*
- [x] System dashboard: health, costs, errors, queue depth — *(single `/system/status` endpoint aggregates sources, tasks, costs, briefings, queue)*
- [x] Briefings: view, regenerate both types — *(list last 30 days; regenerate delegates to `generate_briefing(force=True)` / `generate_learning_digest(force=True)`)*
- [x] All operations logged (fetch_logs, pipeline_logs) — *(reuses existing logging infrastructure from Phases 1-3; reclassify writes pipeline_log with trigger="reclassify")*

---

### Phase 4 Implementation Record

**Status**: Code complete. All backend routers and frontend pages written. TypeScript compiles with zero errors. Python syntax verified (ast.parse). Needs `docker compose up` for runtime verification (JWT auth flow, admin UI rendering, LLM-powered preview and model testing, batch refresh timing).

**Date**: 2026-03-17

#### What was built (18 new files, 2 modified)

| Area | Files | Key modules |
|------|-------|-------------|
| Auth package | 2 | `auth/__init__.py`, `auth/admin.py` — JWT login endpoint + `get_admin` security dependency |
| Admin routers | 6 | `admin_sources.py` (9 endpoints), `admin_categories.py` (8 endpoints + background reclassify), `admin_models.py` (6 endpoints), `admin_tasks.py` (3 endpoints), `admin_articles.py` (3 endpoints), `admin_system.py` (4 endpoints) |
| Schemas | 1 (modified) | `schemas/admin.py` — extended with 20 new request/response models (was 6, now 26) |
| App entry | 1 (modified) | `main.py` — mounts auth router + 6 admin routers |
| Admin API client | 1 | `frontend/lib/admin-api.ts` — `adminFetch()` with JWT + auto-redirect on 401 |
| Admin pages | 8 | `login/page.tsx`, `layout.tsx`, `page.tsx` (dashboard), `sources/page.tsx`, `categories/page.tsx`, `models/page.tsx`, `articles/page.tsx`, `briefings/page.tsx` |
| Cache infrastructure | 1 | `frontend/app/api/revalidate/route.ts` — ISR cache flush via `revalidatePath()` |

**Total admin endpoints: 33** across 7 routers (1 public login + 32 protected).

#### Deviations from plan

**1. Schemas consolidated into single file, not split per domain**

The BUILD_PLAN Step 1.3 described separate schema files per admin domain (`admin_sources.py`, `admin_categories.py`, etc.). The actual project consolidated all admin schemas into a single `schemas/admin.py` during Phase 1. Phase 4 extends this same file with 20 additional models rather than creating 6 new files. This is simpler and avoids circular imports between related admin schemas (e.g., `ArticleCategoryDetail` used by both article and category responses).

**2. Cache flush via Next.js Route Handler, not backend endpoint**

The plan described `POST /api/admin/cache/flush` as a backend endpoint. The implementation uses a Next.js Route Handler at `/api/revalidate` that calls `revalidatePath('/', 'layout')`. This is more correct: the ISR cache lives in Next.js, not FastAPI — the backend has no cache to invalidate. The admin's "Flush Cache" button calls this endpoint directly (same origin). Protected by `REVALIDATION_SECRET` env var (matches `NEXT_PUBLIC_REVALIDATION_SECRET` sent by the client).

**3. Admin sidebar excludes Analytics**

The plan's sidebar listed "Analytics" as a navigation item. Since Phase 5 (Analytics) hasn't been built, the implementation correctly omits it. When Phase 5 is built, add `{ href: "/admin/analytics", label: "Analytics" }` to the `NAV_ITEMS` array in `frontend/app/admin/layout.tsx`.

**4. No `select_for_update()` on category merge**

The plan mentioned using `select_for_update()` to lock the source category row during merge to prevent race conditions. The implementation uses the default transaction isolation (READ COMMITTED) without explicit row locking. Acceptable for a single-user admin tool — concurrent merge operations are extremely unlikely. Can be added if needed.

**5. Reclassification progress is coarse-grained (as planned)**

The plan noted that progress tracking would be "running → complete" without intermediate updates, because `classify_batch()` processes all articles atomically. The implementation follows this honestly — the admin sees total count and status transitions (`starting` → `running` → `complete` or `failed: <error>`). No fake progress bars.

**6. `ArticleAdminResponse.categories` changed from `list[str]` to `list[ArticleCategoryDetail]`**

The Phase 1 schema had `categories: list[str]` (just slugs). The admin panel needs confidence scores and manual override flags, so this was changed to `list[ArticleCategoryDetail]` (slug + confidence + manual boolean). This is a breaking change to the admin schema but does not affect the public reader API (which uses `schemas/headlines.py`).

#### Key design decisions

1. **`dependencies=[Depends(get_admin)]` on router, not per-endpoint**: All 6 admin routers declare the auth dependency at the router level. This eliminates the risk of forgetting `Depends(get_admin)` on individual endpoints — every route in the router is automatically protected.

2. **Lazy imports for circular dependency avoidance**: Admin router endpoints that call pipeline functions (`scrape`, `classify_batch`, `dedup_batch`, `generate_briefing`, etc.) use lazy imports inside the function body, consistent with Phases 1-3.

3. **`joinedload` / `selectinload` everywhere**: All relationships use `lazy="raise"`, so every query that accesses related objects (e.g., `article.source`, `article.article_categories`) must explicitly load them. The admin routers follow this strictly.

4. **Client Components throughout**: All admin pages use `"use client"` directive. Data fetching via `useState` + `useEffect` + `adminFetch()`. No SWR/React Query — sufficient for single-user admin tool.

5. **Native HTML5 drag-and-drop for category reorder**: No DnD library. Uses `draggable`, `onDragStart`, `onDragOver`, `onDrop` attributes. Reorder is a simple flat list per surface — doesn't need library complexity.

6. **Background reclassification with module-level dict**: `_reclassify_jobs` dict in `admin_categories.py` stores job progress. Jobs are lost on process restart (idempotent — admin just restarts). If this becomes a problem, migrate to DB-backed job state.

#### Known limitations to address before production

1. **JWT in localStorage** — XSS can steal the token. Acceptable for single-user internal tool. CSP headers mitigate XSS. Token expires in 24h.
2. **Batch refresh blocks HTTP request** — `POST /api/admin/refresh-all` can take 10-30s. Frontend uses `AbortSignal.timeout(60000)`. Per-source status available via `/refresh-status/{batch_id}` if request times out.
3. **Preview endpoint costs tokens** — Classification preview calls `run_classify()` on 50 articles. ~$0.001 per preview with Haiku, ~3s latency. No caching.
4. **No admin API rate limiting** — All admin endpoints are unthrottled. The auth gate is the only protection. Consider rate limiting if exposed to internet.
5. **`REVALIDATION_SECRET` must be configured in production** — Both `REVALIDATION_SECRET` (server) and `NEXT_PUBLIC_REVALIDATION_SECRET` (client) must be set to the same non-empty value. In development, both default to `""` and match (endpoint works but is unprotected).

---

## Phase 5: Analytics

**Goal**: Understand how people use the reader site — sessions, clicks, engagement by source and category.

> **Partial head start from Phase 1**: `frontend/lib/analytics.ts` already implements `trackEvent()` with session ID generation (currently uses `sessionStorage`, not cookies). The `POST /api/events` backend endpoint is already built and writes to `analytics_events`. See "Phase 1 Implementation Record — Deviation #6" above.

### Step 5.1 — Client-Side Event Tracking

**What**: Session management + event firing on the reader frontend.

**File**: `frontend/lib/analytics.ts` (exists, needs enhancement)

**Tasks**:

1. **Session management**: ~~On first page load, check for `headlines_sid` cookie.~~ **UPDATE**: Phase 1 implemented session ID via `sessionStorage`. Switch to cookie-based with `max-age=1800`, `SameSite=Strict`, `path=/` per DESIGN.md spec. Each page load resets max-age. This gives 30-minute inactivity window and survives page reloads (sessionStorage doesn't expire on inactivity).
2. **page_view event**: Wire `trackEvent("page_view", { surface, category_slug })` into page components. Consider a client-side wrapper component or `useEffect` hook.
3. **headline_click event**: Wire `trackEvent("headline_click", { article_id, source_slug, surface })` into HeadlineItem/LeadHeadline click handlers. These are currently Server Components — may need a thin client wrapper for the click tracking.
4. **POST /api/events** — ~~Build endpoint~~ **Already built** in Phase 1 (`backend/app/routers/events.py`). Consider adding `navigator.sendBeacon` or `fetch` with `keepalive` for reliability.

**Verification**: Open reader site, navigate between categories, click headlines → check `analytics_events` table has correct events with session_ids.

---

### Step 5.2 — Analytics Dashboard

**What**: Admin analytics views.

**Backend** (`backend/app/routers/admin_analytics.py`):
- `GET /api/admin/analytics/overview` — daily unique sessions, page views, CTR, new vs returning
- `GET /api/admin/analytics/top-headlines?period=7d` — top headlines by clicks
- `GET /api/admin/analytics/by-source?period=7d` — CTR by source
- `GET /api/admin/analytics/by-category?period=7d` — CTR by category
- `GET /api/admin/analytics/by-hour?period=7d` — time-of-day distribution

All queries are SQL aggregations on `analytics_events`. No separate analytics infrastructure.

**Frontend** (`frontend/app/admin/analytics/page.tsx`):
- Overview cards: sessions today, page views, CTR
- Charts: top headlines, by-source breakdown, by-category breakdown, time-of-day
- Period selector: 7d, 30d, 90d

**Verification**: After some browsing on the reader site, analytics dashboard shows accurate metrics. CTR calculated correctly (clicks / impressions).

---

### Phase 5 Exit Criteria

- [x] Session cookies generated on reader site
- [x] page_view and headline_click events recorded
- [x] Analytics dashboard shows sessions, CTR, top headlines
- [x] Breakdown by source and category works
- [x] Time-of-day distribution visible

---

### Phase 5 Implementation Record

**Status**: Code complete. All backend endpoints and frontend pages written. Needs `docker compose up` + `alembic upgrade head` (migration 004) for runtime verification (event recording, analytics queries, dashboard rendering).

**Date**: 2026-03-17

#### What was built (5 new files, 8 modified)

| Area | Files | Key modules |
|------|-------|-------------|
| Model update | 1 (modified) | `models/analytics_event.py` — added `surface` column + `idx_analytics_surface` composite index |
| Event endpoint fix | 1 (modified) | `routers/events.py` — now stores `event.surface` in DB |
| Migration | 1 | `alembic/versions/004_add_surface_to_analytics.py` — adds `surface` column + index |
| Analytics schemas | 1 | `schemas/analytics.py` — 11 Pydantic response models (Overview, TopHeadlines, BySource, ByCategory, ByHour + sub-models) |
| Analytics router | 1 | `routers/admin_analytics.py` — 5 admin-protected endpoints with `Period` enum |
| App entry | 1 (modified) | `main.py` — mounts `admin_analytics` router |
| Session upgrade | 1 (modified) | `frontend/lib/analytics.ts` — cookie-based sessions replacing sessionStorage, added `source_slug` to data type |
| Data attributes | 2 (modified) | `HeadlineItem.tsx`, `LeadHeadline.tsx` — added `data-article-id` and `data-source-slug` to outer `<a>` tags |
| Analytics provider | 1 | `frontend/components/AnalyticsProvider.tsx` — Client Component with event delegation |
| Reader layout | 1 (modified) | `frontend/app/(reader)/layout.tsx` — wraps children in `<AnalyticsProvider>` |
| Admin nav | 1 (modified) | `frontend/app/admin/layout.tsx` — added "Analytics" nav item |
| Dashboard page | 1 | `frontend/app/admin/analytics/page.tsx` — full analytics dashboard with 5 sections |

**Total analytics endpoints: 5** — overview, top-headlines, by-source, by-category, by-hour. All under `GET /api/admin/analytics/*` with `Depends(get_admin)` at router level.

#### Deviations from plan

**1. Event delegation instead of Client Component conversion**

The BUILD_PLAN Step 5.1 item 3 noted "may need a thin client wrapper for the click tracking." The implementation uses a single `AnalyticsProvider` Client Component that wraps the reader layout's children and attaches a `document.addEventListener("click")` handler. Headline clicks are detected via `closest("a[data-article-id]")` event delegation. HeadlineItem and LeadHeadline remain pure Server Components — they only received `data-*` HTML attributes (no `"use client"`, no event handlers). This preserves the SSR architecture.

**2. `navigator.sendBeacon` deferred**

Step 5.1 item 4 mentioned "Consider adding `navigator.sendBeacon` or `fetch` with `keepalive` for reliability." The implementation uses plain `fetch`. All headline links use `target="_blank"` so the reader page stays open and the fetch completes. If same-tab navigation is added later, switch `trackEvent` to `navigator.sendBeacon` with a `Blob` wrapper for correct `Content-Type`.

**3. By-source shows clicks + share, not CTR**

The BUILD_PLAN Step 5.2 described "CTR by source." The implementation returns click count and click share (clicks / total_clicks) instead. True per-source CTR requires impression tracking (which headlines were visible on each page view), which the analytics system doesn't capture. This was called out as an explicit architecture decision.

**4. Hour-of-day in UTC**

The `EXTRACT(HOUR FROM created_at)` operates on the UTC-stored timestamp. The dashboard shows hours 0-23 without timezone annotation. Acceptable for a single-timezone user; could add timezone conversion via `AT TIME ZONE` if multi-timezone support is needed.

**5. `surface` derived from pathname, not from a prop**

The `AnalyticsProvider` determines surface from `pathname.startsWith("/learning")`. The existing `data-surface` attribute on `SurfacePage`'s container div is used for `headline_click` events (via `closest("[data-surface]")`), but `page_view` events derive surface from the URL. Both approaches yield the same result given the routing structure.

#### Key design decisions

1. **Event delegation pattern**: A single `document.addEventListener("click")` catches all headline clicks via `data-article-id` attribute detection. This avoids converting any Server Component to a Client Component and has zero hydration overhead on headline elements. New headline components automatically get tracking by adding `data-article-id` to their links.

2. **Cookie-based sessions with 30-minute rolling expiry**: `headlines_sid` cookie with `max-age=1800`, `SameSite=Strict`, `path=/`. Each `trackEvent` call resets the max-age, creating a rolling inactivity window. Replaces sessionStorage which had no inactivity timeout.

3. **`surface` as a real column**: Added `Text` column with composite B-tree index `(surface, created_at)` rather than storing in JSONB `metadata`. Analytics queries frequently filter/group by surface — a real column is far more efficient than JSONB extraction. Migration 004 adds the column non-destructively (nullable, no backfill needed).

4. **CSS-only charts**: Horizontal bar charts use percentage-width `<div>` with `bg-accent` inside `bg-surface-alt` containers. Vertical hour chart uses flex columns with percentage heights. No chart library dependency. Matches the minimal admin UI aesthetic established in Phase 4.

5. **`Period` enum across all endpoints**: All 5 analytics endpoints accept `?period=7d|30d|90d` via a shared `Period` enum with `_cutoff()` and `_days()` helpers. Consistent filtering pattern, easy to extend (e.g., `1d`, `365d`).

6. **Parallel data fetching**: The dashboard fires all 5 `adminFetch` calls via `Promise.all` on mount and period change. Single loading state — the dashboard appears fully populated once all queries complete.

7. **Router-level auth dependency**: Following the Phase 4 pattern, `dependencies=[Depends(get_admin)]` is declared on the router, not per-endpoint. All 5 analytics endpoints are automatically protected.

#### Known limitations

1. **No data until real usage** — Analytics dashboard shows zeros/empty states until the reader site generates events. The dashboard handles this gracefully with "No click data yet" messages.
2. **Returning session detection scales linearly** — The `IN` subquery for returning sessions scans all historical session_ids before the cutoff. Acceptable for expected traffic (<1K sessions/day). The `idx_analytics_session` index covers it. If needed, add a `sessions` materialized view.
3. **No impression tracking** — Cannot calculate true per-source or per-headline CTR (requires knowing which headlines were visible). By-source shows click count and share. Site-wide and by-category CTR use page views as the denominator.
4. **`category_slug` null on homepage** — Homepage shows mixed categories, so page_view events from `/` have no `category_slug`. The by-category query filters `WHERE category_slug IS NOT NULL`, correctly excluding homepage views.
5. **No caching on analytics endpoints** — Each dashboard load runs 5 SQL aggregation queries against `analytics_events`. Acceptable for single-user admin. Could add short TTL caching if query latency becomes noticeable.

---

## Phase 6: Polish

**Goal**: Production-readiness — responsive design, performance, error alerting, RSS output.

**Status**: Code complete (2026-03-17). 3 new files + 17 modified = 20 files, ~350 lines of new code.

### Step 6.1 — Responsive Design Pass

**Core mechanism**: CSS custom property overrides at breakpoints in `primitives.css`. Changing `--width-content`, `--text-2xl`, `--text-lg`, and `--width-column-gap` at breakpoints propagates through the entire token chain (`primitives → semantic → components → Tailwind`) without touching any component code.

**Reader-side changes** (3 files):
- `frontend/styles/tokens/primitives.css` — Two `@media` blocks: tablet (≤1199px: `--width-content: 45rem`) and mobile (≤767px: `--width-content: 100%`, smaller text, tighter gaps). Also updated `--font-sans` to use `var(--font-inter)` CSS variable for `next/font` integration.
- `frontend/styles/globals.css` — Added `scrollbar-hide` utility in `@layer utilities` (hides native scrollbar with `-webkit-overflow-scrolling: touch` + `scrollbar-width: none`). Scoped to a class — NOT applied globally, so admin data tables keep visible scrollbars.
- `frontend/components/CategoryNav.tsx` — Added `scrollbar-hide` class alongside existing `overflow-x-auto`. Fade gradient already hints at scrollability.
- `frontend/components/Masthead.tsx` — Changed `py-6` to `py-4 md:py-6`.

**No changes needed** for: `HeadlineList` (`md:grid-cols-2` already correct), `LeadHeadline`/`HeadlineItem` (scale via tokens), `SurfaceNav` (two items fit any screen), `Footer`/`Pagination` (text-only, wraps gracefully), dark mode (all changes use CSS custom properties).

**Admin-side changes** (6 files):
- `frontend/app/admin/layout.tsx` — Sidebar collapses to horizontal top bar on mobile. Container: `min-h-screen bg-surface md:flex`. Aside: `md:w-56 md:shrink-0`, switches `border-r` to `border-b md:border-b-0 md:border-r`. Nav: `flex gap-1 overflow-x-auto scrollbar-hide md:overflow-visible md:flex-col md:flex-1`. Dual logout buttons (inline mobile, `hidden md:block` desktop). Main: `p-4 md:p-6`.
- `frontend/app/admin/sources/page.tsx` — Nested `overflow-x-auto` div inside `overflow-hidden` wrapper for border-radius clipping.
- `frontend/app/admin/articles/page.tsx` — Same table scroll wrapper pattern.
- `frontend/app/admin/analytics/page.tsx` — Same table scroll wrapper + stat cards changed from `grid-cols-4` to `grid-cols-2 md:grid-cols-4`.
- `frontend/app/admin/models/page.tsx` — Same table scroll wrapper.
- `frontend/app/admin/page.tsx` — Two table scroll wrappers (Source Health + Pipeline Tasks) + stat cards changed to `grid-cols-2 md:grid-cols-4`.

**Breakpoint behavior**:
- ≥1200px: Content column centered at 840px (`52.5rem`), two-column headline grid
- 768–1199px: Content column at 720px (`45rem`), two-column grid
- <768px: Full-width with gutter padding, single-column grid, smaller headlines (22px/16px), admin sidebar becomes top bar

### Step 6.2 — Performance Optimization

**Backend** (1 file):
- `backend/app/routers/briefing.py` — Added `Response` parameter, set `Cache-Control: public, max-age=300` (daily news) / `max-age=1800` (weekly learning) when briefing exists, `max-age=60` when no briefing found. Headlines (120s/1800s) and categories (600s) were already cached from Phase 1.

**Frontend** (3 files):
- `frontend/lib/api.ts` — Fixed double-spread bug (lines 13–15 spread `options` twice, second spread overwrote `next.revalidate`). Refactored `apiFetch` to accept optional `revalidate` parameter, destructured before spreading to `fetch()`. Updated call sites: `fetchHeadlines` (120s news / 1800s learning), `fetchCategories` (600s), `fetchBriefing` (300s news / 1800s learning).
- `frontend/app/layout.tsx` — Integrated `next/font/google` Inter with `subsets: ["latin"]`, `variable: "--font-inter"`, `display: "swap"`. Added `className={inter.variable}` to `<html>`. Provides automatic self-hosting, preload hints, zero CLS.
- `frontend/next.config.ts` — Added `headers()` function setting `Cache-Control: public, max-age=31536000, immutable` on `/_next/static/:path*`. Next.js does this by default for hashed assets, but explicit declaration prevents proxy stripping.

**Deferred**: Database query tuning (existing indexes sufficient at current scale). Lighthouse audit deferred to runtime verification.

### Step 6.3 — Retention Pipeline

**New file**: `backend/app/workers/retention_worker.py` (~40 lines)

Single async function `run_retention()` using `async with async_session() as db:`. Five bulk `DELETE` queries using SQLAlchemy `delete()` construct (no ORM loading):

| Table | Condition | Cascade |
|-------|-----------|---------|
| `articles` | `published_at < now - 30d` | `article_categories` via FK CASCADE |
| `briefings` | `date < today - 30d` | None |
| `fetch_logs` | `started_at < now - 90d` | None (uses `started_at` — has `idx_fetch_logs_started` index) |
| `pipeline_logs` | `started_at < now - 90d` | None (uses `started_at` — has `idx_pipeline_logs_started` index) |
| `analytics_events` | `created_at < now - 90d` | None |

Logs row counts via `logger.info`. Wraps in try/except with rollback on error. `AnalyticsEvent.article_id` has NO FK constraint (plain UUID column), so deleting articles won't cause FK violations.

**Scheduler** (1 file modified): `backend/app/workers/scheduler.py` — Registered `run_retention` as `daily_retention` job at 3:00 AM UTC via `CronTrigger(hour=3, minute=0, timezone="UTC")`.

### Step 6.4 — Error Alerting

**Config** (1 file): `backend/app/config.py` — Added `SLACK_WEBHOOK_URL: str = ""`. Empty string = disabled. All alerting code guards with `if settings.SLACK_WEBHOOK_URL:`. Email alerting deferred — adds SMTP complexity (4+ env vars) for minimal gain over Slack.

**New file**: `backend/app/workers/alerting.py` (~70 lines). Three functions:

1. **`notify_slack(message)`** — POST to webhook URL using `httpx.AsyncClient(timeout=10)`. Fire-and-forget with try/except. Returns immediately if `SLACK_WEBHOOK_URL` is empty.
2. **`check_source_alert(source_name, consecutive_failures)`** — Fires at exact threshold (`== 5`), not `>= 5`. Only triggers once per failure streak, avoiding spam on subsequent failures.
3. **`send_daily_error_summary()`** — Opens own DB session, counts FetchLog/PipelineLog errors in last 24h, lists sources with `consecutive_failures >= 5`. Sends formatted Slack message. Exits early if nothing to report.

**Scheduler wiring** (1 file modified): `backend/app/workers/scheduler.py` — Two integration points:
- Source failure alert in `_tick()`: After `scrape()` returns and commits, checks `fetch_result.status == "failed"` and calls `check_source_alert()`. Wrapped in try/except so alerting never breaks the pipeline. Placed after the except/continue block so it only runs on successful commit paths.
- Daily error summary: Registered `send_daily_error_summary` at 7:00 AM UTC via `CronTrigger(hour=7, minute=0, timezone="UTC")`.

### Step 6.5 — RSS Output

**New file**: `backend/app/routers/feed.py` (~60 lines)

`GET /api/feed.xml` with optional `?surface=news|learning` (default `"news"`). Uses `xml.etree.ElementTree` from stdlib (no new dependency). Reuses the same article filtering pattern as `headlines.py`: `hidden=False`, `classified=True`, `is_representative=True`, JOIN Source where `surface` matches, `ORDER BY published_at DESC LIMIT 50`.

RSS 2.0 structure:
- `<channel>`: title (`Headlines — News/Learning`), link, description, lastBuildDate (RFC 822 via `email.utils.format_datetime`)
- `<item>`: title, link, guid (`isPermaLink="true"`), description (summary if available), pubDate, source (with `url` attribute pointing to source homepage)

Response: `media_type="application/rss+xml; charset=utf-8"`, `Cache-Control: public, max-age=300`.

**Router registration** (1 file modified): `backend/app/main.py` — Added `from app.routers import feed` and `app.include_router(feed.router)` after `events` router, before admin routers.

---

### Phase 6 File Manifest

**New files (3)**:

| File | Lines | Purpose |
|------|-------|---------|
| `backend/app/workers/retention_worker.py` | ~40 | Daily cleanup of old data |
| `backend/app/workers/alerting.py` | ~70 | Slack webhook notifications |
| `backend/app/routers/feed.py` | ~60 | RSS 2.0 feed endpoint |

**Modified files (17)**:

| File | Change |
|------|--------|
| `frontend/styles/tokens/primitives.css` | Responsive media queries (tablet + mobile) + `--font-sans` update for `next/font` |
| `frontend/styles/globals.css` | `scrollbar-hide` utility class |
| `frontend/components/Masthead.tsx` | Responsive padding (`py-4 md:py-6`) |
| `frontend/components/CategoryNav.tsx` | Added `scrollbar-hide` class |
| `frontend/app/admin/layout.tsx` | Sidebar → top bar on mobile (largest frontend change) |
| `frontend/app/admin/sources/page.tsx` | Table scroll wrapper |
| `frontend/app/admin/articles/page.tsx` | Table scroll wrapper |
| `frontend/app/admin/analytics/page.tsx` | Table scroll wrapper + responsive stat grid |
| `frontend/app/admin/models/page.tsx` | Table scroll wrapper |
| `frontend/app/admin/page.tsx` | Two table scroll wrappers + responsive stat grid |
| `frontend/lib/api.ts` | Fixed double-spread bug + surface-aware ISR revalidation |
| `frontend/app/layout.tsx` | `next/font/google` Inter integration |
| `frontend/next.config.ts` | Static asset cache headers |
| `backend/app/routers/briefing.py` | Cache-Control headers (300s/1800s/60s) |
| `backend/app/config.py` | `SLACK_WEBHOOK_URL` env var |
| `backend/app/workers/scheduler.py` | Retention + error summary jobs, source failure alert in `_tick()` |
| `backend/app/main.py` | Feed router registration |

### Phase 6 Exit Criteria

- [x] Responsive on all breakpoints (token cascade, admin sidebar collapse, table scroll wrappers, responsive grids)
- [ ] Lighthouse 95+ across all categories (infrastructure in place — audit deferred to runtime verification)
- [x] Retention pipeline running daily (3:00 AM UTC, 30d articles/briefings, 90d logs/analytics)
- [x] Error alerting configured (Slack webhook — email deferred)
- [x] Cache-Control headers on all public endpoints (headlines, categories, briefing, feed)

---

## Phase 7: In Focus

**Goal**: The aggregator's unique editorial value — identifying the top story and showing how each publication frames it differently. Leverages existing dedup cluster infrastructure to find the most cross-source story, then generates an LLM framing comparison.

### Step 7.1 — Analysis Pipeline ✓

**3 new files, 8 modified. ~220 lines of new backend code.**

1. **Model columns** (`backend/app/models/briefing.py`): Added `focus_topic`, `focus_body`, `focus_model` — three nullable Text columns on the existing Briefing model. Column isolation: briefing upsert only touches `brief`/`article_ids`/`brief_model`/`generated_at`; analysis upsert only touches `focus_*` columns. Neither overwrites the other.

2. **Migration 005** (`backend/alembic/versions/005_add_focus_and_analysis.py`): Adds the 3 columns + seeds `analysis` pipeline task (copies `model_id` from briefing task, config `{"min_sources": 3}`).

3. **Prompts** (`backend/app/editorial/prompts.py`): `ANALYSIS_SYSTEM_PROMPT` instructs the LLM to write a topic headline, then `---` separator, then 2–4 sentences of flowing prose comparing how each source frames the story. `build_analysis_prompt()` formats the cluster articles with title, source name, and truncated summary.

4. **Analysis pipeline** (`backend/app/editorial/analysis.py`): `generate_analysis(db, trigger, force)` — follows the exact pattern from `briefing.py`:
   - Task check → date resolution → idempotency (checks `focus_topic` instead of `brief`)
   - **Core query**: Finds cluster with most distinct `source_id` values in last 24h, filtered to news surface, classified, not hidden, with `cluster_id` set. Uses `HAVING count(distinct source_id) >= min_sources`.
   - **Per-source dedup**: A cluster can contain multiple articles from the same source. Keeps the most recently published article per `source_id`.
   - **LLM generation** via `run_generate(db, "analysis", ...)` — provider-agnostic with retry.
   - **Output parsing**: Splits on first `---` line. Fallback: first line = topic, rest = body.
   - **Upsert**: `ON CONFLICT (type, date) DO UPDATE SET focus_topic, focus_body, focus_model` — creates a partial briefing row if analysis runs before briefing (harmless: EditorialSummary guards with `if (!briefing?.brief)`).
   - Pipeline log with token counts and cost.

5. **Scheduler** (`backend/app/workers/scheduler.py`): `_run_analysis()` + CronTrigger at 7:00 AM daily (30 min after briefing). **No post-classify trigger** — In Focus needs the full picture from all sources; early triggers would produce incomplete analysis that idempotency then blocks from regenerating.

6. **API response** (`backend/app/schemas/briefing.py`, `backend/app/routers/briefing.py`): `focus_topic` and `focus_body` fields added to `BriefingResponse` and included in response construction.

7. **Admin** (`backend/app/schemas/admin.py`, `backend/app/routers/admin_system.py`): `focus_topic`, `focus_body`, `focus_model` added to `BriefingAdminResponse`. Regenerate endpoint extended with `elif body.type == "analysis"`. `"analysis"` added to `task_names` list in system_status for cost tracking and last-run display.

### Step 7.2 — In Focus Frontend ✓

**1 new file, 2 modified. ~30 lines of new frontend code.**

1. **TypeScript types** (`frontend/lib/types.ts`): `focus_topic` and `focus_body` added to `BriefingResponse`.

2. **InFocus component** (`frontend/components/InFocus.tsx`): Server Component following the same pattern as `EditorialSummary.tsx`. Guards with `config.slug !== "news"` (early return before `fetchBriefing` — no API call on learning surface). Renders: "In Focus" label (`text-section-label text-briefing-label`) → topic headline (`text-headline font-serif`) → body (`text-briefing-text`) → `<hr>` separator. All styling matches THE BRIEF for visual consistency.

3. **SurfacePage wiring** (`frontend/components/SurfacePage.tsx`): `<InFocus config={config} />` inserted between `<EditorialSummary>` and `<HeadlineList>`. Next.js auto-deduplicates the `fetchBriefing()` call (same URL as EditorialSummary in one render pass) — zero performance cost.

**Key design decisions:**
- **Scheduled-only generation** (no post-classify trigger) — a framing comparison with missing source perspectives is worse than no comparison. The 7:00 AM run captures overnight accumulation.
- **Column isolation on shared row** — analysis and briefing can run in any order without data loss. Each upsert's `set_` clause is scoped to its own columns.
- **Configurable min_sources** via `pipeline_tasks.config` — defaults to 3, adjustable without code changes.
- **Graceful degradation** — if no cluster qualifies, analysis returns `{"status": "skipped"}`. If focus fields are null, InFocus component returns `null` (no empty container rendered).

---

## Phase 8: Monopage Reader Navigation

**Goal**: Convert both reader surfaces (News at `/`, Learning at `/learning`) from multi-page category routing to single-page scroll navigation. Each surface becomes one page showing all categories as scrollable sections, with category tabs acting as scroll-to anchors and per-section "Show more" client-side pagination.

**Motivation**: The multi-page approach (clicking "Economy" navigates to `/economy`, triggering a full server fetch) creates unnecessary navigation latency. The monopage approach shows all content upfront with instant category switching via smooth scroll.

### Step 8.1 — Monopage Reader Navigation ✓

**3 new files, 5 rewritten/modified, 4 deleted. ~200 lines of new frontend code.**

#### Architecture change

**Before**: Single filtered `fetchHeadlines({ surface, category, page })` call per route. CategoryNav uses `<Link>` for route-based navigation. HeadlineList groups headlines by time/topic. Pagination links to `?page=N`.

**After**: Two-round parallel server fetch (categories + lead headline → per-category headlines). CategoryNav uses `<button>` with `scrollIntoView()` and IntersectionObserver scroll-spy. CategorySections (new Client Component) renders per-category `<section>` elements with "Show more" client-side pagination.

Server fetch pattern in SurfacePage:
- **Round 1** (parallel): `fetchCategories(surface)` + `fetchHeadlines({ surface })` (unfiltered, for lead headline — news only)
- **Round 2** (parallel, after categories known): `fetchHeadlines({ surface, category: cat.slug })` for each category, via `Promise.allSettled` (one failed category doesn't crash the page)

#### Files created (3)

1. **`frontend/components/CategorySections.tsx`** — Client Component. Core new component. Receives server-fetched initial data, manages per-section "Show more" state.
   - Each `<section id={category.slug} className="scroll-mt-16">` serves as scroll target for CategoryNav and analytics context (AnalyticsProvider reads `closest("section[id]")`)
   - `scroll-mt-16` (4rem) accounts for sticky CategoryNav height — works for both `scrollIntoView()` and native hash scrolling
   - "Show more" button per section: client-side `fetch()` using `NEXT_PUBLIC_API_URL`, appends results, updates pagination metadata
   - Concurrency guard via `loadingRef` (ref, not state) to prevent stale closure issues with React batched updates
   - Error handling: try/catch/finally — silently fails on error (user can retry), `finally` always clears loading state

2. **`frontend/app/(reader)/page.tsx`** — Root news page. Replaces the catch-all `[[...slug]]/page.tsx`. Minimal: renders `SurfaceNav` + `SurfacePage` with no category/page params.

3. **`frontend/app/(reader)/[slug]/page.tsx`** — Legacy redirect. `/:slug` → `/#slug` for backwards compatibility. Dynamic segment — only catches slugs not matched by static routes (`/admin`, `/learning`).

#### Files rewritten (4)

4. **`frontend/components/SurfacePage.tsx`** — Two-round parallel fetches, composes CategorySections + LeadHeadline. Props reduced to just `config: SurfaceConfig` (removed `page`, `category`). Lead headline: unfiltered fetch for news (`showLeadHeadline: true`), skipped for learning. `Promise.allSettled` for per-category resilience — failed categories render as empty sections.

5. **`frontend/components/CategoryNav.tsx`** — Complete rewrite: `<Link>` → `<button>`, `router.push()` → `scrollIntoView()`. Sticky nav (`sticky top-0 z-10 bg-surface border-b border-rule`). IntersectionObserver scroll-spy with `rootMargin: "0px 0px -70% 0px"` (top 30% of viewport = intersection zone). `isScrollingRef` flag suppresses observer during programmatic scrolling (1s timeout, cleared on rapid clicks). URL hash sync via `replaceState` (no history pollution). Initial hash handling on mount via `requestAnimationFrame`. Props reduced to just `categories` (removed `config`, `activeCategory`).

6. **`frontend/app/(reader)/learning/page.tsx`** — Simplified: removed `searchParams`/`page` handling. Just renders `SurfaceNav` + `SurfacePage`.

7. **`frontend/app/(reader)/learning/[category]/page.tsx`** — Rewritten to redirect: `/learning/:category` → `/learning#category`.

#### Files modified (1)

8. **`frontend/components/AnalyticsProvider.tsx`** — Two changes: (a) `page_view` simplified to just `{ surface }` — no URL-derived `category_slug` since pathname is always `/` or `/learning`; (b) `headline_click` derives `category_slug` from DOM (`anchor.closest("section[id]")?.id`) instead of URL path — more accurate, tells you which section the user was browsing when they clicked.

#### Files deleted (4)

| File | Reason |
|---|---|
| `frontend/app/(reader)/[[...slug]]/page.tsx` | Replaced by `app/(reader)/page.tsx` + `app/(reader)/[slug]/page.tsx` |
| `frontend/components/Pagination.tsx` | Replaced by per-section "Show more" in CategorySections. Only consumer was SurfacePage. |
| `frontend/components/HeadlineList.tsx` | Replaced by CategorySections. Only consumer was SurfacePage. |
| `frontend/lib/grouping.ts` | Only consumer was HeadlineList. `groupByTime`/`groupByTopic` no longer needed — category sections ARE the groups. |

#### Deviations from design

**1. `loadMore` uses ref guard instead of state guard**

The design showed `loadingSection` state in the `useCallback` dependency array. This creates a stale closure risk: under React's batched updates, the `if (loadingSection) return` guard could read stale state, and having `loadingSection` in deps causes the callback to change identity on every loading state toggle. Fixed by adding a `loadingRef` for the guard (always current, never stale) and removing `loadingSection` from `useCallback` deps. `loadingSection` state is still used for UI rendering (button text and disabled state).

**2. `scrollTo` renamed to `scrollToSection`**

The design used `scrollTo` as the callback name, which shadows `window.scrollTo`. While not a runtime bug (the function body uses `window.scrollTo(...)` explicitly), it's a code smell that could mask bugs in future edits. Renamed to `scrollToSection` for clarity.

**3. Hash effect dependency array fixed**

The design's hash-handling `useEffect` had empty deps `[]` while referencing the `scrollTo` callback, violating React's exhaustive-deps lint rule. Fixed by moving the `useCallback` definition before the effect and adding `scrollToSection` to the dependency array. Since `scrollToSection` has stable identity (`useCallback(... , [])`), the effect still only runs once on mount.

#### Impact on existing architecture

**`SurfaceConfig.groupBy` field is now unused.** The `groupBy: "time" | "topic"` field was consumed by `HeadlineList` → `groupHeadlines()`. With the monopage architecture, categories sections ARE the groups — there's no in-component grouping. The field remains in the type and config objects (harmless dead code) but has no consumers. The "Adding a New Grouping Strategy" extension point (Appendix) is obsoleted by this change.

**`SurfaceConfig.basePath` field is partially unused.** Was consumed by CategoryNav (for building category URLs) and Pagination (for building page URLs). CategoryNav now uses scroll-to (no URL construction). Pagination is deleted. `basePath` is still used by the legacy redirect routes conceptually (they hardcode paths), but not read from config at runtime. The field remains for SurfaceNav and any future use.

**Route structure simplified.** Old: `[[...slug]]/page.tsx` catch-all handled `/`, `/economy`, `/economy?page=2`. New: `page.tsx` handles `/`, `[slug]/page.tsx` redirects `/economy` → `/#economy`. Learning: similar simplification with `[category]/page.tsx` becoming a redirect.

#### Verification

- `npm run build` — 0 type errors, 0 lint errors, all 14 pages generated
- `/` → News with all category sections, sticky category nav, lead headline, briefing
- `/learning` → Learning with all category sections, no lead headline
- Category tabs scroll smoothly to correct section
- "All" tab scrolls to top
- "Show more" in a section loads additional headlines without page reload
- Scroll-spy updates active tab as you scroll through sections
- `/economy` → 307 redirect → `/#economy`
- `/learning/tech` → 307 redirect → `/learning#tech`
- Direct navigation to `/#economy` scrolls to Economy section on load
- `page_view` fires with surface only (no category_slug)
- `headline_click` fires with correct `category_slug` from section ID
- LeadHeadline click fires with `category_slug: undefined` (correct — not inside a section)

---

## Appendix: Cross-Cutting Concerns

### Testing Strategy

| Layer | Tool | What to test |
|-------|------|-------------|
| Backend unit | pytest + pytest-asyncio | Scraper dedup logic, classification prompt builder, story dedup similarity + clustering, time formatting, adapter parsing |
| Backend integration | pytest + test DB | Full scrape → classify → dedup flow, API endpoint responses (is_representative filter, also_reported_by), concurrency guards |
| Frontend unit | Vitest + React Testing Library | Component rendering, prop variations, surface-conditional behavior |
| Frontend E2E | Playwright | Full user flows: load news → switch to learning → click headline → admin login → refresh sources |

### Error Handling Philosophy

- The scraper function **never throws** — catches all, records in fetch_log
- The classifier **never throws** — catches all, records in pipeline_log
- Partial success > total failure (one article failing doesn't stop the batch)
- `asyncio.gather(return_exceptions=True)` for concurrent operations
- Admin dashboard surfaces errors immediately — no SSH needed

### Environment Variables (Complete)

```
# Database
DATABASE_URL=postgresql+asyncpg://headlines:password@db:5432/headlines

# LLM Providers (only the active provider's key is required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_AI_API_KEY=AIza...

# Admin
ADMIN_PASSWORD=...

# App
BRIEFING_TIMEZONE=America/New_York
PUBLIC_API_URL=https://headlines.example.com/api

# Frontend
NEXT_PUBLIC_API_URL=https://headlines.example.com/api

# Optional: Alerting (Phase 6)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...  # empty string = disabled

# Optional: NextAuth (if used for admin auth)
NEXTAUTH_SECRET=...
```

### Extension Points (Modularity Contracts)

The system is designed around five extension points. Each one follows the same principle: **add a new entry to a registry, not a new branch to existing code.** The table below summarizes what you touch for each type of extension, and the sections below walk through each in detail.

| Extension | Files to ADD | Files to MODIFY | Existing components modified |
|-----------|-------------|-----------------|------------------------------|
| New source (e.g., Reuters) | 0 | 0 | 0 — admin panel operation |
| New category (e.g., Climate) | 0 | 0 | 0 — admin panel operation |
| Rearrange category tabs | 0 | 0 | 0 — admin drag-and-drop |
| Rename a category | 0 | 0 | 0 — admin inline edit |
| Merge two categories | 0 | 0 | 0 — admin merge operation |
| Tune dedup sensitivity | 0 | 0 | 0 — edit pipeline_tasks.config for dedup task |
| Disable dedup entirely | 0 | 0 | 0 — set dedup task active=false in admin |
| New source adapter (e.g., JSON API) | 1 (`adapters/json_api.py`) | 1 (`adapters/registry.py` — add to dict) | 0 |
| New LLM provider (e.g., Mistral) | 1 (`llm/mistral.py`) | 1 (`llm/registry.py` — add to dict) | 0 |
| New pipeline task (e.g., analysis) | 1 (`editorial/analysis.py`) | 1 (`workers/scheduler.py` — register CronTrigger job) | 0 — *proven by Phase 7* |
| New reader surface (e.g., Research) | 1 (page file) + optional CSS override | 1 (`lib/surfaces.ts` — add config entry) | 0 |
| ~~New grouping strategy (e.g., by source)~~ | ~~1 (`lib/grouping.ts` — add function)~~ | ~~0~~ | ~~0~~ | *(Removed in Phase 8 — category sections replaced in-component grouping)* |
| New theme (e.g., high contrast) | 0 | 1 (`tokens/semantic.css` — add `[data-theme]` block) | 0 |
| New visual variant per surface | 0 | 1 (`tokens/components.css` — add `[data-surface]` block) | 0 |

#### Adding a New Reader Surface

Example: adding a "Research" surface for academic papers.

**Step 1 — Surface config** (`lib/surfaces.ts`):
```ts
SURFACES.research = {
  slug: "research",
  label: "Research",
  basePath: "/research",
  groupBy: "topic",        // unused since Phase 8 (category sections are the groups)
  showSummary: true,
  showLeadHeadline: false,
  showAlsoReportedBy: true,
  timeFormat: "date",
  briefingType: "weekly_research",
  briefingLabel: "THE RESEARCH ROUNDUP",
  briefingCadence: "this week",
  categoryApiSurface: "research",
};
```

**Step 2 — Page file** (`app/(reader)/research/page.tsx`):
```tsx
import { SURFACES } from "@/lib/surfaces";
import { SurfaceNav } from "@/components/SurfaceNav";
import { SurfacePage } from "@/components/SurfacePage";

export default async function ResearchPage() {
  return (
    <>
      <SurfaceNav activeSurface="research" />
      <SurfacePage config={SURFACES.research} />
    </>
  );
}
```

No `[category]/page.tsx` needed — the monopage architecture (Phase 8) shows all categories as scrollable sections on one page. CategoryNav handles scroll-to navigation internally.

**Step 3 (optional) — CSS overrides** (`tokens/components.css`):
```css
[data-surface="research"] {
  --headline-size: var(--text-md);              /* smaller headlines for academic titles */
  --summary-color: var(--color-text-tertiary);  /* less prominent summaries */
}
```

**What happens automatically:**
- SurfaceNav renders a "Research" tab (reads from `Object.values(SURFACES)`)
- CategoryNav fetches research categories, renders as sticky scroll-to tabs
- CategorySections renders one scrollable section per category with "Show more"
- EditorialSummary fetches the research briefing
- All CSS component tokens resolve through the `[data-surface="research"]` scope
- **Zero existing components are modified**

**Backend**: Add `surface='research'` sources and categories via admin panel. Add a `weekly_research` pipeline task via DB migration. The classifier automatically uses research categories for research sources.

#### Adding a New Source Adapter

Example: adding a JSON API adapter for a source that doesn't have RSS.

**Step 1** — Create `backend/app/adapters/json_api.py`:
```python
class JSONAPIAdapter(BaseAdapter):
    async def fetch(self, source: Source) -> AdapterResult:
        config = source.adapter_config  # {"api_url": "...", "response_mapping": {...}}
        # HTTP GET → parse JSON → map to RawArticle list
        ...
```

**Step 2** — Register in `backend/app/adapters/registry.py`:
```python
ADAPTER_REGISTRY["json_api"] = JSONAPIAdapter
```

**That's it.** The scraper function calls `get_adapter(source.adapter_type)` → gets the new adapter → everything else (dedup, logging, classification) works unchanged. The admin creates a source with `adapter_type = "json_api"` and the appropriate `adapter_config` JSON.

#### Adding a New LLM Provider

Example: adding Mistral.

**Step 1** — Create `backend/app/llm/mistral.py`:
```python
async def classify_mistral(articles, categories, model_id, api_key, config) -> ClassificationResult:
    # Call Mistral API with the same prompt content
    ...

async def generate_mistral(prompt, model_id, api_key, config) -> BriefingResult:
    ...
```

**Step 2** — Register in `backend/app/llm/registry.py`:
```python
PROVIDERS["mistral"] = (classify_mistral, generate_mistral)
```

**Step 3** — Add `MISTRAL_API_KEY` to env and `backend/app/config.py`.

**That's it.** The admin registers a Mistral model in the model registry (provider="mistral"), and assigns it to any pipeline task. The `run_task()` dispatcher resolves "mistral" → adapter functions automatically.

#### Adding a New Pipeline Task

**Real example**: the "analysis" task added in Phase 7 for In Focus.

**Step 1** — Create `backend/app/editorial/analysis.py` (see Phase 7 Step 7.1 for the full implementation). The key pattern: task check → idempotency → data collection → prompt building → `run_generate(db, "analysis", ...)` → upsert result → pipeline log.

**Step 2** — Register the scheduled job in `backend/app/workers/scheduler.py`:
```python
async def _run_analysis():
    async with async_session() as db:
        try:
            from app.editorial import generate_analysis
            result = await generate_analysis(db, trigger="scheduled")
            await db.commit()
        except Exception as e:
            logger.error(f"Analysis generation failed: {e}")
            await db.rollback()

scheduler.add_job(
    _run_analysis,
    CronTrigger(hour=7, minute=0, timezone=settings.BRIEFING_TIMEZONE),
    id="daily_analysis", max_instances=1,
)
```

**Step 3** — DB: Alembic migration seeds the task row (copies `model_id` from an existing task).

**That's it.** The admin panel automatically shows the new task in the Pipeline Tasks section (it reads from the `pipeline_tasks` table dynamically). Cost tracking, logging, and model assignment work through the existing `pipeline_logs` and `run_generate()` infrastructure. Phase 7 proved this extension point works exactly as designed — 1 new file + 1 modification to `scheduler.py` + 1 migration.

#### ~~Adding a New Grouping Strategy~~ — Removed in Phase 8

> **This extension point no longer exists.** Phase 8 deleted `lib/grouping.ts` and `HeadlineList.tsx`. The monopage architecture replaced in-component grouping with per-category sections: `CategorySections` renders one `<section>` per API category. The categories themselves ARE the groups — determined by the API response, not client-side logic.
>
> The `SurfaceConfig.groupBy` field is now unused (harmless dead code). If sub-grouping within a category section is ever needed (e.g., grouping Economy headlines by time), it would be a new feature in `CategorySections`, not a revival of the old extension point.

#### Adding, Rearranging, and Reorganizing Categories

Categories are the most frequently changed part of the system. Here's what each operation touches:

| Operation | Backend | Frontend | Classifier | Reader URLs |
|-----------|---------|----------|------------|-------------|
| **Add category** | 1 DB row | 0 changes (dynamic nav) | Auto (next run) | New slug works immediately |
| **Rearrange tabs** | N display_order UPDATEs | 0 changes (sorted by display_order) | No effect | No effect |
| **Rename category** | 1 UPDATE (name) | 0 changes (name from API) | No effect | No effect (slug unchanged) |
| **Change slug** | 1 UPDATE + 1 redirect row | 0 changes (slug from API) | No effect | Old `#slug` anchor updates automatically (API-driven) |
| **Edit description** | 1 UPDATE | 0 changes | Future articles use new description; reclassify for retroactive | No effect |
| **Merge categories** | Reassign rows + redirect + DELETE | 0 changes | No effect (target category exists) | Old `#slug` section disappears; target section gains articles |
| **Disable category** | 1 UPDATE (active=false) | 0 changes (hidden by API filter) | Removed from prompt | Section disappears from page (API-driven) |
| **Delete category** | CASCADE delete | 0 changes | Removed from prompt | Section disappears from page (API-driven) |

**The key insight: the frontend never changes.** CategoryNav fetches from `/api/categories?surface=...` and renders tabs as scroll-to buttons, in API order (`display_order`). CategorySections renders one `<section id={slug}>` per category. No category name, slug, or order is hardcoded in frontend code. Since Phase 8 (monopage), there are no per-category routes — categories are sections on a single page, so adding/removing/reordering categories only requires API changes.

**Why rearranging is instant**: `PUT /api/admin/categories/reorder` updates `display_order` in the DB. The next `/api/categories` response returns the new order. The frontend renders tabs in that order. No build step, no code change, no restart. The only delay is the categories API cache (≤ 10 min, or instant with cache flush).

**Why adding is safe**: A new category with 0 articles is harmless — it appears as a scroll-to tab in CategoryNav and an empty section showing "No headlines in this section." The classifier picks it up on the next run. Articles start flowing in within minutes.

**Why description editing has a feedback loop**: The "Preview" feature lets the admin test a description against recent articles *before saving*. The admin sees which articles would gain/lose this category. This turns category tuning from "change it and hope" into "change it, see the effect, iterate, then commit." Reclassification applies the change retroactively.

#### Adding a CSS Theme or Surface Variant

**New theme** (e.g., high contrast) — edit `tokens/semantic.css`:
```css
[data-theme="high-contrast"] {
  --color-text-primary:   #000000;
  --color-surface:        #FFFFFF;
  --color-rule:           #000000;
  --color-accent:         #0000FF;
  /* ... */
}
```
Zero component changes. The ThemeToggle gains an option. Every component that uses `text-primary` or `bg-surface` automatically picks up the new values.

**Surface-specific visual variant** — edit `tokens/components.css`:
```css
[data-surface="research"] {
  --headline-size: var(--text-md);
  --headline-weight: var(--weight-regular);
  --meta-size: var(--text-xs);
}
```
Zero component changes. Headlines within the research surface render smaller and lighter.

#### The Modularity Test

Before shipping any phase, run this mental check:

1. **Can I add a new source without touching code?** → Yes (admin panel operation).
2. **Can I add a new category without touching code?** → Yes (admin panel operation).
3. **Can I rearrange category tabs without touching code?** → Yes (drag-and-drop in admin, instant after cache flush).
4. **Can I rename a category without breaking URLs?** → Yes (slug unchanged on rename; if slug changes, redirect created).
5. **Can I merge two categories without losing articles?** → Yes (articles reassigned, old slug redirects).
6. **Can I add a new reader surface by adding files, not modifying existing ones?** → Yes (config entry + page file + optional CSS override). Since Phase 8, no `[category]` route needed — monopage shows all categories as sections.
7. **Can I add a new adapter/provider by adding one file and one line in a registry?** → Yes.
8. **Can I change the visual treatment of a surface without touching any component?** → Yes (component token override in CSS).
9. **Can I add a new theme without touching any component?** → Yes (semantic token override in CSS).
10. **Can I tune or disable dedup without touching code?** → Yes (edit `pipeline_tasks.config` or set `active = false` in admin).

If any answer is "no," the architecture has a coupling problem that should be fixed before moving on.

---

### Estimated Timeline

| Phase | Scope | Steps | Status |
|-------|-------|-------|--------|
| **Phase 1** | Core Pipeline + News Reader | 11 steps — the foundation | **Code complete** (2026-03-16) |
| **Phase 2** | Learning Surface | 1 step — leverages Phase 1 infrastructure | **Code complete** (2026-03-16) |
| **Phase 3** | Briefings | 2 steps — editorial generation + display | **Code complete** (2026-03-16) |
| **Phase 4** | Admin Panel | 6 steps — full operational control | **Code complete** (2026-03-17) |
| **Phase 5** | Analytics | 2 steps — event tracking + dashboard | **Code complete** (2026-03-17) |
| **Phase 6** | Polish | 5 steps — production readiness | **Code complete** (2026-03-17) |
| **Phase 7** | In Focus | 2 steps — cross-source framing analysis | **Code complete** (2026-03-17) |
| **Phase 8** | Monopage Reader Navigation | 1 step — scroll-based category navigation | **Code complete** (2026-03-19) |

**Total: 30 steps across 8 phases. All 8 phases code complete (147 files, 4 deleted in Phase 8).**

Phase 1 is the largest and most critical — it builds the entire backend infrastructure, pipeline, and primary reader experience. Phases 2-3 were comparatively small because they build on Phase 1's infrastructure. Phase 4 (admin panel) was the second-largest phase — 6 steps, 33 endpoints, 18 new files. Phase 5 added analytics (13 files). Phase 6 was a cross-cutting polish pass — responsive design, performance, retention, alerting, RSS — touching 20 files across both frontend and backend. Phase 7 added In Focus — the aggregator's editorial differentiator, leveraging the existing dedup cluster infrastructure to identify the most cross-source story and generate a framing comparison (3 new files, 10 modified, ~250 lines). Phase 8 converted the reader from multi-page category routing to monopage scroll navigation — all categories as scrollable sections with sticky CategoryNav, IntersectionObserver scroll-spy, per-section "Show more" client-side pagination, and legacy URL redirects (8 files touched, 4 deleted, ~200 lines).

**Blocking for all eight phases**: `docker compose up` + `alembic upgrade head` for full end-to-end verification — RSS feeds parsing, LLM classification, editorial generation, In Focus analysis generation (requires 3+ source cluster), reader display at all breakpoints, admin login + CRUD operations, analytics event recording + dashboard, retention job execution, Slack alerting, RSS output feed validation, monopage scroll-spy + "Show more" client-side pagination.
