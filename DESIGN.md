# Headlines — Design Document

**A curated headlines and learning aggregator for high-agency readers of the FT, Bloomberg, WSJ, The Verge, Stratechery, Harvard Business Review, and MIT Sloan Management Review.**

---

## 1. Product Vision

**Headlines is where high-agency people get their news and learning from high-quality sources.**

The target reader — a founder, investor, operator, engineer — already subscribes to the Financial Times, Bloomberg, the Wall Street Journal, The Verge, and Stratechery for news. They read Harvard Business Review and MIT Sloan Management Review for management insight and strategic thinking. They chose these publications because editorial quality directly informs decision quality. Information, for them, is not entertainment. It is leverage.

But reading across seven premium publications daily is friction. News stories overlap, important pieces get buried under volume, and context-switching between apps compounds into hours over weeks. Management insights get bookmarked and forgotten. These readers don't need more sources. They need a better interface to the sources they already trust.

**Headlines is that interface.** Two surfaces — **News** and **Learning** — each curated from publications that matter, classified into categories that make sense, presented with the typographic seriousness the content deserves. Click a headline, read the article on the original site. Nothing else.

The News surface aggregates time-sensitive headlines from FT, Bloomberg, WSJ, The Verge, and Stratechery. The Learning surface aggregates enduring insights from HBR and MIT Sloan Management Review — strategy, leadership, innovation, and management thinking that stays relevant for weeks or months. Same design language, different temporal treatment. News is organized by recency; Learning is organized by topic.

### Principles

1. **Source quality is the product.** We don't aggregate the internet — we curate from publications with editorial standards worth paying for. The sources are chosen, not crawled. News sources for current events; learning sources for enduring management insight.

2. **Respect the reader's time and intelligence.** No clickbait, no infinite scroll, no algorithmic feed, no "recommended for you." Every headline earns its place. The reader scans in minutes what would otherwise take an hour.

3. **Curation through structure.** A human (the admin) chooses the sources and defines the categories. An LLM does the sorting. Human editorial judgment plus machine classification produces a feed that feels curated without constant manual work.

4. **Extensibility without code changes.** Adding a new source or category is an admin panel operation, not a deployment. Pluggable adapters and LLM-driven classification adapt automatically to new categories.

5. **Stay out of the way.** Headlines is a lens, not a destination. No accounts, no comments, no likes, no social features on the reader side. The product is the reading experience — and the reading happens on the original site.

---

## 2. Three Surfaces

### 2.1 Reader Site (public)

The primary product. What visitors see. Two content surfaces — **News** and **Learning** — under one roof, sharing the same visual language but with content treatment tailored to each.

**Core experience:**
- Two top-level surfaces: **News** (default) and **Learning** — selectable via top-level tabs beneath the masthead
- **News**: A clean page of headlines from news sources, grouped by time and filtered by news categories
- **Learning**: A page of management/strategy articles from HBR and MIT SMR, grouped by topic and filtered by learning categories
- Each headline shows: title, source name, time metadata (relative for news, date for learning), and optionally an "Also in:" line listing other sources that covered the same story
- Click any headline → opens original article on the source's site (new tab)
- Filter by category via tabs within each surface
- No login, no paywall, no cookies beyond minimal analytics

**Editorial Summaries — the first thing you see on each surface:**

Above the headlines on the **News** surface, an LLM-generated editorial section appears each day:

**The Brief** — A 3-5 sentence thematic summary of today's news headlines. Not article-by-article recap, but *orientation*: what themes dominate, which stories are getting cross-source coverage, what's breaking. Think of it as the forest before the trees — the reader knows where to focus before scanning individual headlines.

Above the articles on the **Learning** surface, a weekly editorial section appears:

**The Learning Digest** — A 3-5 sentence thematic summary of the week's management articles from HBR and MIT SMR. What strategic questions are being debated? What research findings matter for practitioners? What themes are both publications converging on? Generated once per week (Monday morning).

> **Deferred: In Focus.** A cross-source synthesis feature (identifying the top story and comparing how each publication frames it) is planned for a future phase. It requires stronger editorial prompting and quality validation before shipping. The Brief ships first — In Focus follows once the pipeline and reader experience are proven.

Both summaries are clearly labeled as AI-generated. They're signposts, not replacements — always pointing back to the original source articles. The admin can toggle each on/off independently via pipeline task settings.

**Visual identity — "the morning briefing you'd design for yourself":**

The reader site should feel like opening a beautifully typeset morning edition — quiet confidence, zero clutter, effortless scanning. Think: if the FT's digital edition and a perfectly set broadsheet had a child, and that child only cared about headlines. The design earns trust through typography and restraint, not through decoration.

**Design Principles:**

1. **Typography carries everything.** With no images, no thumbnails, no avatars — the typeface, its weight, its size, and its spacing ARE the design. Every pixel of hierarchy is typographic.
2. **Quiet authority.** The palette is muted, the layout is structured, the whitespace is generous. Nothing competes for attention. The content speaks.
3. **Editorial, not app-like.** This is a page you *read*, not a dashboard you *interact with*. No cards with shadows, no rounded corners on content blocks, no hover animations. Thin rules, clear sections, classical structure.
4. **Density with breathing room.** Premium doesn't mean sparse — it means *organized density*. A well-set column of headlines can be both information-rich and elegant.

#### Typography

| Role | Font | Fallback | Weight | Notes |
|------|------|----------|--------|-------|
| **Headlines** | `GT Sectra` or `Freight Text Pro` | `Georgia, 'Times New Roman', serif` | 500 (medium) for standard, 600 (semibold) for lead | Serif headlines signal editorial seriousness. The slight contrast between thick/thin strokes gives character without being decorative. |
| **Navigation / Labels** | `Inter` or `Söhne` | `system-ui, -apple-system, sans-serif` | 400 regular, 500 medium for active state | Clean, neutral sans-serif that doesn't compete with headline serifs. |
| **Metadata** (source, time) | Same sans-serif | — | 400, slightly smaller, muted color | Should be readable but recede. The headline is the star; metadata is supporting cast. |
| **Masthead** | Same serif as headlines | — | 400, letterspaced | Understated. Not shouting — just clearly the nameplate. |

**Type scale:**

| Element | Desktop | Mobile |
|---------|---------|--------|
| Lead headline | 26px / 1.25 line-height | 22px / 1.25 |
| Standard headline | 18px / 1.35 | 17px / 1.35 |
| Source + time | 13px / 1.4 | 12px / 1.4 |
| Category nav | 14px / 1.0, letterspaced 0.03em, uppercase | 13px |
| Section header ("Today", "Yesterday") | 12px / 1.0, uppercase, letterspaced 0.08em | Same |

**Why serif headlines?** Every premium financial publication uses serifs for headlines — FT (Financier Display), Bloomberg (proprietary), WSJ (Escrow), The Economist (Econ Sans is the exception, but they use Milo Serif for body). Serifs say "journalism" before the reader processes a single word.

#### Color Palette

**Light mode (default):**

| Element | Color | Hex |
|---------|-------|-----|
| Background | Warm off-white (not pure white — pure white is clinical) | `#FAF9F7` |
| Text — headlines | Near-black | `#1A1A1A` |
| Text — metadata | Warm gray | `#6B6560` |
| Text — source name | Slightly darker than metadata | `#4A4540` |
| Rules / dividers | Subtle warm gray, 1px | `#E5E0DB` |
| Category nav — inactive | Warm gray | `#8A8580` |
| Category nav — active | Near-black + underline | `#1A1A1A` |
| Accent | Deep ink blue (for links, active states, hover) | `#1A3A5C` |
| Masthead | Near-black | `#1A1A1A` |
| Footer | Muted | `#8A8580` on `#FAF9F7` |

**Dark mode:**

| Element | Color | Hex |
|---------|-------|-----|
| Background | Deep warm charcoal (not pure black) | `#1C1B19` |
| Text — headlines | Warm white | `#EDECE8` |
| Text — metadata | Warm gray | `#9A9590` |
| Rules / dividers | Subtle | `#2E2D2A` |
| Accent | Muted blue | `#6B9FD4` |

**Why warm tones?** Pure whites and pure blacks feel digital and sterile. Warm off-whites and charcoals feel *printed* — like paper, like ink. This is the single cheapest trick to making a text-heavy page feel premium. The FT's entire brand rests on `#FFF1E5`.

#### Layout — Editorial Grid

Not a flat list. A structured editorial page with visual hierarchy.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   Headlines                                              March 10, 2026 │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   News    Learning                                                      │
│   ────                                                                  │
│                                                                         │
│   All    Economy    Markets    Tech    Politics    US    Europe    World │
│          ───────                                                        │
│                                                                         │
│   THE BRIEF                                                             │
│   Markets are digesting a hawkish Fed signal alongside soft UK          │
│   inflation, creating a divergence trade. In tech, Meta's layoffs       │
│   contrast with NVIDIA's AI infrastructure dominance — two strategies,  │
│   two very different outcomes.                                          │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   TODAY                                                                 │
│                                                                         │
│   Nvidia surpasses $4T market cap as AI                                 │
│   infrastructure spending accelerates                                   │
│   Bloomberg · 2h                                                        │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   Fed signals rate pause through Q2             UK inflation drops to   │
│   amid sticky CPI data                         2.1%, below BoE target  │
│   The Wall Street Journal · 3h                  Financial Times · 5h    │
│   Also in: Bloomberg, Financial Times                                   │
│                                                                         │
│   OpenAI valued at $350B in latest              Apple Vision Pro 2:     │
│   funding round                                everything announced     │
│   Bloomberg · 6h                                The Verge · 4h          │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   EU reaches provisional deal on AI             Senate confirms new     │
│   liability framework after marathon            Treasury secretary in   │
│   negotiations in Brussels                      narrow bipartisan vote  │
│   Financial Times · 7h                          The Wall Street Jrnl · 8h│
│                                                                         │
│   Meta announces 15,000 layoffs in              The AI infrastructure   │
│   second restructuring this year                thesis: why NVIDIA's    │
│   The Verge · 8h                                moat keeps widening     │
│                                                 Stratechery · 10h       │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   YESTERDAY                                                             │
│                                                                         │
│   China's manufacturing PMI contracts            ...                    │
│   for third consecutive month                                           │
│   Bloomberg · 18h                                                       │
│   ...                                                                   │
│                                                                         │
│                          More headlines                                  │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│   Financial Times · Bloomberg · WSJ · The Verge · Stratechery           │
│   Harvard Business Review · MIT Sloan Management Review                 │
│   headlines.example.com                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Layout mechanics:**

- **Lead headline**: The most recent headline renders at larger type (26px), full-width, with more vertical space. It anchors the page. Only one — the latest chronologically, or optionally the admin can pin one.
- **Two-column grid** (desktop, ≥768px): After the lead, headlines flow into a two-column grid. Each cell is a headline + source + time. No borders, no cards — just two columns of well-set text separated by generous gutter space and thin horizontal rules between rows.
- **Single column** (mobile, <768px): Everything stacks. Lead headline is still slightly larger than the rest, but the gap is smaller.
- **Time sections**: "TODAY" and "YESTERDAY" as uppercase, letterspaced, small-caps section dividers with a thin rule beneath. These break up the chronological flow and give the eye anchoring points. If all headlines are from today, the section header is omitted — no empty sections.
- **No bullets, no icons**: The headline IS the element. No `●`, no `▶`, no decorative markers. Hierarchy comes from type size, weight, and position.
- **Thin horizontal rules**: 1px lines in the divider color (`#E5E0DB`) separate logical groups. This is the classical newspaper device — rules organize without adding visual weight.

#### Surface & Category Navigation

**Two-level navigation:**

1. **Surface tabs** — directly beneath the masthead: `News  Learning`. These switch the entire content surface. Active surface: near-black text + 2px underline. Inactive: warm gray. Same serif font as the masthead, at nav size. This is a top-level switch, visually weightier than category tabs.
2. **Category tabs** — beneath the surface tabs: the category set changes per surface. News shows `ALL  ECONOMY  MARKETS  TECH  POLITICS  US  EUROPE  WORLD  BUSINESS  OPINION`. Learning shows `ALL  STRATEGY  LEADERSHIP  INNOVATION  TECHNOLOGY & AI  OPERATIONS  PEOPLE & CULTURE  ENTREPRENEURSHIP`.

**Category tab styling** (same for both surfaces):

- Uppercase, letterspaced sans-serif
- Active category: near-black text + 2px underline offset beneath the text (not a full-width bar — just under the word)
- Inactive: warm gray text, no underline
- On hover (desktop): smooth transition to near-black
- On mobile: horizontally scrollable if categories overflow, with subtle fade gradient on the right edge to hint at more
- No background colors, no pills, no borders around tabs — just text and an underline. Maximum restraint.

#### Headline Item Anatomy

Each headline (non-lead) is:

```
Fed signals rate pause through Q2 amid sticky CPI      ← headline text (serif, 18px, near-black)
The Wall Street Journal · 3h                             ← source · relative time (sans, 13px, muted)
```

That's it. Two lines. No summary, no image, no category tag, no "read more" link. The entire block is the click target (cursor: pointer on hover, headline color shifts to accent blue on hover — single, clean affordance).

**Lead headline** is the same anatomy but:
- Serif at 26px, semibold weight
- Source/time at 14px
- Full-width (spans both columns on desktop)
- Slightly more vertical padding above and below
- Separated from the grid by a thin rule

**Source formatting**: Full publication name, not abbreviations. "Financial Times" not "FT". "The Wall Street Journal" not "WSJ". The formality is part of the premium feel. Exception: if the source name would cause awkward wrapping on mobile, the `source.name` can include a shorter display variant.

**Time formatting**: Compact relative time. "2h" not "2 hours ago". "3d" not "3 days ago". "Mar 2" for anything older than 7 days. The brevity matches the headline-scanning cadence — your eye should not linger on metadata.

#### Micro-details That Create the Premium Feel

- **Proper punctuation**: Curly quotes (" "), em-dashes (—), not straight quotes or hyphens. Server-side typography processing with a library like `smartypants`.
- **No favicon/logo next to sources**: Text only. Favicons are low-resolution, visually inconsistent across sources, and add noise. The source name in clean sans-serif is more elegant.
- **"More headlines" button** (not "Load more"): Phrased as a noun, not a command. Centered, small sans-serif, with a thin horizontal rule above it. No button styling — just text, like a quiet invitation. On hover, text color transitions to accent blue.
- **Footer**: Minimal. Source names separated by middots (`·`), the site domain, nothing else. Same muted gray as metadata. No "About" link unless there's a real about page. No social links. The footer is a colophon, not a navigation.
- **Page top**: "Headlines" as the masthead, left-aligned, in the headline serif at medium weight. Not letterspaced to extremes, not all-caps — just "Headlines" with understated confidence. Date on the right side: "March 10, 2026" in muted sans-serif. The date signals "this is today's edition" — a newspaper convention.
- **Scroll position**: On page load, the viewport should start at the lead headline, not at the masthead. The masthead is present but not the hero — the content is.
- **Link behavior**: All headline clicks open in a new tab (`target="_blank"` with `rel="noopener"`). The reader stays on Headlines; the article opens alongside. No interstitials, no "you're leaving" warnings.
- **Selection color**: When text is selected, the highlight color should match the accent (a tinted version of the ink blue) rather than the default system blue.

#### Responsive Behavior

| Breakpoint | Layout | Notes |
|------------|--------|-------|
| ≥1200px | Centered content column (max 840px), two-column grid | Generous side margins. The content doesn't stretch to fill a widescreen monitor — it stays at a comfortable reading width. |
| 768–1199px | Same centered column (max 720px), two-column grid | Slightly narrower. |
| <768px | Full-width with 20px side padding, single column | Lead headline still slightly larger. Category nav becomes horizontally scrollable. |

**Max content width: 840px.** This is a *reading* width, not a dashboard width. The FT's article column is ~680px. Bloomberg's is ~720px. Going wider makes headline scanning harder because the eye has to travel too far. 840px accommodates two columns of shorter headlines comfortably.

#### What This Is NOT

- **Not a dashboard.** No cards with shadows, no rounded rectangles, no grid of equal-sized boxes. That's SaaS, not editorial.
- **Not brutalist / minimalist-chic.** This isn't a portfolio site. It's a utility — but a utility with taste.
- **Not a clone of any single publication.** It should feel *of the same world* as the FT, Bloomberg, WSJ, Stratechery, HBR, and MIT SMR — but not copy any one of them. It has its own voice: a quiet aggregator that respects the reader's intelligence and time.

**Key UX decisions:**

- **Time-grouped sections (News surface)**: Headlines are sorted by `published_at DESC` and grouped into "Today" and "Yesterday" sections. Section headers are uppercase, letterspaced, small-type dividers — a newspaper convention for temporal anchoring. If all headlines fall within "Today", no header is shown. The Learning surface uses topic-grouped sections instead — see the Learning Surface section below.
- **No infinite scroll**: Paginated with a "More headlines" text link. Infinite scroll encourages mindless consumption; a deliberate load action respects the reader's attention.
- **No source favicons**: Text-only source attribution. Favicons are low-resolution and visually noisy. The source name in clean sans-serif is more premium.
- **No images in the headline list**: Headlines only. Images slow scanning and add visual noise. The reader is here for headlines, not thumbnails. The typography must be strong enough to carry the page alone.
- **Mobile-first**: Single column on mobile, two-column grid on desktop. The content is text — it should be fast and readable on any device, with comfortable reading width capped at 840px.
- **Server-rendered core reading**: The headline list is fully server-rendered — the page displays correctly before any client-side JavaScript executes. Next.js does ship a hydration bundle, but the core reading experience (headline display, category navigation via links, pagination) does not depend on it. Analytics and progressive enhancements (theme toggle, admin interactivity) use client-side JS.
- **Warm color palette**: Off-white backgrounds and warm grays instead of pure white/black. This single choice makes the page feel *printed* rather than *digital* — the foundation of premium perception.

#### Learning Surface

The Learning tab is the second content surface. Where News serves time-sensitive headlines organized by recency, Learning serves enduring management insights organized by topic.

**Sources**: Harvard Business Review and MIT Sloan Management Review. Both publish research-backed articles on strategy, leadership, innovation, technology, and management — content that remains valuable for weeks or months.

**Why a separate surface, not just more categories?** HBR and MIT SMR content is fundamentally different from news:

| Dimension | News | Learning |
|-----------|------|----------|
| **Time sensitivity** | Hours — stale by tomorrow | Weeks/months — an HBR piece on "Leading Through Uncertainty" is relevant for a year |
| **Temporal grouping** | "Today" / "Yesterday" | By topic — time grouping is meaningless for evergreen content |
| **Time display** | Relative ("2h", "3d") | Publication date ("Mar 12, 2026") |
| **Summaries** | Hidden — the headline is enough | Shown — management articles benefit from the subtitle/description to help decide whether to click |
| **Publishing cadence** | 50-100+ articles/day across 5 sources | 5-15 articles/week across 2 sources |
| **Briefing cadence** | Daily (The Brief) | Weekly (The Learning Digest) |
| **Category taxonomy** | News beats (Economy, Markets, Tech, Politics...) | Management disciplines (Strategy, Leadership, Innovation...) |

Mixing these into a single feed would create a jarring experience — a Bloomberg piece on "Fed Raises Rates" next to an HBR piece on "Why Your Strategy Process Needs a Redesign." They serve different reading modes: scanning vs. deliberate selection.

**Layout — Topic-Organized Reading:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   Headlines                                              March 16, 2026 │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   News    Learning                                                      │
│           ────────                                                      │
│                                                                         │
│   All    Strategy    Leadership    Innovation    Technology & AI         │
│          ────────                                                       │
│                                                                         │
│   THE LEARNING DIGEST                                                   │
│   This week's management thinking centers on AI integration              │
│   strategy — both HBR and MIT SMR published pieces arguing that         │
│   organizational readiness, not model capability, is the binding         │
│   constraint. Leadership and change management emerge as the            │
│   underrated bottleneck.                                                │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   STRATEGY                                                              │
│                                                                         │
│   Why Your AI Strategy Needs an Organizational                          │
│   Redesign — Not Just a Technology Upgrade                              │
│   Most companies treat AI adoption as a technology problem.             │
│   The real constraint is organizational design.                          │
│   Harvard Business Review · Mar 14, 2026                                │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   The Strategic Implications of                 How Platform Companies   │
│   Vertical Integration in AI                    Are Rethinking Their     │
│   MIT Sloan Management Review · Mar 12          Competitive Moats       │
│                                                 HBR · Mar 10, 2026      │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   LEADERSHIP                                                            │
│                                                                         │
│   Leading Through the Productivity Paradox:                             │
│   When More AI Doesn't Mean More Output                                 │
│   Research from 200 firms shows that AI productivity gains              │
│   plateau without corresponding management practice changes.            │
│   MIT Sloan Management Review · Mar 13, 2026                            │
│   ...                                                                   │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│   Harvard Business Review · MIT Sloan Management Review                 │
│   headlines.example.com                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key differences from the News layout:**

- **Topic grouping, not time grouping**: Articles are grouped under their primary learning category (Strategy, Leadership, Innovation, etc.) with the category name as a section header — the same uppercase, letterspaced style as "TODAY"/"YESTERDAY" on the News surface. Within each topic group, articles are sorted by `published_at DESC`.
- **Summaries shown**: Each article displays the title *and* a 1-2 sentence summary/description beneath it (from the RSS feed's `description` field). Management articles have descriptive titles but often benefit from the subtitle to convey the key insight. Summaries render in the same sans-serif as metadata, slightly larger than timestamps, in secondary text color.
- **Publication date, not relative time**: "Mar 14, 2026" instead of "2h". Relative time implies urgency; dates imply permanence. Learning content should feel like a library shelf, not a news ticker.
- **No lead headline**: All articles are visually equal weight. Learning content doesn't have a "breaking" piece that deserves 26px. All titles render at the standard headline size (18px).
- **Same two-column grid** (desktop): The grid structure carries over from News. Two columns of headline + summary pairs, separated by rules.
- **"All" shows all learning articles** in reverse chronological order (not grouped by topic). Topic-filtered views show only that topic.

**Learning category navigation**: Same horizontal tab bar as News, but with learning categories:

`ALL  STRATEGY  LEADERSHIP  INNOVATION  TECHNOLOGY & AI  OPERATIONS  PEOPLE & CULTURE  ENTREPRENEURSHIP`

Same styling: uppercase, letterspaced, underline on active. Same scrollable behavior on mobile.

**Weekly Learning Digest — the learning equivalent of The Brief:**

Above the topic-grouped articles, a weekly editorial summary appears:

**The Learning Digest** — A 3-5 sentence thematic summary of the week's management articles. What themes are HBR and MIT SMR converging on? What strategic questions are being debated? What research findings matter for practitioners? Generated once per week (default: Monday 7:00 AM), covering the previous 7 days of learning content.

The Learning Digest is clearly labeled as AI-generated. Like The Brief, it's a signpost pointing back to the original articles.

**URL structure:**

| URL | Content |
|-----|---------|
| `/` | News surface, all categories |
| `/economy` | News surface, Economy category |
| `/learning` | Learning surface, all categories |
| `/learning/strategy` | Learning surface, Strategy category |

### 2.2 Admin Panel (authenticated)

For the operator to manage sources, categories, and monitor system health.

**Sections:**

#### Sources Management
- **Global "Refresh All" button** in the page header — triggers batch fetch of all active sources with real-time progress panel (see Section 4.1.1)
- Table of all sources with: name, status (ok/error/running), last fetch time, new articles last fetch, **fetch interval** (inline dropdown), consecutive failures, actions
- **Fetch interval dropdown**: Each source shows its current interval with an inline dropdown ([▼]) directly in the table row. Presets: 5m, 15m, 30m, 1h, 2h, 6h, 12h, 24h. Change takes effect on the next scheduler cycle — no restart, no deploy. Same interaction pattern as the pipeline task model dropdown. Minimum 5 minutes (server-validated).
- Per-source action buttons:
  - **"Refresh"**: fetch this source now (trigger=manual), inserts articles, triggers classification
  - **"Test Fetch"**: dry run — shows what articles the adapter finds without inserting them
  - **"Edit"**: modify source config (name, feed URL, adapter type, fetch interval, adapter config)
  - **"Disable/Enable"**: toggle active status
- Add source: name, homepage URL, feed URL, surface (dropdown: News / Learning), adapter type (dropdown), fetch interval (dropdown, default 15m for news / 360m for learning), adapter config (JSON editor)
- Fetch history log per source: expandable row showing last N fetch_logs with timestamps, article counts, status, errors
- Sources with `consecutive_failures >= 5` highlighted in red with error message visible

#### Categories Management

**The admin's most important editorial tool.** Categories define what the reader sees in the navigation tabs, how articles are organized, and what the LLM classifies into. Rearranging, adding, renaming, and removing categories must be fast, safe, and immediately visible.

**Category list view:**
- Grouped by surface (News categories / Learning categories), each group independently orderable
- Drag-to-reorder within each surface group — order determines display order in the reader's category tabs
- Each category row shows: name, slug, description (truncated), article count (last 7 days), active toggle
- "Surface" indicator (News / Learning) per category — not editable after creation (prevents accidentally moving a news category to learning)

**Per-category operations:**
- **Edit**: name, slug (with redirect warning), description, active toggle
- **"Description"** is the most important field — it tells the LLM what belongs in this category. Changing it changes classification behavior for future articles.
- **"Preview"** button: takes the last 50 classified articles from the category's surface, runs classification with the current (possibly edited, unsaved) description, shows what would be assigned to this category vs. what's currently assigned. This is the feedback loop for tuning — the admin can iterate on the description and re-preview before saving.
- **"Reclassify"** button (per category): after saving a changed description, reclassify recent articles (last 24h or 7d) using the new description. This is a background job with a progress indicator — not a blocking operation. Only clears non-manual classifications.
- **Disable**: sets `active = false`. Category disappears from reader navigation and classification prompt. Existing article_categories rows are preserved — re-enabling restores them. This is the safe way to remove a category without losing data.
- **Delete**: permanently removes the category, cascades article_categories rows. Articles that only had this category become effectively uncategorized (they'll be reclassified on the next run if still within the retention window). Admin sees a confirmation dialog showing how many articles will be affected.
- **Merge**: select a target category → all article_categories from the source are reassigned to the target (deduplicating where an article already has both) → old slug added to `category_redirects` → source category deleted. This is how you consolidate: "merge Marketing & Growth into Strategy."

**Adding a new category:**
- Click "Add Category" → form with: name (required), slug (auto-generated from name, editable), surface (dropdown, required), description (required, textarea with guidance text: "Describe what kind of articles belong here. This text is sent directly to the LLM.")
- Slug auto-generates as the admin types the name (debounced, lowercased, hyphens for spaces). Admin can override the slug before first save. After save, the slug can still be changed but creates a redirect.
- Display order: new categories are appended to the end. Admin can drag to desired position immediately.
- "Preview" available before first save — the admin can test the description against recent articles before committing.
- After save: category appears in the reader's nav tabs within the next API cache cycle (≤ 10 minutes, or immediately after the admin clicks "Flush Reader Cache" — a convenience button that invalidates the categories cache).

**Rearranging categories:**
- Drag-and-drop reorder within each surface group
- Drop triggers `PUT /api/admin/categories/reorder` — updates `display_order` for all affected rows in one request
- Reader site reflects new order on the next categories API call (≤ 10 minutes cache, or instant with cache flush)
- No reclassification needed — ordering is purely a display concern

**Batch operations:**
- "Reclassify All" button per surface: reclassify all articles from the last 24h or 7d against the current category set. Useful after adding/removing multiple categories or substantially changing descriptions.
- Reclassification is a background job — the admin sees progress (articles processed / total) and can continue using the admin panel while it runs.

#### Articles Management
- Searchable, sortable table of all articles
- Columns: title, source, categories (with confidence), published_at, clicks
- Filter by: source, category, date range, classified/unclassified
- Actions: manually assign/remove categories, hide article (remove from reader), flag for review
- Bulk actions: select multiple → assign category, hide, reclassify

#### LLM Models & Pipeline Tasks
- **Model Registry**: Table of all registered models: provider, model ID, display name, pricing (input/output per MTok), active status
- **"Test"** button per model: sends a 3-article sample classification to verify API key + model responds correctly. Shows response time, token usage, and parsed result
- **"Add Model"** form: provider (dropdown: Anthropic / OpenAI / Google), model ID string, display name, input/output pricing
- **"Disable/Enable"** per model: disabled models can't be assigned to a task. Useful for sunsetting deprecated models
- **API key status** per provider: shows whether the environment variable is configured and validates with a lightweight API call. Keys live in env vars (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY`) — never stored in the database
- **Pipeline Tasks**: Below the model table, a section showing each pipeline task (classification, dedup, briefing, learning_digest) with its assigned model, active toggle, and description. The admin assigns any active model to any task — different tasks can use different models
- **Cost breakdown by task**: shows estimated daily/monthly cost per task based on recent volume from `pipeline_logs`, plus total pipeline cost
- **Recent usage**: last 10 LLM runs grouped by task, showing which model was used, tokens consumed, cost — pulled from `pipeline_logs`

```
┌──────────────────────────────────────────────────────────────────┐
│  LLM Models & Pipeline Tasks                                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Model Registry                                                  │
│  ──────────────                                                  │
│  Provider    Model                Input/MTok  Output/MTok Status │
│  ─────────   ─────                ──────────  ─────────── ────── │
│  Anthropic   Claude Haiku 4.5       $1.00       $5.00   ✓ Active │
│  Anthropic   Claude Sonnet 4.6      $3.00      $15.00   ✓ Active │
│  OpenAI      GPT-5 Mini             $0.25       $2.00   ✓ Active │
│  OpenAI      GPT-5 Nano             $0.05       $0.40   ✓ Active │
│  Google      Gemini 2.5 Flash       $0.30       $2.50   ✓ Active │
│  Google      Gemini 2.5 Flash-Lite  $0.10       $0.40   ✓ Active │
│                                                                  │
│  [Add Model]                                  [Test All Keys]    │
│                                                                  │
│  Pipeline Tasks                                                  │
│  ──────────────                                                  │
│  Task              Model               Active   Est. Cost        │
│  ───────────────   ─────               ──────   ─────────        │
│  Classification    Claude Haiku 4.5  [▼] ✓     ~$1.50/mo        │
│  Dedup             Claude Haiku 4.5  [▼] ✓     ~$0.30/mo        │
│  Briefing          Claude Sonnet 4.6 [▼] ✓     ~$0.90/mo        │
│  Learning Digest   Claude Sonnet 4.6 [▼] ✓     ~$0.05/mo        │
│                                        Total:  ~$2.82/mo         │
│                                                                  │
│  API Keys                                                        │
│  ─────────                                                       │
│  ANTHROPIC_API_KEY   ····sk-ant-****     ✓ Valid                 │
│  OPENAI_API_KEY      ····sk-****         ✓ Valid                 │
│  GOOGLE_AI_API_KEY   ····AIza****        ✓ Valid                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Task model assignment workflow**: Each pipeline task has a model dropdown ([▼]) populated with active models. Admin changes the dropdown → confirmation dialog shows cost delta → confirmed → `pipeline_tasks.model_id` updates → next run of that task uses the new model. No restart, no deployment. Each task is toggled independently — disabling "Briefing" keeps classification running. The `pipeline_logs.task` field tracks which task each LLM call belongs to, so you have a clear audit trail per task.

#### System Dashboard
All powered by `fetch_logs` and `pipeline_logs` — no separate monitoring infrastructure needed.
- **Fetch status per source**: last fetch time, last status (green/yellow/red), consecutive failures, articles/hour trend — all derived from `fetch_logs`
- **Pipeline task status**: per-task last run time, success rate, model used — from `pipeline_logs` grouped by `task`
- **LLM cost tracker**: API calls today per task, tokens used, estimated cost — summed from `pipeline_logs.input_tokens` / `output_tokens`
- **Briefing status**: today's news briefing generated? this week's learning digest generated? when? models used? — from `briefings`
- **Error feed**: Recent failed/partial fetch_logs and pipeline_logs, with error messages and tracebacks
- **Queue depth**: Count of `articles WHERE classified = false` — shows backlog waiting for classification

**Auth**: Simple password-based login. Single admin account initially. No need for role-based access or multi-user at this stage. Can upgrade to OAuth later if needed.

### 2.3 Analytics Dashboard (authenticated, part of admin)

Understanding how people use the reader site.

**Metrics:**

| Metric | What it tells you |
|--------|-------------------|
| Daily unique sessions | How many people visit |
| Page views per session | How engaged they are |
| Click-through rate (CTR) | % of headline impressions that result in clicks |
| CTR by source | Which sources produce the most compelling headlines |
| CTR by category | Which topics are most interesting to your audience |
| Top headlines (by clicks) | What resonated this week |
| Time-of-day distribution | When people read (informs fetch scheduling) |
| Referrer breakdown | Where traffic comes from |
| New vs returning sessions | Are people coming back? |

**Implementation approach:**
- Track two event types on the reader site: `page_view` (with category filter state) and `headline_click` (with article_id)
- **Session tracking**: On first page load, `lib/analytics.ts` checks for a `headlines_sid` cookie. If absent, it generates a random UUID v4 and sets the cookie with `max-age=1800` (30 minutes), `SameSite=Strict`, `path=/`. Each subsequent page load or event resets the cookie's max-age to 1800 — so the session expires after 30 minutes of inactivity, matching standard web analytics conventions. A new visit after expiry generates a new session ID. This means "unique sessions" approximates unique visits with a 30-minute inactivity window. The session_id is sent with every event POST. No server-side session state.
- Events posted to backend API → written to analytics_events table
- Dashboard queries this table with SQL aggregations
- Start simple, add PostHog or Plausible later if deeper funnel analysis is needed

**Privacy:**
- No user accounts, no PII collected
- Session IDs are random UUIDs, not tied to identity
- No third-party tracking scripts
- Analytics data retained for 90 days, then purged

---

## 3. Data Model

### `sources`

```sql
CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,              -- "Financial Times"
    slug            TEXT NOT NULL UNIQUE,       -- "ft"
    surface         TEXT NOT NULL DEFAULT 'news', -- "news" or "learning" — determines which reader surface shows this source's articles
    homepage_url    TEXT NOT NULL,              -- "https://ft.com"
    feed_url        TEXT NOT NULL,              -- RSS/Atom feed URL
    adapter_type    TEXT NOT NULL DEFAULT 'rss', -- "rss", "api", "scraper"
    adapter_config  JSONB NOT NULL DEFAULT '{}', -- adapter-specific settings
    fetch_interval  INTEGER NOT NULL DEFAULT 15, -- minutes between fetches
    active          BOOLEAN NOT NULL DEFAULT true,
    last_fetched_at TIMESTAMPTZ,
    last_etag       TEXT,                       -- ETag from last response (for conditional fetch)
    last_modified   TEXT,                       -- Last-Modified from last response (for conditional fetch)
    last_error      TEXT,                       -- last error message, null if healthy
    consecutive_failures INTEGER NOT NULL DEFAULT 0, -- reset to 0 on success, incremented on failure
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**`adapter_config` examples:**

```jsonc
// Standard RSS — no extra config needed
{}

// RSS with custom headers (e.g., for feeds that check User-Agent)
{
    "headers": {
        "User-Agent": "Headlines/1.0"
    }
}

// Future: API-based adapter
{
    "api_url": "https://api.example.com/articles",
    "api_key_env": "EXAMPLE_API_KEY",
    "response_mapping": {
        "title": "headline",
        "url": "link",
        "published_at": "pub_date"
    }
}
```

### `categories`

```sql
CREATE TABLE categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,              -- "Markets"
    slug            TEXT NOT NULL UNIQUE,       -- "markets"
    surface         TEXT NOT NULL DEFAULT 'news', -- "news" or "learning" — determines which surface and classification prompt uses this category
    description     TEXT NOT NULL,              -- LLM classification prompt context
    display_order   INTEGER NOT NULL DEFAULT 0,
    active          BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Category descriptions** are the editorial lever. They directly influence how the LLM classifies. The `description` field is injected verbatim into the classification prompt. The `surface` field determines which classification prompt a category belongs to — news categories are used when classifying articles from news sources, learning categories when classifying articles from learning sources. See Section 9 for the full initial category sets: 9 news categories (Economy, Markets, Tech, Politics, US, Europe, World, Business, Opinion) and 8 learning categories (Strategy, Leadership, Innovation, Technology & AI, Operations, Marketing & Growth, People & Culture, Entrepreneurship).

**Slug handling:** Slugs are the URL identifiers (`/markets`, `/learning/strategy`). They are auto-generated from the category name on creation (lowercased, spaces → hyphens, stripped of special characters). After creation, a slug can be changed, but this creates a redirect entry in `category_redirects` to preserve existing URLs. The admin UI shows a warning when editing a slug: "Changing this slug will create a redirect from the old URL. Existing bookmarks will continue to work."

### `category_redirects`

When a category slug changes, the old slug is preserved as a redirect — so bookmarked URLs like `/markets` continue working even if the category is renamed to `/financial-markets`.

```sql
CREATE TABLE category_redirects (
    old_slug    TEXT PRIMARY KEY,
    new_slug    TEXT NOT NULL,                  -- points to the current slug in categories
    surface     TEXT NOT NULL,                  -- "news" or "learning" — for URL resolution
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Behavior:** When the reader site or API receives a category slug that doesn't match any active category, it checks `category_redirects`. If found, it returns an HTTP 301 redirect to the new URL. If not found, it returns 404. Redirect chains are collapsed — if `A → B → C`, the entry for `A` is updated to point directly to `C`.

**Merge support:** When two categories are merged (e.g., "Marketing" into "Strategy"), the source category's slug is added to `category_redirects` pointing to the target category's slug. All `article_categories` rows are reassigned. The source category is then deleted.

### `articles`

```sql
CREATE TABLE articles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    external_id     TEXT NOT NULL,              -- GUID from feed, for dedup
    title           TEXT NOT NULL,
    url             TEXT NOT NULL,
    summary         TEXT,                       -- first paragraph or feed description
    author          TEXT,
    image_url       TEXT,
    published_at    TIMESTAMPTZ NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    classified      BOOLEAN NOT NULL DEFAULT false,
    hidden          BOOLEAN NOT NULL DEFAULT false, -- admin can hide articles
    cluster_id      UUID,                      -- articles about the same story share a cluster_id
    is_representative BOOLEAN NOT NULL DEFAULT true, -- only representatives appear in reader
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(), -- set by upsert when title/summary revised

    UNIQUE(source_id, external_id)
);

CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_unclassified ON articles(id) WHERE classified = false;
CREATE INDEX idx_articles_reader ON articles(published_at DESC) WHERE hidden = false AND is_representative = true;
CREATE INDEX idx_articles_cluster ON articles(cluster_id) WHERE cluster_id IS NOT NULL;
```

### `article_categories`

```sql
CREATE TABLE article_categories (
    article_id      UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    category_id     UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    confidence      REAL NOT NULL,             -- 0.0 to 1.0
    manual_override BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (article_id, category_id)
);

CREATE INDEX idx_article_categories_category ON article_categories(category_id);
```

### `fetch_logs`

Every fetch attempt — whether scheduled, manual, or test — is recorded here. This is the system's audit trail and the basis for health monitoring in the admin panel.

```sql
CREATE TABLE fetch_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id           UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    batch_id            UUID,                       -- groups fetches from "Refresh All" (null for scheduled/single)
    status              TEXT NOT NULL,              -- "running", "success", "partial", "failed"
    trigger             TEXT NOT NULL DEFAULT 'scheduled', -- "scheduled", "manual", "test", "batch"
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at         TIMESTAMPTZ,
    duration_ms         INTEGER,                    -- wall-clock time of the fetch
    http_status         INTEGER,                    -- HTTP status from feed request
    response_bytes      INTEGER,                    -- size of feed response
    articles_in_feed    INTEGER DEFAULT 0,          -- total articles found in the feed
    articles_new        INTEGER DEFAULT 0,          -- inserted (passed dedup)
    articles_updated    INTEGER DEFAULT 0,          -- existing articles with revised title/summary
    articles_skipped    INTEGER DEFAULT 0,          -- already existed, unchanged (dedup hit)
    articles_failed     INTEGER DEFAULT 0,          -- failed to parse individually
    error_message       TEXT,                       -- null if success
    error_traceback     TEXT,                       -- full traceback for debugging
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_fetch_logs_source ON fetch_logs(source_id, started_at DESC);
CREATE INDEX idx_fetch_logs_status ON fetch_logs(status) WHERE status != 'success';
CREATE INDEX idx_fetch_logs_started ON fetch_logs(started_at DESC);
CREATE INDEX idx_fetch_logs_batch ON fetch_logs(batch_id) WHERE batch_id IS NOT NULL;
```

**Why this matters:**
- **Debugging**: "Why are no Bloomberg articles from yesterday?" → check fetch_logs for that source. Was it a 403? A timeout? A parse failure?
- **Health dashboard**: Aggregate success/failure rates per source over time. Spot degrading feeds before they go fully dark.
- **Admin visibility**: The Sources table in admin shows last N fetches inline — green/red indicators, article counts, durations.
- **Capacity planning**: Track how many articles each source produces per fetch. Useful when tuning the classification batch size.
- **Test fetches**: When admin clicks "Test Fetch", the result is saved with `trigger='test'` so you have a record of what happened, but those articles are NOT inserted into the main articles table.

### `pipeline_logs`

Same principle for all LLM pipeline tasks — record every run. Used for classification batches, dedup confirmation, and briefing generation.

```sql
CREATE TABLE pipeline_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task                TEXT NOT NULL DEFAULT 'classification', -- "classification", "dedup", "briefing", "learning_digest"
    status              TEXT NOT NULL,              -- "running", "success", "partial", "failed"
                                                   -- "partial" (classification): some articles classified, some returned unparseable LLM output
                                                   -- "partial" (dedup): some articles deduped, some LLM calls failed
                                                   -- "partial" (briefing): briefing generated but with fewer articles than expected
    trigger             TEXT NOT NULL DEFAULT 'scheduled', -- "scheduled", "manual", "batch", "reclassify"
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at         TIMESTAMPTZ,
    duration_ms         INTEGER,
    articles_processed  INTEGER DEFAULT 0,          -- how many articles in this batch (classification/dedup)
    articles_classified INTEGER DEFAULT 0,          -- successfully assigned >= 1 category (classification only)
    articles_uncategorized INTEGER DEFAULT 0,       -- no category met confidence threshold (classification only)
    articles_failed     INTEGER DEFAULT 0,          -- LLM returned unparseable result (classification/dedup)
    model_used          TEXT,                        -- "claude-haiku-4-5" or "claude-sonnet-4-6"
    input_tokens        INTEGER,                    -- from API response usage
    output_tokens       INTEGER,                    -- from API response usage
    estimated_cost_usd  REAL,                       -- computed from token counts + model pricing
    error_message       TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pipeline_logs_started ON pipeline_logs(started_at DESC);
CREATE INDEX idx_pipeline_logs_task ON pipeline_logs(task, started_at DESC);
CREATE INDEX idx_pipeline_logs_status ON pipeline_logs(status) WHERE status != 'success';
```

**Why this matters:**
- **Cost tracking per task**: Know exactly how much classification vs. briefing costs. The admin dashboard breaks down spend by task.
- **Quality monitoring**: If `articles_uncategorized` spikes (classification), your category descriptions may need tuning. If briefing quality drops, try a different model.
- **Debugging**: If any task fails, the error_message tells you whether it was an API error, a rate limit, or a malformed response.
- **Audit trail**: The `task` + `model_used` fields show exactly which model produced each output, even as you experiment with different assignments.

### `llm_models`

The model registry. A catalog of every LLM model the system can use. Models are assigned to pipeline tasks via the `pipeline_tasks` table — the registry itself just tracks what's available.

```sql
CREATE TABLE llm_models (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider                TEXT NOT NULL,              -- "anthropic", "openai", "google"
    model_id                TEXT NOT NULL UNIQUE,       -- "claude-sonnet-4-6", "gpt-5-mini", "gemini-2.5-flash"
    display_name            TEXT NOT NULL,              -- "Claude Haiku 4.5"
    active                  BOOLEAN NOT NULL DEFAULT true,
    input_price_per_mtok    REAL,                       -- USD per million input tokens
    output_price_per_mtok   REAL,                       -- USD per million output tokens
    context_window          INTEGER,                    -- max input tokens
    max_output_tokens       INTEGER,                    -- max output tokens
    config                  JSONB NOT NULL DEFAULT '{}', -- provider-specific overrides (temperature, etc.)
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_llm_models_provider ON llm_models(provider);
```

**Design decisions:**

- **No `is_default` column.** Model-to-task assignment lives in `pipeline_tasks`, not here. The registry is a pure catalog. This cleanly supports different models for different tasks (e.g., Haiku for classification, Sonnet for editorial synthesis).
- **Pricing in the table**: Enables the admin UI cost comparison widget. Updated manually when providers change pricing — happens rarely enough that DB storage is fine.
- **`config` JSONB**: Provider-specific overrides. For example, `{"temperature": 0.2}` or `{"reasoning_effort": "none"}`. The pipeline merges these with sensible defaults per provider.
- **`model_id` is the API string**: The exact string sent to the provider API. `claude-sonnet-4-6`, not a friendly name. The `display_name` is for the UI.
- **API keys are NOT in this table**: They live in environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY`). The provider field tells the pipeline which env var to use.

### `pipeline_tasks`

Maps each pipeline task to a model. This is where you control which model does what. Different tasks can use different models — cheap models for classification, smarter models for editorial synthesis.

```sql
CREATE TABLE pipeline_tasks (
    task            TEXT PRIMARY KEY,              -- "classification", "dedup", "briefing", "learning_digest"
    model_id        TEXT NOT NULL REFERENCES llm_models(model_id),
    active          BOOLEAN NOT NULL DEFAULT true, -- toggle tasks independently
    config          JSONB NOT NULL DEFAULT '{}',   -- task-specific settings
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**The four tasks:**

| Task | Purpose | Default Model | Why |
|------|---------|---------------|-----|
| `classification` | Categorize articles into topics (both news and learning) | Claude Haiku 4.5 | Structured output task. Haiku is fast, cheap, accurate enough. Surface-aware: uses news categories for news sources, learning categories for learning sources. |
| `dedup` | Detect cross-source duplicate stories and cluster them | Claude Haiku 4.5 | Semantic comparison of headline pairs. Structured output: is_duplicate yes/no + pick best representative. Haiku handles this well — it's pattern matching, not synthesis. |
| `briefing` | Generate The Brief (daily news thematic summary) | Claude Sonnet 4.6 | Requires synthesizing themes across 100+ headlines into coherent prose. Needs stronger writing and reasoning. |
| `learning_digest` | Generate The Learning Digest (weekly learning summary) | Claude Sonnet 4.6 | Requires synthesizing management themes across a week of HBR/MIT SMR articles. Same quality requirement as briefing — reader-facing prose. |

> **Deferred: `analysis` task.** An "In Focus" task (top story cross-source synthesis, assigned to Sonnet 4.6) is planned for a future phase. When added, it will be a fifth row in this table with its own model assignment and active toggle.

**Design decisions:**

- **`task` as primary key**: There's a fixed, small set of tasks. No UUID needed. Adding a new task type is a code change (new worker + prompt), not an admin operation.
- **`config` JSONB**: Task-specific settings. For classification: `{}` (no overrides needed). For briefing: `{"max_sentences": 5}`. For learning_digest: `{"max_sentences": 5}`. The worker reads these at runtime.
- **Independent active toggles**: Disable briefing without affecting classification. Useful for testing, cost control, or if the editorial quality isn't meeting standards.
- **Model reassignment is instant**: Change `model_id` → next run picks up the new model. No restart.

### `briefings`

Stores generated editorial content — one row per date per type. Supports both the daily news briefing (The Brief) and the weekly learning digest (The Learning Digest).

```sql
CREATE TABLE briefings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type            TEXT NOT NULL,                 -- "daily_news" or "weekly_learning"
    date            DATE NOT NULL,                 -- the date this briefing covers (for weekly: the Monday)
    brief           TEXT,                          -- markdown content (null if task was inactive)
    article_ids     UUID[],                        -- articles referenced in the briefing
    brief_model     TEXT,                          -- model used (null if task inactive)
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(type, date)
);
```

**Two briefing types:**

| Type | Cadence | Covers | Appears on |
|------|---------|--------|------------|
| `daily_news` | Daily (6:30 AM) | Last 24 hours of classified news articles | News surface, above headlines |
| `weekly_learning` | Weekly (Monday 7:00 AM) | Last 7 days of classified learning articles | Learning surface, above topic-grouped articles |

**Why a separate table?** The briefing is one logical unit per period, not per-article. It references articles but has its own lifecycle (generated on schedule, can be regenerated on demand). Storing it alongside articles or classification logs would be awkward. The `UNIQUE(type, date)` constraint ensures at most one briefing per type per date.

### `analytics_events`

```sql
CREATE TABLE analytics_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      TEXT NOT NULL,              -- "page_view", "headline_click"
    article_id      UUID REFERENCES articles(id) ON DELETE SET NULL,
    category_slug   TEXT,                       -- which category tab was active
    source_slug     TEXT,
    session_id      TEXT NOT NULL,
    referrer        TEXT,
    user_agent      TEXT,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_analytics_created ON analytics_events(created_at DESC);
CREATE INDEX idx_analytics_session ON analytics_events(session_id);
CREATE INDEX idx_analytics_type ON analytics_events(event_type, created_at DESC);
```

**Partitioning**: If analytics volume grows, partition `analytics_events` by month. For now, the index on `created_at` plus a 90-day retention policy keeps the table manageable.

---

## 4. Pipeline Architecture

### 4.1 The Scraper Function

The scraper function is the central unit of the fetch pipeline. It is a single, well-defined function that orchestrates the entire process of fetching articles from a source and recording everything that happened. Every fetch — scheduled, manual, or test — goes through this function.

```
┌────────────────────────────────────────────────────────────────────────┐
│                  scrape(source, trigger, batch_id=None)                 │
│                                                                        │
│  1. Create fetch_log record (status="running", batch_id if provided)   │
│                         │                                              │
│                         ▼                                              │
│  2. Call adapter.fetch(source)                                         │
│     ├── HTTP GET with conditional headers (ETag, Last-Modified)        │
│     ├── If 304 Not Modified → skip to step 6 (success, 0 new)         │
│     ├── Record http_status, response_bytes                             │
│     └── Parse raw articles                                             │
│                         │                                              │
│                         ▼                                              │
│  3. Dedup + upsert against existing articles                           │
│     ├── Check (source_id, external_id) uniqueness                      │
│     ├── New article → insert with classified=false                     │
│     ├── Exists but title/summary changed → update (keep classification)│
│     ├── Exists and unchanged → skip                                    │
│     └── Count: articles_new, articles_updated, articles_skipped        │
│                         │                                              │
│                         ▼                                              │
│  4. Write to DB (if trigger != "test")                                 │
│     └── Bulk upsert: INSERT ... ON CONFLICT DO UPDATE                  │
│                         │                                              │
│                         ▼                                              │
│  5. Update source record                                               │
│     ├── last_fetched_at = now                                          │
│     ├── last_etag, last_modified = from response headers               │
│     ├── last_error = null (on success) or error message (on failure)   │
│     └── Increment consecutive_failures or reset to 0                   │
│                         │                                              │
│                         ▼                                              │
│  6. Finalize fetch_log record                                          │
│     ├── status = "success" | "partial" | "failed"                      │
│     ├── finished_at = now                                              │
│     ├── duration_ms = finished_at - started_at                         │
│     └── All counters filled in                                         │
│                         │                                              │
│                         ▼                                              │
│  7. Return FetchResult (for test fetches: includes parsed articles)    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Four callers, one function:**

| Caller | Trigger value | batch_id | Behavior |
|--------|--------------|----------|----------|
| **Scheduler** (per source interval) | `"scheduled"` | `null` | Full scrape: fetch → dedup → insert → log. Silent unless errors. |
| **Admin "Refresh" per source** | `"manual"` | `null` | Same as scheduled, but triggered on demand for one source. |
| **Admin "Refresh All"** | `"batch"` | shared UUID | Scrapes all active sources concurrently. All fetch_logs share the same `batch_id` so the UI can track them as a group. Triggers classification when done. |
| **Admin "Test Fetch"** | `"test"` | `null` | Runs the full scrape pipeline but does NOT insert articles. Returns parsed articles for preview. Still writes a fetch_log. |

**Return type:**

```
FetchResult = {
    fetch_log_id: uuid,                         # for tracking / polling
    status: "success" | "partial" | "failed",
    articles_in_feed: int,
    articles_new: int,
    articles_updated: int,
    articles_skipped: int,
    articles_failed: int,
    duration_ms: int,
    error: str | None,
    articles: List[RawArticle] | None           # only populated for test fetches
}
```

### 4.1.1 Manual Refresh — Deep Design

Manual refresh is a first-class feature, not an afterthought. The admin needs to be able to say "fetch everything now" and see exactly what happens, in real time.

**Two levels of manual refresh:**

| Action | Scope | Use case |
|--------|-------|----------|
| **Refresh source** | Single source | Just added a source, debugging a feed, breaking news on a specific outlet |
| **Refresh All** | All active sources | Want fresh headlines now, just changed categories and want new articles to classify, morning routine |

**Refresh All — how it works:**

```
Admin clicks "Refresh All"
         │
         ▼
POST /api/admin/refresh-all
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Generate batch_id (UUID)                                 │
│  2. Check cooldown: reject if another batch started < 60s    │
│  3. Query all active sources                                 │
│  4. For each source, check concurrency lock:                 │
│     - If source has a fetch_log with status="running",       │
│       skip it (don't double-fetch)                           │
│  5. Fire scrape(source, trigger="batch", batch_id) for each  │
│     eligible source — run concurrently (asyncio.gather)      │
│  6. Return batch_id immediately to the admin UI              │
│  7. Sources are fetched concurrently in background            │
│  8. When ALL source fetches in the batch complete:            │
│     - Trigger classification for newly fetched articles      │
│     - Log the classification run with trigger="batch"        │
└─────────────────────────────────────────────────────────────┘
```

**Response (immediate):**
```
{
    batch_id: "abc-123",
    sources_triggered: 5,
    sources_skipped: 0,       // already running
    sources_skipped_names: []
}
```

**Admin UI polls for progress:**
```
GET /api/admin/refresh-status/:batch_id

Response:
{
    batch_id: "abc-123",
    started_at: "2026-03-10T14:00:00Z",
    sources: [
        {
            source_name: "Financial Times",
            source_slug: "ft",
            status: "success",
            articles_new: 5,
            articles_skipped: 12,
            duration_ms: 1200
        },
        {
            source_name: "Bloomberg",
            source_slug: "bloomberg",
            status: "running",      // still in progress
            articles_new: null,
            articles_skipped: null,
            duration_ms: null
        },
        ...
    ],
    overall_status: "running",      // "running" | "completed" | "completed_with_errors"
    total_articles_new: 5,          // sum of completed sources so far
    classification: {
        status: "pending",          // "pending" | "running" | "completed"
        articles_classified: null
    }
}
```

**Concurrency guard:**

A source must never have two fetches running simultaneously. The scraper function enforces this:

```
def scrape(source, trigger, batch_id=None):
    # Check for in-flight fetch (with staleness guard)
    running = db.query(fetch_logs)
        .filter(
            source_id=source.id,
            status="running",
            started_at > now() - interval '5 minutes'  # stale records are considered failed
        )
        .first()

    if running:
        # Don't double-fetch. Return a skip result.
        return FetchResult(status="skipped", error="Fetch already in progress")

    # Expire any stale "running" records for this source (crash recovery)
    db.execute(
        update(fetch_logs)
        .where(source_id=source.id, status="running", started_at <= now() - interval '5 minutes')
        .values(status="failed", error_message="Expired: worker likely crashed", finished_at=now())
    )

    # Proceed with fetch...
```

**Stale record recovery:** If the worker crashes mid-fetch, the fetch_log record stays `status='running'` forever, which would permanently block the concurrency guard. The 5-minute staleness window handles this: any "running" record older than 5 minutes is assumed to be a crash artifact. The scraper expires it before proceeding. Additionally, the worker runs a startup sweep on boot — `UPDATE fetch_logs SET status='failed', error_message='Expired on worker restart' WHERE status='running'` — to clean up any records left by a previous process.

This handles all race conditions:
- Scheduled fetch running when admin clicks "Refresh" → skip
- Admin clicks "Refresh All" twice quickly → second call rejected by 60s cooldown
- Two sources in a batch finish at different times → each is independent

**Cooldown / rate limiting:**

| Scope | Cooldown | Why |
|-------|----------|-----|
| **Refresh All** | 60 seconds between batch triggers | Prevent accidental double-clicks. One full sweep per minute is plenty. |
| **Per-source Refresh** | 30 seconds between manual fetches of the same source | Don't hammer a feed. Also prevents double-clicks. |
| **Scheduled fetches** | Governed by `source.fetch_interval` (default 15 min) | Normal cadence. Conditional fetching (ETags) keeps this polite. |

The cooldown is checked server-side. The UI also disables the button with a countdown timer, but the server is the authority.

**Post-refresh classification:**

After a "Refresh All" batch completes, the system automatically triggers a classification run for all newly fetched (unclassified) articles. This means: click "Refresh All", wait ~30 seconds, and the reader site has fresh, categorized headlines. No second manual step needed.

For single-source refresh, classification is also triggered but just for that source's new articles.

**Admin UI for manual refresh:**

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Sources                                                     [Refresh All] │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Source           Surface  Status  Last Fetch    New  Interval   Actions            │
│  ──────────────   ───────  ──────  ──────────    ───  ────────   ────────           │
│  Financial Times  News     ● OK    10 min ago     3   15m  [▼]   [Refresh] [Edit]  │
│  Bloomberg        News     ● OK    12 min ago     5   15m  [▼]   [Refresh] [Edit]  │
│  WSJ              News     ● Err   1h ago         0   15m  [▼]   [Refresh] [Edit]  │
│  The Verge        News     ● OK    8 min ago      2   30m  [▼]   [Refresh] [Edit]  │
│  Stratechery      News     ● OK    10 min ago     1   120m [▼]   [Refresh] [Edit]  │
│  HBR              Learning ● OK    4h ago         2   360m [▼]   [Refresh] [Edit]  │
│  MIT SMR          Learning ● OK    8h ago         1   720m [▼]   [Refresh] [Edit]  │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│  ┌─ Refresh Progress (batch abc-123) ───────────────────────────────────┐  │
│  │                                                                       │  │
│  │  ✓ Financial Times    5 new · 12 skipped · 1.2s                      │  │
│  │  ✓ Bloomberg          3 new · 8 skipped  · 0.9s                      │  │
│  │  ✓ WSJ               4 new · 10 skipped · 1.1s                      │  │
│  │  ✓ The Verge          2 new · 15 skipped · 0.7s                      │  │
│  │  ✓ Stratechery        1 new · 0 skipped  · 0.4s                      │  │
│  │  ✓ HBR                2 new · 3 skipped  · 0.5s                      │  │
│  │  ✓ MIT SMR            1 new · 1 skipped  · 0.3s                      │  │
│  │                                                                       │  │
│  │  ⟳ Classifying 18 new articles...                                    │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

The progress panel appears when a refresh is triggered and shows real-time status:
- **Checkmark (✓)**: Source fetch completed successfully
- **Spinner (⟳)**: Source fetch or classification in progress
- **Red X (✗)**: Source fetch failed (with error message expandable)
- After all fetches: classification status with count of articles being processed
- Panel auto-dismisses after 10 seconds of idle (all done), or stays pinned if there were errors

**Keyboard shortcut**: `R` triggers "Refresh All" when on the admin sources page. Power user convenience.

**Adapter pattern:**

```
BaseAdapter (abstract)
  ├── RSSAdapter          — parses RSS/Atom feeds (covers 90%+ of sources)
  ├── JSONAPIAdapter      — for sources with JSON APIs (future)
  └── ScraperAdapter      — for sources requiring HTML scraping (future)

Each adapter implements:
  fetch(source: Source) → AdapterResult

AdapterResult = {
    http_status: int,
    response_bytes: int,
    articles: List[RawArticle],
    errors: List[str],          # per-article parse errors
    etag: str | None,           # from response ETag header (for conditional fetch)
    last_modified: str | None   # from response Last-Modified header
}

RawArticle = {
    external_id: str,    # unique ID from source (GUID from RSS, or URL hash)
    title: str,
    url: str,
    summary: str | None,
    author: str | None,
    image_url: str | None,
    published_at: datetime
}
```

The adapter is responsible for HTTP + parsing. The scraper function handles everything else (dedup, insert, logging). This separation means adapters are simple and testable — they just turn a feed into structured data.

**Conditional fetching (ETags):** The adapter sends `If-None-Match` and `If-Modified-Since` headers using values stored on the source record (`last_etag`, `last_modified`). If the feed server returns `304 Not Modified`, the fetch short-circuits — no parsing, no dedup, no insertion. The fetch log records `http_status=304` and `articles_in_feed=0`. This makes frequent polling (every 15 minutes) polite and efficient: unchanged feeds return a tiny 304 response instead of the full feed body. After a `200` response, the adapter extracts the new `ETag` and `Last-Modified` headers and the scraper stores them on the source record for the next fetch.

**Dedup + upsert logic**: The `(source_id, external_id)` unique constraint drives a three-way branch:

1. **New article** (no conflict) → insert with `classified=false`. Enters the classification queue.
2. **Exists but title or summary changed** → update `title`, `summary`, and `updated_at`. Keep existing classification — a headline tweak rarely changes the category. This matters because sources (especially Bloomberg and WSJ) frequently revise headlines as stories develop. The headline is the product; stale titles undermine trust.
3. **Exists and unchanged** → skip. Nothing to do.

Implementation: `INSERT ... ON CONFLICT (source_id, external_id) DO UPDATE SET title = EXCLUDED.title, summary = EXCLUDED.summary, updated_at = now() WHERE articles.title != EXCLUDED.title OR articles.summary IS DISTINCT FROM EXCLUDED.summary`.

**Cross-source story deduplication**: When multiple sources cover the same story (e.g., Bloomberg, FT, and WSJ all reporting "Fed signals rate pause"), the system detects these as duplicates and clusters them. Only one **representative** article per cluster appears in the reader — the others are linked as "Also in: Bloomberg, Financial Times." This prevents the reader from being flooded with 5-10 headlines about the same event. The deduplication pipeline (§4.2.2) runs after classification and uses a two-phase approach: fast title similarity to find candidates, then LLM confirmation to avoid false positives. All articles are stored — nothing is deleted — but only representatives are shown. The admin can override which article is representative.

**`published_at` validation**: The adapter rejects articles with dates more than 7 days in the past (stale feed cache) or more than 1 hour in the future (timezone bug). Articles with missing `published_at` fall back to `fetched_at`. This prevents a bad feed from polluting the reader site with ghost articles dated 2019 or next Tuesday.

**Status determination:**

| Condition | Status |
|-----------|--------|
| All articles parsed, all new ones inserted | `"success"` |
| Some articles failed to parse, but others succeeded | `"partial"` |
| Adapter threw an exception (network error, timeout, HTTP 4xx/5xx) | `"failed"` |
| Feed returned 200 but contained 0 articles | `"success"` (empty feed is not an error) |
| Feed returned 304 Not Modified (conditional fetch) | `"success"` (no new content — expected and efficient) |

**Error handling:**
- If a fetch fails, the error is recorded in both `fetch_logs.error_message` and `sources.last_error`
- The source tracks `consecutive_failures` — if it reaches 5, the admin dashboard highlights this source in red, but it is NOT auto-disabled (the admin decides)
- Timeout: 30 seconds per HTTP request. RSS feeds should respond much faster, but be defensive.
- The scraper function NEVER throws — it catches all exceptions and records them in the fetch_log. The scheduler must never crash because one source failed.

**Scheduler:**

Each source has its own fetch interval (default 15 minutes). The scheduler:
1. Queries all active sources where `now() - last_fetched_at >= fetch_interval` (or `last_fetched_at IS NULL`)
2. Calls `scrape(source, trigger="scheduled")` for each
3. Fetches are staggered — not all sources at minute :00. On startup, spread initial fetches over the first interval window.
4. After each scheduled scrape completes with `articles_new > 0`, triggers a classification run for the newly inserted articles. This ensures classification follows fetching immediately — no separate polling loop, no delay.

**On worker startup:** The scheduler runs a one-time sweep: `UPDATE fetch_logs SET status='failed', error_message='Expired on worker restart', finished_at=now() WHERE status='running'`. This cleans up any stale "running" records left by a previous crashed process before the scheduler begins dispatching fetches.

### 4.2 LLM Classification Pipeline

Same philosophy as the scraper function — every classification run is logged in `pipeline_logs`.

```
┌───────────────┐     ┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│ Collect batch  │────▶│ Create class_log │────▶│ Build prompt │────▶│ Call LLM API │
│ (unclassified) │     │ (status=running) │     │              │     │              │
└───────────────┘     └──────────────────┘     └──────────────┘     └──────┬───────┘
                                                                           │
                                                                           ▼
                                                                   ┌──────────────┐
                                                                   │ Parse response│
                                                                   │ Write to DB   │
                                                                   │ Finalize log  │
                                                                   └──────────────┘
```

**Trigger**: Classification is triggered directly by the scraper — after each successful fetch that inserts `articles_new > 0`, the scraper calls the classifier for the newly inserted articles. For "Refresh All" batches, classification runs once after all source fetches complete (not after each individual source). For reclassification requests from admin, it runs on demand. There is no independent polling loop — classification always follows a concrete event.

**Batching**: Process unclassified articles in batches of 10-20. This reduces API calls while keeping latency reasonable. New articles are classified immediately after the fetch that produced them — typically within seconds.

**Prompt design** (categories are loaded dynamically from DB, filtered by the source's `surface` — this is what makes it modular). Below is the news classification prompt; the learning classification prompt has the same structure but with learning categories (Strategy, Leadership, Innovation, etc.):

```
System: You are a news article classifier. Given a list of articles (title,
summary, source), assign each article to one or more categories. Return JSON.

Categories:
- economy: Macroeconomic trends, GDP, inflation, unemployment, economic
  policy, fiscal policy, economic indicators, recessions, growth forecasts
- markets: Stock markets, bonds, commodities, forex, interest rates, central
  bank policy (Fed, ECB, BoE), trading, IPOs, earnings reports, market
  analysis, investor sentiment
- tech: Technology companies, products, software, hardware, artificial
  intelligence, machine learning, startups, gadgets, consumer electronics,
  apps, social media platforms, cybersecurity, cloud computing
- politics: Political campaigns, legislation, government policy, partisan
  politics, elections, political analysis, lobbying, political appointments
- us: United States domestic affairs — US economy, US policy, US society, US
  events. Stories primarily about what's happening inside America.
- europe: European affairs — EU policy, European economies, European politics,
  events in European countries. Stories primarily about what's happening in
  Europe.
- world: International affairs outside US and Europe — Asia, Middle East,
  Africa, Latin America, global diplomacy, wars and conflicts, international
  organizations (UN, NATO), global health, climate policy
- business: Corporate strategy, mergers and acquisitions, executive
  appointments, company earnings, industry trends, regulation, antitrust,
  supply chains, entrepreneurship
- opinion: Editorials, op-eds, columns, analysis and commentary pieces. Often
  identifiable by URL patterns (/opinion/, /editorial/) or by the presence of
  a prominent columnist byline.

Articles:
[
  {"id": "abc123", "title": "...", "summary": "...", "source": "Bloomberg"},
  {"id": "def456", "title": "...", "summary": "...", "source": "WSJ"},
  ...
]

For each article, return:
{
  "classifications": [
    {
      "id": "abc123",
      "categories": [
        {"slug": "markets", "confidence": 0.95},
        {"slug": "business", "confidence": 0.7}
      ]
    },
    ...
  ]
}

Rules:
- An article can belong to 1-3 categories
- Only assign a category if confidence >= 0.5
- If none of the categories fit well, return an empty categories array
- "us" and "europe" are geographic — use them when the story is primarily
  about that region. A story about "Fed raises rates" is both "us" and
  "economy". A story about "ECB policy" is both "europe" and "economy".
```

**Critical: categories are loaded from DB at prompt-build time, filtered by surface.** The prompt is not hardcoded. When classifying articles from a news source, only categories with `surface='news'` are loaded into the prompt. When classifying articles from a learning source, only categories with `surface='learning'` are loaded. This means an HBR article is classified against Strategy, Leadership, Innovation, etc. — never against Economy, Markets, or Politics. When you add, remove, or rename a category in the admin panel, the next classification batch for that surface automatically uses the updated set. The category `description` field in the database is what appears in the prompt. This is the modularity mechanism.

**Task-based model dispatch**: No task hardcodes a provider or model. Each pipeline task reads its assigned model from the `pipeline_tasks` table and dispatches to the appropriate provider adapter. Reassigning a model to a task is an admin panel operation — zero code changes, zero restarts.

```
run_task(task_name, payload, db)
    │
    ├── 1. task = get_pipeline_task(db, task_name)    # SELECT * FROM pipeline_tasks WHERE task = ?
    ├── 2. model = get_model(db, task.model_id)       # SELECT * FROM llm_models WHERE model_id = ?
    ├── 3. provider_fn = PROVIDERS[model.provider]     # "anthropic" → call_anthropic
    ├── 4. api_key = get_api_key(model.provider)       # env var: ANTHROPIC_API_KEY, etc.
    └── 5. result = provider_fn(payload, model.model_id, api_key, task.config)
```

**Provider adapters**: Each provider has a thin adapter that translates the universal classification request into the provider's specific API format. The prompt content is identical across providers — only the API call differs.

```
LLM Provider Adapters
  ├── anthropic.py    → Anthropic Messages API (structured JSON via tool use)
  ├── openai.py       → OpenAI Chat Completions API (response_format: json_object)
  ├── google.py       → Google Generative AI API (response_mime_type: application/json)
  └── registry.py     → provider string → adapter function mapping

All adapters implement the same interface:
  async def classify_<provider>(
      articles: list[dict],
      categories: list[dict],
      model_id: str,
      api_key: str,
      config: dict          # from llm_models.config JSONB
  ) -> ClassificationResult

ClassificationResult = {
    classifications: list[{id, categories: [{slug, confidence}]}],
    input_tokens: int,
    output_tokens: int,
    latency_ms: int
}
```

**The prompt is provider-agnostic.** The same system prompt and article payload is used regardless of provider. What changes is *how* it's sent: Anthropic uses the Messages API with tool use for structured output, OpenAI uses chat completions with `response_format`, Google uses `generateContent` with JSON response MIME type. The adapter handles this translation. The prompt itself (category definitions, article list, output format instructions) is built once and passed to the adapter.

**Classification model**: Claude Haiku 4.5 (via `pipeline_tasks`). Classification is a straightforward structured-output task — Haiku handles it well at minimal cost. The admin can reassign any registered model to the classification task at any time.

**Classification cost**: With 5 news sources fetched every 15 minutes plus 2 learning sources fetched every 6-12 hours, expect ~160 articles/day total (~150 news + ~10 learning) → ~11 batch calls/day → ~22K input tokens + ~5.5K output tokens/day. At Haiku 4.5 pricing ($1/$5 per MTok): ~$0.05/day (~$1.50/mo).

**Logging**: Each classification batch creates a `pipeline_logs` record with `task='classification'`, tracking: articles processed, classified, uncategorized, failed, **model used**, token counts, estimated cost, and any errors. This feeds the System Dashboard and the per-task cost breakdown.

### 4.2.1 Briefing Pipelines

Two editorial tasks generate reader-facing summaries on different cadences — one daily for news, one weekly for learning. Both follow the same architecture: collect articles → build prompt → call LLM → store in `briefings` table → log in `pipeline_logs`.

#### The Brief — Daily News Summary

`pipeline_tasks.task = 'briefing'`:
1. Collect all **news** articles (from sources with `surface='news'`) classified in the last 24 hours, filtering to `is_representative = true` to avoid counting the same story multiple times
2. Read task config from `pipeline_tasks.config` (e.g., `{"max_sentences": 5}`) and inject into the prompt (e.g., "Write a {max_sentences}-sentence thematic summary")
3. Build prompt: system instructions + task config + article list (title, source, categories) — ~9K input tokens
4. Send to the briefing model (default: Sonnet 4.6)
5. Response: 3-5 sentence thematic summary in markdown — ~150 output tokens
6. Store in `briefings` with `type='daily_news'`
7. Log in `pipeline_logs` with `task='briefing'`

**Schedule**: The editorial worker runs on a fixed daily schedule via APScheduler — default **6:30 AM** in the timezone set by `BRIEFING_TIMEZONE` (default `America/New_York`). At this time, it checks whether today's briefing already exists in `briefings` (where `type='daily_news'`). If not, it collects all news articles classified in the last 24 hours and generates The Brief. If no articles were classified (e.g., all fetches returned 304 overnight), it skips and retries at the next scheduled classification run — specifically, any classification run that produces newly classified news articles checks whether today's news briefing is missing, and generates it as a follow-up. This means The Brief appears either at 6:30 AM or shortly after the first successful classification of the day, whichever comes later. The admin can also trigger generation manually at any time.

**Regeneration**: The admin can trigger regeneration of today's briefing (e.g., after a midday fetch brings significant new stories). This overwrites the existing `briefings` row for today's `daily_news` and logs a new `pipeline_logs` entry with `trigger='manual'`.

#### The Learning Digest — Weekly Learning Summary

`pipeline_tasks.task = 'learning_digest'`:
1. Collect all **learning** articles (from sources with `surface='learning'`) classified in the last 7 days, filtering to `is_representative = true`
2. Read task config from `pipeline_tasks.config` (e.g., `{"max_sentences": 5}`)
3. Build prompt: system instructions + task config + article list (title, source, summary, categories) — includes summaries since learning articles benefit from the extra context. ~4K input tokens (lower volume than news).
4. Send to the learning digest model (default: Sonnet 4.6)
5. Response: 3-5 sentence thematic summary of the week's management/strategy thinking — ~150 output tokens
6. Store in `briefings` with `type='weekly_learning'`, `date` = the Monday of the current week
7. Log in `pipeline_logs` with `task='learning_digest'`

**Schedule**: Weekly via APScheduler — default **Monday 7:00 AM** in the timezone set by `BRIEFING_TIMEZONE`. Checks whether this week's learning digest already exists. If fewer than 3 learning articles were classified in the past week, it skips (not enough content for a meaningful digest). The admin can trigger generation manually at any time.

**Regeneration**: Same as The Brief — admin can regenerate this week's digest on demand.

#### Why Sonnet for both?

Classification is pattern matching — "read title → assign categories." Editorial synthesis requires understanding nuance, comparing how different publications frame the same topic, and writing coherent prose. The quality difference between Haiku and Sonnet is negligible for classification but noticeable for synthesis. Sonnet is worth the premium for both reader-facing summaries.

**Cost**: News briefing ~$0.03/day (~$0.90/mo). Learning digest ~$0.03/week (~$0.12/mo). Combined with classification (~$1.50/mo) and dedup (~$0.30/mo), total pipeline cost is ~$2.82/mo.

**Confidence threshold**: Only write `article_categories` rows where confidence >= 0.5. Articles with no confident category assignment appear in an "Uncategorized" list in admin for manual review.

**Reclassification**: When category definitions change, the admin can trigger reclassification of recent articles (last 24h or 7d). This clears existing `article_categories` rows (where `manual_override = false`) and reprocesses them. Reclassification runs are logged with `trigger='reclassify'`.

### 4.2.2 Cross-Source Story Deduplication

When 5 news sources each report "Fed signals rate pause," the reader shouldn't show 5 nearly identical headlines. The deduplication pipeline clusters articles about the same story and selects one representative to display, while preserving all articles in the database.

**Why this matters**: With 5 news sources fetching every 15 minutes, a major story generates 5-10 duplicate headlines within hours. Without dedup, the reader's front page looks like a broken aggregator — repeating the same event over and over. Dedup transforms this into a single authoritative headline with "Also in: Bloomberg, Financial Times, WSJ" beneath it, which is actually *more* informative than showing all five.

**Pipeline position**: Dedup runs after classification, triggered by the same event:

```
Scrape → Store → Classify → Dedup → (Briefing uses representatives only)
```

After each classification batch completes with newly classified articles, the scheduler triggers `dedup_batch()` for those articles. This ensures articles are both classified and deduped before the reader sees them.

**Two-phase approach**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  dedup_batch(article_ids)                               │
│                                                                        │
│  Phase 1 — Fast candidate detection (free, instant, no LLM)           │
│  ─────────────────────────────────────────────────────────────         │
│  For each new article:                                                 │
│    1. Normalize title (lowercase, strip punctuation, remove stops)     │
│    2. Compare against articles from same surface, last 48h             │
│       (only representatives — don't compare against existing dupes)    │
│    3. Compute Jaccard similarity on word tokens                        │
│    4. If similarity > threshold (config, default 0.35):                │
│       → add to candidate list (max 5 candidates per article)          │
│    5. If no candidates → article stays independent (representative)   │
│                         │                                              │
│                         ▼                                              │
│  Phase 2 — LLM semantic confirmation (only for candidates)            │
│  ─────────────────────────────────────────────────────────             │
│  For each article with candidates:                                     │
│    1. Send to LLM: "Is this the same story?"                          │
│    2. LLM returns: is_duplicate (yes/no), which candidate,            │
│       best representative (most informative), confidence              │
│    3. If duplicate confirmed:                                          │
│       → Assign same cluster_id as the match                           │
│       → Mark as is_representative = false                             │
│       → Re-evaluate representative (LLM picks the best headline)     │
│    4. If not duplicate → article stays independent                    │
│                         │                                              │
│                         ▼                                              │
│  Log in pipeline_logs (task='dedup')                                   │
│    articles_processed, duplicates_found, clusters_created,             │
│    clusters_updated, model used, tokens, cost                          │
│                                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Phase 1 — Fast candidate detection**:

No LLM calls. Runs in milliseconds. Filters out the ~80% of articles that have no plausible duplicates, so the LLM only processes real candidates.

```
normalize_title(title):
    1. Lowercase
    2. Strip punctuation
    3. Remove common stop words (the, a, an, in, on, at, to, for, of, is, ...)
    4. Return set of remaining tokens

similarity(title_a, title_b):
    tokens_a = normalize_title(title_a)
    tokens_b = normalize_title(title_b)
    return |tokens_a ∩ tokens_b| / |tokens_a ∪ tokens_b|    # Jaccard index
```

The threshold (default 0.35) is stored in `pipeline_tasks.config` for the `dedup` task — tunable via admin without code changes. Lower threshold = more candidates sent to LLM (higher recall, higher cost). Higher threshold = fewer candidates (might miss paraphrased duplicates).

**Phase 2 — LLM semantic confirmation**:

The prompt explicitly distinguishes between "same story" and "same topic":

```
System: You are a news deduplication system. Determine whether a new article
covers the SAME SPECIFIC story as any candidate article.

SAME STORY = same event, announcement, or development
  ✓ "Apple launches iPhone 17" and "iPhone 17 unveiled at Apple event"
  ✓ "Fed signals rate pause amid sticky CPI" and "Fed holds rates steady, cites inflation"

NOT the same story:
  ✗ Same topic, different event: "Fed discusses rates" vs "ECB considers rate cut"
  ✗ Same subject, different angle: "Apple launches iPhone" vs "How iPhone 17's chip was designed"
  ✗ News vs opinion: "Apple launches iPhone 17" vs "Why the iPhone 17 is a disappointment"
  ✗ Update to a story: "Apple announces iPhone 17" vs "iPhone 17 pre-orders now open"

NEW ARTICLE:
Title: {title}
Source: {source}
Summary: {summary}
Published: {published_at}

CANDIDATES (from other sources, same surface, last 48h):
1. Title: {title} | Source: {source} | Summary: {summary} | Published: {published_at}
2. ...

Respond with JSON:
{
  "is_duplicate": true | false,
  "duplicate_of": <candidate number> | null,
  "best_representative": "new" | <candidate number>,
  "confidence": "high" | "medium" | "low",
  "reasoning": "<one sentence>"
}

"best_representative" picks the article with the most informative headline —
the one a reader would prefer to see. If the new article has a better headline,
return "new" and the system will swap the representative.
```

**Representative selection**: The LLM picks the best headline based on informativeness. If a later article has a better headline than the current representative, the system swaps: the old representative gets `is_representative = false`, the new one gets `is_representative = true`. The cluster_id stays the same. This means a cluster's visible headline improves over time as more sources cover the story.

**Cluster lifecycle**:

1. **First article** — no candidates → stays independent, `cluster_id = gen_random_uuid()`, `is_representative = true`
2. **Second article about same story** — Phase 1 finds candidate, Phase 2 confirms → assigned same `cluster_id`, LLM picks best representative
3. **Third, fourth, fifth** — each checked against the cluster's representative → added to the cluster if confirmed
4. **After 48 hours** — new articles are no longer compared against this cluster (window expired)

**What the reader sees**:

Instead of:
```
Fed signals rate pause through Q2 amid sticky CPI data
The Wall Street Journal · 3h

Fed holds rates steady, cites persistent inflation concerns
Bloomberg · 4h

Federal Reserve pauses rate cuts as CPI remains above target
Financial Times · 5h
```

The reader sees:
```
Fed signals rate pause through Q2 amid sticky CPI data
The Wall Street Journal · 3h · Also in: Bloomberg, Financial Times
```

One headline. Clear attribution. The reader knows the story has broad coverage, which signals importance. Clicking any "Also in" source opens that source's version of the article.

**Learning surface**: Dedup applies to both surfaces, but learning sources (HBR, MIT SMR) rarely cover the exact same topic simultaneously. The system handles it generically — no surface-specific dedup logic.

**Briefings use representatives only**: When The Brief or The Learning Digest collects articles to summarize, it filters `WHERE is_representative = true`. This prevents the LLM from seeing the same story 5 times and wasting tokens on redundant content. The briefing becomes a better summary of distinct stories.

**Admin visibility**:
- Articles list shows cluster info: "Part of cluster (3 sources)" badge
- Admin can click into a cluster to see all articles and their sources
- Admin can override representative: click "Make representative" on any article in the cluster
- Admin can break a cluster: "Unlink" removes an article from its cluster, making it independent
- Pipeline logs show dedup stats: articles processed, duplicates found, clusters created/updated

**Cost**: Most articles won't have candidates after Phase 1 (different topics, different sources, different times). Estimate ~20-30% of articles pass Phase 1, meaning ~30-50 LLM calls/day for dedup confirmation. At Haiku 4.5 pricing with ~500 input tokens + ~100 output tokens per call: ~$0.01/day (~$0.30/mo). Combined with classification and briefings, total pipeline cost rises from ~$2.52/mo to ~$2.82/mo.

**Config** (stored in `pipeline_tasks.config` for the `dedup` task):
```json
{
  "similarity_threshold": 0.35,
  "window_hours": 48,
  "max_candidates": 5
}
```

Tunable via admin panel. The admin can also disable dedup entirely by setting the `dedup` task to `active = false` — all articles revert to independent display.

### 4.3 Retention Pipeline

- Daily job: delete articles where `published_at` is older than 30 days (configurable)
- Cascade deletes article_categories rows
- Briefings (both daily news and weekly learning) retained for 30 days
- Fetch logs and pipeline logs retained for 90 days
- Analytics events retained for 90 days independently

---

## 5. API Design

Single backend API serving all three surfaces.

### Public Endpoints (Reader Site)

```
GET /api/headlines
    ?surface={news|learning}  -- default "news"
    ?category={slug}         -- filter by category (optional, must match surface)
    ?page={n}                -- pagination (default 1)
    &per_page={n}            -- items per page (default 30, max 100)
    Response: {
        surface: "news" | "learning",
        headlines: [
            {
                id, title, url, summary?,         -- summary included for learning articles
                source_name, source_slug,
                source_homepage, published_at,
                categories: [{name, slug}],
                also_reported_by: [               -- other sources covering the same story
                    { source_name, source_slug, url }
                ]                                 -- empty array if no cluster or solo article
            }
        ],
        pagination: { page, per_page, total, has_next }
    }
    -- Only representative articles are returned (WHERE is_representative = true)
    -- also_reported_by is populated from other articles in the same cluster
    -- If category slug doesn't match an active category, check category_redirects:
    --   found → 301 redirect to the correct URL with the new slug
    --   not found → 404
    -- Learning surface: articles sorted by published_at DESC (no time grouping)
    -- News surface: articles sorted by published_at DESC (with Today/Yesterday grouping in frontend)

GET /api/briefing
    ?type={daily_news|weekly_learning}  -- default "daily_news"
    ?date={YYYY-MM-DD}       -- optional, defaults to today (news) or current week's Monday (learning)
    Response: {
        type, date, brief,
        generated_at
    }
    -- Returns null brief if briefing not yet generated or task inactive

GET /api/categories
    ?surface={news|learning}  -- default "news"
    Response: [{ name, slug, article_count_today }]
    -- Sorted by display_order ASC — this is the order the frontend renders tabs
    -- For learning surface, article_count_today reflects the last 7 days instead
    -- Only includes categories where active = true

POST /api/events
    Body: { event_type, article_id?, category_slug?, surface?, session_id, referrer? }
    Response: 204 No Content
```

### Admin Endpoints (authenticated)

```
-- Sources
GET    /api/admin/sources
POST   /api/admin/sources
PUT    /api/admin/sources/:id
DELETE /api/admin/sources/:id           -- cascades: deletes all articles + fetch_logs for this source
POST   /api/admin/sources/:id/test-fetch   -- trigger=test, returns parsed articles without inserting
POST   /api/admin/sources/:id/refresh      -- trigger=manual, fetches + inserts + triggers classify

-- Batch Refresh
POST   /api/admin/refresh-all              -- triggers all active sources, returns batch_id
GET    /api/admin/refresh-status/:batch_id -- poll for batch progress (per-source status + classification)

-- Fetch Logs
GET    /api/admin/fetch-logs               -- paginated, filterable by source/status/trigger
GET    /api/admin/fetch-logs/:id           -- single log with full detail + error traceback
GET    /api/admin/sources/:id/fetch-logs   -- logs for a specific source

-- Pipeline Logs
GET    /api/admin/pipeline-logs      -- paginated, filterable by task/status/trigger

-- Categories
GET    /api/admin/categories
POST   /api/admin/categories
PUT    /api/admin/categories/:id
DELETE /api/admin/categories/:id
POST   /api/admin/categories/:id/preview  -- test description against recent articles before saving
PUT    /api/admin/categories/reorder    -- body: [{id, display_order}]
POST   /api/admin/categories/:id/merge  -- body: {target_id} — reassign articles, create redirect, delete source
POST   /api/admin/reclassify            -- body: {since: "24h" | "7d", surface?: "news" | "learning"}
POST   /api/admin/cache/flush           -- invalidate reader-facing caches (categories, headlines) for instant visibility

-- LLM Models
GET    /api/admin/models                -- list all registered models with status + pricing
POST   /api/admin/models                -- register a new model
PUT    /api/admin/models/:id            -- update model config, pricing, active status
DELETE /api/admin/models/:id            -- remove a model (fails if assigned to an active task)
POST   /api/admin/models/:id/test       -- send a 3-article sample classification, return result + latency
GET    /api/admin/models/providers      -- list providers with API key status (configured? valid?)

-- Pipeline Tasks
GET    /api/admin/tasks                 -- list all pipeline tasks with assigned models + status
PUT    /api/admin/tasks/:task           -- update task model assignment, active toggle, config
GET    /api/admin/tasks/cost-estimate   -- projected cost per task based on recent volume

-- Briefings (news + learning)
GET    /api/admin/briefings             -- list recent briefings (both types) with generation metadata
POST   /api/admin/briefings/regenerate  -- body: {type: "daily_news" | "weekly_learning"} — regenerate on demand

-- Articles
GET    /api/admin/articles              -- with search, filters, pagination
PUT    /api/admin/articles/:id          -- update hidden, manual category overrides
POST   /api/admin/articles/bulk         -- bulk actions

-- Analytics
GET    /api/admin/analytics/overview    -- summary metrics
GET    /api/admin/analytics/top-headlines?period=7d
GET    /api/admin/analytics/by-source?period=7d
GET    /api/admin/analytics/by-category?period=7d
GET    /api/admin/analytics/by-hour?period=7d

-- System
GET    /api/admin/system/status         -- pipeline health (derived from fetch_logs + pipeline_logs)
GET    /api/admin/system/errors         -- recent errors from fetch_logs + pipeline_logs
```

### Caching Strategy

- `GET /api/headlines?surface=news`: Cache for 2 minutes (news sources fetched every 15 min, 2-min cache balances freshness and load)
- `GET /api/headlines?surface=learning`: Cache for 30 minutes (learning sources fetched every 6-12h — longer cache is fine)
- `GET /api/categories`: Cache for 10 minutes
- Admin endpoints: No caching
- Cache implementation: HTTP Cache-Control headers + optional Redis if needed

---

## 6. Architecture Principles

These principles govern how every module is structured. They're the contract between "what the system does" (above) and "how it's built" (below). When in doubt about an implementation decision, defer to these.

### Vertical slices, not horizontal layers

Do not organize code as controller → service → repository layers that cut horizontally across the entire app. Organize as **vertical modules** — scraper, classifier, reader, admin — where each module owns its routes, its business logic, and its data access.

```
 ❌ Horizontal layers                    ✅ Vertical slices

 ┌──────────────────────┐               ┌─────────┬─────────┬─────────┬─────────┐
 │     Controllers      │               │ Scraper │ Classif.│ Reader  │  Admin  │
 ├──────────────────────┤               │         │         │         │         │
 │      Services        │               │  route  │  route  │  route  │  route  │
 ├──────────────────────┤               │  logic  │  logic  │  logic  │  logic  │
 │    Repositories      │               │  query  │  query  │  query  │  query  │
 ├──────────────────────┤               └────┬────┴────┬────┴────┬────┴────┬────┘
 │       Models         │                    │   shared models & db   │
 └──────────────────────┘                    └────────────────────────┘
```

A vertical slice is self-contained: you can read, understand, test, and modify the scraper module without ever opening the classifier. The modules share database models and common utilities (database session, config, auth), but otherwise they don't reach into each other.

**Why this matters here specifically:** This project has four genuinely independent concerns — fetching feeds, classifying articles, serving headlines, and managing the system. They happen to share a database, but their logic doesn't overlap. Vertical slices match the natural shape of the problem.

**The one exception:** Triggering classification after a fetch completes. The scraper module calls into the classifier module at one well-defined point (after inserting new articles). This is an explicit, documented coupling — not a hidden dependency.

### Functions and modules over classes

Python's natural unit of organization is the module and the function, not the class. Use classes only when they earn their keep:

| Use classes for | Use functions for |
|---|---|
| SQLAlchemy models (ORM requires it) | Business logic (`scrape()`, `classify_batch()`, `dedup_batch()`) |
| Pydantic schemas (validation requires it) | Route handlers |
| Adapters with shared interface (polymorphism) | Data queries and transformations |
| FastAPI router groups | Utility operations |

```python
# ✅ This — the scraper function from Section 4.1
async def scrape(
    db: AsyncSession,
    source: Source,
    trigger: str,
    batch_id: UUID | None = None,
) -> FetchResult:
    ...

# ❌ Not this
class ScraperService:
    def __init__(self, db: AsyncSession, adapter_registry: AdapterRegistry):
        self.db = db
        self.adapter_registry = adapter_registry

    async def scrape(self, source: Source, trigger: str, ...) -> FetchResult:
        ...
```

The `ScraperService` class adds a constructor, instance state, and a `self` parameter to every method — all ceremony, no value. The function version takes its dependencies as arguments and returns a result. It's shorter, clearer, and trivially testable.

**Where classes DO earn their keep:** The adapter pattern. `RSSAdapter`, `JSONAPIAdapter`, and `ScraperAdapter` share a `BaseAdapter` interface. This is textbook polymorphism — the right tool. But the `scrape()` function that *calls* the adapter remains a function.

### Explicit dependencies, no global state

Every function receives what it needs as arguments. No module-level singletons, no global database connections, no import-time side effects.

```python
# ✅ Dependencies as arguments — testable, explicit
@router.post("/admin/sources/{source_id}/refresh")
async def refresh_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    source = await get_source_or_404(db, source_id)
    result = await scrape(db, source, trigger="manual")
    return FetchResultResponse.from_result(result)

# ❌ Module-level singleton — hidden, untestable
_db = get_database()  # created at import time

@router.post("/admin/sources/{source_id}/refresh")
async def refresh_source(source_id: UUID):
    source = _db.query(Source).get(source_id)  # hidden dependency
    ...
```

FastAPI's `Depends()` is the mechanism for route handlers. For non-route functions (scraper, classifier), pass the session and config explicitly. This makes the dependency graph visible in the function signatures — you can trace what any function needs just by reading its parameters.

### Thin route handlers

A route handler does exactly three things:

1. **Parse and validate** the incoming request (FastAPI + Pydantic do this automatically)
2. **Call one business logic function** that does the actual work
3. **Map the result** to a response schema and return it

If a handler is longer than ~15 lines, extract the logic into a function in the module's business logic file. The handler should read like a table of contents, not like an implementation.

```python
# ✅ Thin — reads like a script
@router.post("/admin/refresh-all")
async def refresh_all(db: AsyncSession = Depends(get_db)):
    batch = await start_batch_refresh(db)      # one function does the work
    return BatchRefreshResponse.from_batch(batch)

# ❌ Fat — business logic embedded in the handler
@router.post("/admin/refresh-all")
async def refresh_all(db: AsyncSession = Depends(get_db)):
    last_batch = await get_last_batch(db)
    if last_batch and (now() - last_batch.started_at).seconds < 60:
        raise HTTPException(429, "Cooldown active")
    batch_id = uuid4()
    sources = await db.execute(select(Source).where(Source.active == True))
    tasks = []
    for source in sources.scalars():
        running = await db.execute(...)
        if not running.first():
            tasks.append(scrape(db, source, "batch", batch_id))
    # ... 30 more lines ...
```

### Interfaces at integration points only

Define abstract interfaces (base classes, `Protocol` types) **only** where the system touches something external or where multiple implementations exist today:

| Integration point | Interface | Implementations |
|---|---|---|
| Source adapters | `BaseAdapter.fetch(source) → AdapterResult` | `RSSAdapter`, later `JSONAPIAdapter`, `ScraperAdapter` |
| LLM classification | `classify_<provider>(articles, categories, model_id, api_key, config) → ClassificationResult` | `classify_anthropic`, `classify_openai`, `classify_google` — dispatched via model registry |
| Database session | `Depends(get_db)` | Production async session, test session |

**Do NOT create interfaces for things with one implementation.** No `IArticleRepository`, no `ICategoryService`, no `IFetchLogger`. A function with type hints is sufficient. If a second implementation appears someday, extract the interface then — it's a 10-minute refactor, not a regret.

```python
# ✅ Direct — one implementation, no interface needed
async def get_headlines(
    db: AsyncSession,
    category_slug: str | None = None,
    page: int = 1,
    per_page: int = 30,
) -> tuple[list[Article], int]:
    query = select(Article).where(Article.hidden == False)
    if category_slug:
        query = query.join(ArticleCategory).join(Category).where(Category.slug == category_slug)
    ...

# ❌ Over-abstracted — interface for a single implementation
class IHeadlineRepository(ABC):
    @abstractmethod
    async def get_headlines(self, category_slug: str | None, page: int, per_page: int) -> ...:
        ...

class PostgresHeadlineRepository(IHeadlineRepository):
    async def get_headlines(self, ...):
        ...  # the only implementation that will ever exist
```

### Configuration lives in the database

Everything that the admin might want to change without a deploy is stored in the database and editable through the admin panel:

- **Sources**: which feeds to fetch, how often, with what adapter
- **Categories**: what to classify into, and how (via the `description` field injected into the LLM prompt)
- **Fetch intervals**: per source
- **Display order**: category ordering on the reader site

Code is agnostic to specific sources and categories. The classifier doesn't contain a hardcoded list of categories — it loads them from the DB at prompt-build time. The scraper doesn't know which feeds exist — it processes whatever the admin has configured.

**The test:** Can you add a new source, a new category, or change a classification description without touching code or redeploying? If yes, the boundary is right.

Application-level config (database URL, API keys, port numbers) lives in environment variables via `.env`. Editorial config (sources, categories) lives in the database. Never mix these two.

### Every operation is logged and observable

No SSH-and-grep debugging. Every fetch writes to `fetch_logs`. Every classification batch writes to `pipeline_logs`. These records aren't just an audit trail — they power the admin dashboard, the health monitoring, and the cost tracking.

This is a design principle, not an implementation detail:

- The admin should never have to ask "did the Bloomberg fetch run last night?" — they look at the dashboard.
- You should never have to ask "why are there no articles from the last 3 hours?" — the fetch logs tell you whether it was a 403, a timeout, or a parse failure.
- You should never have to guess LLM costs — the classification logs track tokens and estimated cost per batch.

**Corollary:** The scraper and classifier functions **never throw exceptions to the caller.** They catch everything internally, record it in the log, and return a result with a status. The scheduler must never crash because one source returned a 500.

### Fail in isolation

One source failing must not affect other sources. One article failing classification must not stop the batch. One bad feed parse must not crash the fetch.

```python
# ✅ Fail in isolation — each source is independent
for source in active_sources:
    try:
        result = await scrape(db, source, trigger="scheduled")
    except Exception as e:
        logger.error(f"Unexpected error scraping {source.slug}: {e}")
        # Continue to next source

# ❌ All-or-nothing — one failure kills the batch
results = await asyncio.gather(*[
    scrape(db, s, trigger="scheduled") for s in active_sources
])
# If one raises, gather() propagates the exception. All results lost.
```

Use `asyncio.gather(return_exceptions=True)` when running concurrent operations, or wrap each in individual try/except. **Partial success is always better than total failure.**

This principle applies recursively: within a single fetch, if one article out of 20 fails to parse, the other 19 should still be inserted. The fetch log records `articles_failed=1`, and the admin can investigate.

### Types at the boundaries, pragmatism inside

Enforce strong types at the three system boundaries:

| Boundary | Mechanism | Rule |
|---|---|---|
| **API** (request/response) | Pydantic models | Every endpoint has explicit request and response schemas. No raw `dict` in, no raw `dict` out. |
| **Database** (read/write) | SQLAlchemy models | Proper column types, foreign keys, constraints. The schema is the contract. |
| **Frontend** (API consumption) | TypeScript types | Every API response has a corresponding TypeScript type. No `any`. |

Between boundaries, use whatever is clearest. A `dataclass` for internal results, a `TypedDict` for ad-hoc structures, a plain tuple for simple returns. Don't build elaborate internal type hierarchies for data that never crosses a boundary.

```python
# ✅ Typed at the boundary
class FetchResultResponse(BaseModel):
    fetch_log_id: UUID
    status: str
    articles_new: int
    articles_skipped: int
    duration_ms: int

# Internally, a simple dataclass is fine
@dataclass
class FetchResult:
    fetch_log_id: UUID
    status: str
    articles_new: int = 0
    articles_skipped: int = 0
    duration_ms: int = 0
    articles: list[RawArticle] | None = None  # only for test fetches
```

### No premature abstraction

Do not build:

- A generic "pipeline framework" for two pipelines (fetch and classify)
- An "event bus" for "call the classifier after the scraper finishes"
- A "plugin system" for a dict mapping adapter type strings to classes
- A "notification service" for one Slack webhook

Build the concrete thing first. If a pattern emerges across **three or more** instances, extract the abstraction then. Two is a coincidence, three is a pattern.

```python
# ✅ Direct and clear — this is the whole "adapter registry"
ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {
    "rss": RSSAdapter,
}

def get_adapter(adapter_type: str) -> BaseAdapter:
    cls = ADAPTER_REGISTRY.get(adapter_type)
    if not cls:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
    return cls()
```

If `JSONAPIAdapter` and `ScraperAdapter` arrive later, they get added to the dict. If the dict grows to 10 entries and needs auto-discovery, refactor then. Not before.

### Frontend: server-first, component-focused

The Next.js frontend follows the same modularity principles, adapted for React:

**Server Components by default.** The reader site is entirely server-rendered — headlines are fetched at request time (with caching), rendered to HTML, and sent to the browser. Client Components (`"use client"`) are used only where interactivity is required: category tab switching, analytics event firing, admin panel forms.

**Components are focused and composable.** Each component does one thing:

| Component | Responsibility |
|---|---|
| `SurfaceNav` | Renders the top-level News/Learning surface tabs (auto-generated from `SURFACES` registry) |
| `HeadlineItem` | Renders one headline — config-driven: summary, time format, and "Also in:" display controlled by `SurfaceConfig` booleans, not surface-specific branches |
| `HeadlineList` | Renders a list of `HeadlineItem`s with section headers — grouping strategy (`"time"` or `"topic"`) comes from config |
| `LeadHeadline` | Renders the lead headline at larger type — parent decides whether to render based on `config.showLeadHeadline` |
| `CategoryNav` | Renders the category tab bar — fetches categories for `config.categoryApiSurface`, renders in API-returned order |
| `EditorialSummary` | Renders editorial content above headlines — one component for all surfaces, driven by `config.briefingType` and `config.briefingLabel` |
| `SectionLabel` | Renders section headers ("TODAY", "STRATEGY") — pure presentational |
| `Pagination` | Renders the "More headlines" text link |

**No component contains surface-specific branching** (`if surface === 'learning'`). All behavioral differences between surfaces flow through `SurfaceConfig` — see the surface configuration registry below.

Components receive data as props. They do not fetch data themselves (Server Components fetch in the page, Client Components receive via props or use SWR/React Query for polling in admin).

**Surface configuration registry** (`lib/surfaces.ts`). A surface is a configuration object, not a prop that triggers conditional branches. The `SurfaceConfig` type captures every behavioral difference between surfaces:

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
```

Adding a third surface (e.g., "Research") means adding one entry to `SURFACES`, one page file, and optionally one `[data-surface]` CSS override block. Zero existing components are modified.

**Single API client module.** All backend calls go through `lib/api.ts`. No raw `fetch()` calls scattered across components. This is the frontend equivalent of "explicit dependencies" — when the API changes, you update one file.

**Admin and Reader are separate route groups** (`(reader)` and `admin/`) with separate layouts, but they share foundational components (typography primitives, the API client, common types). The admin layout has a sidebar and auth protection; the reader layout has the masthead and category nav. Each surface page is a thin adapter — it resolves the `SurfaceConfig` and delegates to a shared `SurfacePage` component.

### CSS architecture: three-layer design tokens + Tailwind

The visual design in Section 2.1 defines exact colors, type sizes, spacing, and layout values. Those values must live in a structured system and flow into every component through a single mechanism. If changing the accent color requires editing 30 files, the architecture has failed. If adding dark mode requires doubling every color class, the architecture has failed. If adding a new surface requires editing existing components' CSS, the architecture has failed.

**The principle: every visual decision is a token. Tokens flow through three layers — primitives → semantic → component. Tailwind consumes the component layer. Components never contain raw values.**

**Why three layers, not one flat file?** A single `tokens.css` works until you need a second surface, a third theme, or a component variant. Then you're either duplicating values or adding surface-specific overrides with no structure to hang them on. Three layers solve this:

| Layer | Named by | Changes when | Example |
|-------|----------|-------------|---------|
| **Primitives** | What they ARE | Brand evolves | `--gray-900: #1A1A1A` |
| **Semantic** | What they DO | Theme changes (dark mode) | `--color-text-primary: var(--gray-900)` |
| **Component** | Where they're USED | Surface or variant changes | `--headline-color: var(--color-text-primary)` |

Adding a new surface means adding a `[data-surface="x"]` block that overrides component tokens. Adding dark mode means overriding semantic tokens. Changing the brand means editing primitives. Each concern has one place to go.

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

**Three-state dark mode behavior:**
1. **No `data-theme` attribute** → follows OS preference via `prefers-color-scheme` (the default)
2. **`data-theme="dark"`** → always dark, regardless of OS
3. **`data-theme="light"`** → always light, the `:not([data-theme="light"])` selector in `@media` prevents the OS override

This is the most robust pattern. It respects the user's OS setting by default, but allows manual override. The toggle stores the preference in `localStorage` and applies the `data-theme` attribute to `<html>` on page load (a tiny inline script in `<head>` to prevent flash of wrong theme).

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

`@font-face` declarations — separated from tokens because font files are a loading concern, not a design decision.

```css
@font-face {
  font-family: 'GT Sectra';
  src: url('/fonts/GTSectra-Medium.woff2') format('woff2');
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'GT Sectra';
  src: url('/fonts/GTSectra-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-Variable.woff2') format('woff2');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

`font-display: swap` ensures the page renders immediately with the fallback font (Georgia / system-ui), then swaps in the custom font when loaded. No blank text, no layout shift (if the fallback is size-matched well).

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

#### What this makes easy

| Change | What you edit | Files touched |
|---|---|---|
| Change accent color | `--ink-blue` in `primitives.css` | 1 |
| Add dark mode | Already done at semantic layer | 0 (components unchanged) |
| Change headline font to Freight Text | `--font-serif` in `primitives.css` + swap font files | 2 |
| Make headlines slightly larger | `--headline-size` in `components.css` | 1 |
| Add "high contrast" theme | New `[data-theme]` block in `semantic.css` | 1 |
| New surface with different headline treatment | New `[data-surface]` block in `components.css` | 1 |
| Change max content width | `--width-content` in `primitives.css` | 1 |
| Change divider style from solid to dotted | One `border-style` in `globals.css` base layer | 1 |

#### What NOT to do

**No CSS Modules.** CSS Modules (`.module.css` files per component) add import ceremony and generate hashed class names. Useful in large multi-team codebases where class name collisions are a real risk. Unnecessary here — Tailwind utilities don't collide, and component-scoped styles are better handled by the React components themselves.

**No CSS-in-JS.** Styled-components, Emotion, etc. add runtime cost, complicate server rendering, and create a second styling language alongside Tailwind. Pick one system, not two.

**No `@apply` for component classes.** Using `@apply` to create `.headline-item { @apply font-serif text-headline text-primary ... }` defeats Tailwind's purpose and creates a shadow class system. If a pattern repeats, extract a React component — the component IS the abstraction.

```tsx
// ✅ The React component is the abstraction
function HeadlineItem({ title, source, time, url }: Props) {
  return (
    <a href={url} target="_blank" rel="noopener"
       className="block group">
      <h2 className="font-serif text-headline text-headline
                     group-hover:text-headline-hover transition-colors">
        {title}
      </h2>
      <p className="text-meta text-meta mt-1">
        {source} · {time}
      </p>
    </a>
  );
}

// ❌ Don't extract a CSS class for this
// .headline-item h2 { @apply font-serif text-headline text-headline; }
// .headline-item:hover h2 { @apply text-headline-hover; }
```

**No raw hex/rgb values in component markup.** If you catch yourself writing `text-[#1A1A1A]` or `bg-[#FAF9F7]` in a component, stop — that value should be a token in `primitives.css`, mapped through semantic → component layers → Tailwind. The only place raw color values appear is in `primitives.css`.

**No Tailwind `dark:` variant classes.** The variable-swap approach means you never need `dark:bg-gray-900 dark:text-white`. Every `bg-surface` and `text-primary` automatically resolves correctly in both themes. Using `dark:` would create a parallel styling system that fights the token architecture.

---

## 7. Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend API** | Python + FastAPI | Async-native, great for I/O-heavy work (fetching feeds, calling LLM API). Strong typing with Pydantic. Large ecosystem for RSS parsing (feedparser), HTTP (httpx). |
| **Database** | PostgreSQL | JSONB for flexible adapter configs. Window functions for analytics queries. Reliable. |
| **ORM / Queries** | SQLAlchemy 2.0 (async) | Mature, well-documented, good migration support with Alembic. |
| **Task Scheduling** | APScheduler | Lightweight, in-process scheduler. Sufficient for <20 sources with staggered fetches. Graduate to Celery + Redis only if scaling beyond a single process. |
| **LLM** | Multi-provider: Anthropic (Claude), OpenAI (GPT), Google (Gemini) | Model registry + pipeline task assignment. Classification: Haiku 4.5. Briefing: Sonnet 4.6. Admin can reassign any model to any task. |
| **Reader Frontend** | Next.js (App Router) | Server-side rendering for fast first paint and SEO. React ecosystem for the admin panel. Single framework for both surfaces. |
| **Admin Frontend** | Next.js (same app, `/admin` routes) | Shared components, single deployment. Protected by middleware auth check. |
| **Styling** | Tailwind CSS | Utility-first, fast to build clean layouts without fighting a component library. |
| **Deployment** | Docker Compose on a VPS | Simple, predictable, cheap. One compose file runs: API, worker (scheduler + fetcher + classifier), Postgres, and Next.js. |
| **Reverse Proxy** | Caddy or Nginx | Automatic HTTPS via Let's Encrypt. Serves as the entry point. |

### Project Structure

```
headlines/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS, middleware
│   │   ├── config.py                # Settings from env vars
│   │   ├── database.py              # SQLAlchemy engine, session
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── source.py
│   │   │   ├── category.py
│   │   │   ├── article.py
│   │   │   ├── fetch_log.py
│   │   │   ├── pipeline_log.py
│   │   │   ├── llm_model.py
│   │   │   ├── pipeline_task.py
│   │   │   ├── briefing.py
│   │   │   └── analytics.py
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── headlines.py         # Public API
│   │   │   ├── admin_sources.py
│   │   │   ├── admin_categories.py
│   │   │   ├── admin_articles.py
│   │   │   ├── admin_models.py          # LLM model registry CRUD + test
│   │   │   ├── admin_tasks.py          # Pipeline task assignment + briefing management
│   │   │   ├── admin_analytics.py
│   │   │   └── events.py            # Analytics event ingestion
│   │   ├── adapters/
│   │   │   ├── base.py              # BaseAdapter abstract class
│   │   │   ├── rss.py               # RSSAdapter
│   │   │   └── registry.py          # adapter_type → Adapter class mapping
│   │   ├── llm/
│   │   │   ├── registry.py          # provider string → adapter function mapping
│   │   │   ├── anthropic.py         # Anthropic Messages API adapter
│   │   │   ├── openai.py            # OpenAI Chat Completions adapter
│   │   │   ├── google.py            # Google Generative AI adapter
│   │   │   └── types.py             # ClassificationResult, BriefingResult, shared types
│   │   ├── classifier/
│   │   │   ├── classifier.py        # Orchestrates classification batches (reads task model, calls provider)
│   │   │   └── prompts.py           # Classification prompt templates (provider-agnostic)
│   │   ├── dedup/
│   │   │   ├── similarity.py        # Phase 1: fast title similarity (Jaccard on normalized tokens)
│   │   │   ├── deduplicator.py      # Phase 2: LLM confirmation + cluster management
│   │   │   └── prompts.py           # Dedup prompt templates (same-story vs same-topic distinction)
│   │   ├── editorial/
│   │   │   ├── briefing.py          # The Brief: daily news thematic summary generation
│   │   │   ├── learning_digest.py   # The Learning Digest: weekly learning summary generation
│   │   │   ├── analysis.py          # (deferred) In Focus: top story cross-source synthesis
│   │   │   └── prompts.py           # Editorial prompt templates (news + learning)
│   │   ├── scraper/
│   │   │   └── scraper.py           # The scraper function: scrape(source, trigger)
│   │   ├── workers/
│   │   │   ├── scheduler.py         # APScheduler setup
│   │   │   ├── fetch_worker.py      # Calls scraper for each due source
│   │   │   ├── classify_worker.py   # Batch classification with logging
│   │   │   ├── dedup_worker.py      # Story dedup: similarity → LLM confirm → cluster
│   │   │   ├── editorial_worker.py  # Daily briefing generation
│   │   │   └── retention_worker.py  # Cleanup: old articles, logs, briefings
│   │   └── auth/
│   │       └── admin.py             # Admin authentication
│   ├── alembic/                     # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout (imports globals.css, theme detection script)
│   │   ├── (reader)/                # Route group — shared reader layout
│   │   │   ├── layout.tsx           # Masthead + SurfaceNav + footer (shared)
│   │   │   ├── page.tsx             # News surface → passes SURFACES.news to SurfacePage
│   │   │   ├── [category]/
│   │   │   │   └── page.tsx         # News category filter
│   │   │   └── learning/
│   │   │       ├── page.tsx         # Learning surface → passes SURFACES.learning to SurfacePage
│   │   │       └── [category]/
│   │   │           └── page.tsx     # Learning category filter
│   │   └── admin/
│   │       ├── layout.tsx           # Admin layout with sidebar nav
│   │       ├── page.tsx             # Admin dashboard
│   │       ├── sources/
│   │       ├── categories/
│   │       ├── articles/
│   │       ├── models/              # LLM model registry management
│   │       └── analytics/
│   ├── components/
│   │   ├── SurfacePage.tsx          # Shared surface page — composes all reader components from config
│   │   ├── SurfaceNav.tsx           # Top-level News/Learning surface tabs (auto from SURFACES registry)
│   │   ├── EditorialSummary.tsx     # Editorial content (The Brief / The Learning Digest — config-driven)
│   │   ├── HeadlineList.tsx         # Headline list with config-driven grouping (time or topic)
│   │   ├── HeadlineItem.tsx         # Single headline — config-driven (summary, time format, "Also in:")
│   │   ├── LeadHeadline.tsx         # Lead headline at larger type (rendered when config.showLeadHeadline)
│   │   ├── CategoryNav.tsx          # Category tab bar (fetches per config.categoryApiSurface)
│   │   ├── SectionLabel.tsx         # Section headers ("TODAY", "STRATEGY") — pure presentational
│   │   ├── Pagination.tsx
│   │   ├── ThemeToggle.tsx          # Light/dark mode toggle
│   │   └── admin/                   # Admin-specific components
│   ├── styles/
│   │   ├── tokens/
│   │   │   ├── primitives.css       # Raw palette: colors, sizes, spaces (named by what they ARE)
│   │   │   ├── semantic.css         # Role mapping + dark mode swap (named by what they DO)
│   │   │   └── components.css       # Component tokens + surface overrides (named by WHERE)
│   │   ├── typography.css           # @font-face declarations
│   │   └── globals.css              # Imports all layers, Tailwind directives, base styles
│   ├── lib/
│   │   ├── api.ts                   # Single API client — typed fetch wrappers
│   │   ├── surfaces.ts              # Surface config registry (SurfaceConfig type + SURFACES map)
│   │   ├── types.ts                 # TypeScript types mirroring Pydantic schemas
│   │   ├── grouping.ts              # Headline grouping strategies (groupByTime, groupByTopic)
│   │   ├── time.ts                  # Time formatting (relative, date)
│   │   └── analytics.ts             # Client-side event tracking + session management
│   ├── public/
│   │   └── fonts/                   # .woff2 font files (GT Sectra, Inter)
│   ├── tailwind.config.ts           # Maps component tokens → Tailwind utility classes
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── DESIGN.md                        # This file
```

---

## 8. Initial Source Configuration

Starting sources and their RSS feeds, organized by surface:

### News Sources (`surface = 'news'`)

| Source | Feed URL | Fetch Interval | Notes |
|--------|----------|----------------|-------|
| Financial Times | `https://www.ft.com/rss/home` | 15 min | Free RSS with headlines + short summaries. Paywalled articles — but we only need the headline. |
| Bloomberg | `https://feeds.bloomberg.com/markets/news.rss` (and other section feeds) | 15 min | Multiple section-specific feeds. May want to add 2-3 Bloomberg feeds as separate sources or one combined. |
| The Wall Street Journal | `https://feeds.a.dj.com/rss/RSSWorldNews.xml` (and other section feeds) | 15 min | Section-specific feeds. Similar to Bloomberg — may want multiple feeds. |
| The Verge | `https://www.theverge.com/rss/index.xml` | 30 min | Full feed, reliable, good metadata. |
| Stratechery | `https://stratechery.com/feed/` | 120 min | ~1 post/day. The best tech strategy analysis available. Low volume, high signal. Free articles on the public feed; Daily Updates require subscriber feed URL (configured by admin). |

### Learning Sources (`surface = 'learning'`)

| Source | Feed URL | Fetch Interval | Notes |
|--------|----------|----------------|-------|
| Harvard Business Review | `https://hbr.org/rss` | 360 min (6h) | Publishes 3-5 articles/day on the web. Excellent RSS with titles, summaries, and author info. Articles are evergreen management/strategy content — the summary field is especially valuable here, as HBR titles are often conceptual ("The Strategic Implications of...") and benefit from the subtitle context. Paywalled articles — but headline + summary is sufficient for the Learning surface. |
| MIT Sloan Management Review | `https://sloanreview.mit.edu/feed/` | 720 min (12h) | Publishes 2-4 articles/week. Research-backed management insights. Lower volume than HBR but equally high quality. Feed includes good summaries. Content focuses on technology strategy, organizational design, leadership, and data-driven management — strong complement to HBR's broader management coverage. |

**Why these fetch intervals?** News sources need frequent polling because financial headlines go stale in hours. Learning sources publish infrequently (HBR: ~3-5/day, MIT SMR: ~3-4/week) and the content is evergreen — a 6-hour lag on an HBR article is imperceptible. Conditional fetching (ETags/304) means most learning source checks return instantly.

**Note on feed URLs**: These may change or require validation. The "Test fetch" feature in admin is critical — verify each feed works before activating.

**Expansion candidates** (add later via admin):
- **News**: Reuters, AP News, TechCrunch, Ars Technica, The Economist, Politico, Hacker News (has an API adapter opportunity)
- **Learning**: McKinsey Quarterly, Stanford Social Innovation Review, INSEAD Knowledge, Wharton@Work — all publish management/strategy content with RSS feeds

---

## 9. Initial Category Configuration

Two category sets — one per surface. Both are fully modular — add, remove, rename, or reorder via admin panel. The LLM prompt rebuilds from DB on every classification run, filtered by the article's source surface.

### News Categories (`surface = 'news'`)

Nine categories for classifying news headlines:

| Category | Slug | Description (for LLM) | Display Order |
|----------|------|----------------------|---------------|
| Economy | `economy` | Macroeconomic trends, GDP, inflation, unemployment, economic policy, fiscal policy, economic indicators, recessions, growth forecasts, labor markets, trade balances, economic outlook | 1 |
| Markets | `markets` | Stock markets, bonds, commodities, forex, interest rates, central bank policy (Fed, ECB, BoE), trading, IPOs, earnings reports, market analysis, investor sentiment, fund flows | 2 |
| Tech | `tech` | Technology companies, products, software, hardware, artificial intelligence, machine learning, startups, gadgets, consumer electronics, apps, social media platforms, cybersecurity, cloud computing | 3 |
| Politics | `politics` | Political campaigns, legislation, government policy, partisan politics, elections, political analysis, lobbying, political appointments, congressional/parliamentary proceedings | 4 |
| US | `us` | United States domestic affairs — US economy, US policy, US society, US events. Stories primarily about what is happening inside America, including federal and state-level news | 5 |
| Europe | `europe` | European affairs — EU policy, European economies, European politics, events in European countries. Stories primarily about what is happening in Europe, including UK post-Brexit | 6 |
| World | `world` | International affairs outside US and Europe — Asia, Middle East, Africa, Latin America, global diplomacy, wars and conflicts, international organizations (UN, NATO), global health, climate policy | 7 |
| Business | `business` | Corporate strategy, mergers and acquisitions, executive appointments, company earnings, industry trends, regulation, antitrust, supply chains, entrepreneurship, corporate governance | 8 |
| Opinion | `opinion` | Editorials, op-eds, columns, analysis and commentary pieces. Often identifiable by URL patterns (/opinion/, /editorial/) or by the presence of a prominent columnist byline | 9 |

**Note on geographic vs topical categories**: An article can be both geographic and topical. "Fed raises rates" → `us` + `economy` + `markets`. "EU bans TikTok" → `europe` + `tech` + `politics`. The multi-label system handles this naturally.

### Learning Categories (`surface = 'learning'`)

Eight categories for classifying management and strategy articles from HBR and MIT SMR:

| Category | Slug | Description (for LLM) | Display Order |
|----------|------|----------------------|---------------|
| Strategy | `strategy` | Corporate strategy, competitive advantage, business models, strategic planning, disruption, industry analysis, value creation, market positioning, diversification, growth strategy, strategic decision-making | 1 |
| Leadership | `leadership` | Leadership development, executive decision-making, management practices, team building, organizational leadership, influence, coaching, emotional intelligence, leading through change, C-suite challenges | 2 |
| Innovation | `innovation` | Innovation management, R&D, product development, design thinking, creative processes, emerging business models, experimentation, intrapreneurship, disruptive innovation, corporate venturing | 3 |
| Technology & AI | `technology-ai` | Digital transformation, artificial intelligence in business, machine learning applications, automation, data-driven decision making, tech strategy, enterprise technology, AI adoption, algorithmic management | 4 |
| Operations | `operations` | Operations management, supply chain, process improvement, lean management, quality management, scaling operations, operational excellence, logistics, manufacturing, productivity systems | 5 |
| Marketing & Growth | `marketing-growth` | Marketing strategy, customer acquisition, branding, growth strategies, customer experience, market research, go-to-market, pricing strategy, consumer behavior, brand management | 6 |
| People & Culture | `people-culture` | Talent management, organizational culture, diversity and inclusion, employee engagement, hiring, workplace dynamics, remote work, organizational behavior, performance management, team dynamics | 7 |
| Entrepreneurship | `entrepreneurship` | Startups, venture capital, founding teams, scaling businesses, business planning, bootstrapping, founder lessons, lean startup methodology, fundraising, startup strategy | 8 |

**Note on multi-label for learning**: Like news, learning articles can span multiple categories. "How AI Is Transforming Talent Acquisition" → `technology-ai` + `people-culture`. "The Strategic Case for Building an Innovation Lab" → `strategy` + `innovation`. The same confidence threshold (≥ 0.5) and 1-3 category limit applies.

---

## 10. Initial Model Registry & Task Assignment

Six models registered across three providers, assigned to three pipeline tasks. The model registry is a catalog; the pipeline tasks table is where you assign models to jobs. Different tasks use different models — cheap models for classification, smarter models for editorial synthesis.

### Anthropic

| Model ID | Display Name | Input/MTok | Output/MTok | Context | Max Output | Notes |
|----------|-------------|------------|-------------|---------|------------|-------|
| `claude-haiku-4-5` | Claude Haiku 4.5 | $1.00 | $5.00 | 200K | 64K | **Classification default.** Fast, cheap, strong on structured output. The workhorse for categorization. |
| `claude-sonnet-4-6` | Claude Sonnet 4.6 | $3.00 | $15.00 | 200K (1M beta) | 64K | **Briefing default.** Stronger writing, better at nuance and thematic synthesis. Worth the premium for reader-facing prose. |

**Why Haiku for classification, Sonnet for briefing?** Classification is "read title + summary → assign categories" — pattern matching. Haiku handles this at 3x lower cost with near-identical accuracy. The briefing — writing a coherent thematic summary of the day's headlines — requires stronger reasoning and prose quality. Sonnet produces noticeably better synthesis. Opus 4.6 ($5/$25) is overkill for both tasks; register it manually via admin if you want to experiment.

**SDK**: `anthropic` Python package. Messages API with `tool_use` for structured JSON output (classification) and standard text generation (editorial). The adapter handles both modes.

### OpenAI

| Model ID | Display Name | Input/MTok | Output/MTok | Context | Max Output | Notes |
|----------|-------------|------------|-------------|---------|------------|-------|
| `gpt-5-mini` | GPT-5 Mini | $0.25 | $2.00 | 400K | 128K | Latest generation mid-tier. 4x cheaper than Haiku on input. Set `reasoning_effort: "none"` to disable reasoning. Structured output via `response_format: { type: "json_object" }`. |
| `gpt-5-nano` | GPT-5 Nano | $0.05 | $0.40 | 400K | 128K | Ultra-budget. 20x cheaper than Haiku on input. OpenAI recommends for classification and summarization. Cheapest option in the registry. |

**Why not GPT-5.4?** GPT-5.4 ($2.50/$15) is the latest flagship but massive overkill for classification. GPT-5 Mini handles structured output tasks at 10x lower cost. The admin can register GPT-5.4 (or GPT-5, GPT-5.1, GPT-5.2) manually via the admin panel if they want to compare.

**Why not GPT-4.1?** The GPT-4.1 family (4.1, 4.1-mini, 4.1-nano) was retired from ChatGPT in February 2026 and faces API deprecation ~October 2026. The GPT-5 family is the current generation. GPT-5 models support a `reasoning_effort` parameter — set to `"none"` in the model's config JSONB to ensure pure non-reasoning behavior for classification.

**SDK**: `openai` Python package. Chat Completions API with `response_format: { type: "json_object" }` for reliable JSON parsing. Pass `reasoning_effort` from model config.

### Google

| Model ID | Display Name | Input/MTok | Output/MTok | Context | Max Output | Notes |
|----------|-------------|------------|-------------|---------|------------|-------|
| `gemini-2.5-flash` | Gemini 2.5 Flash | $0.30 | $2.50 | 1M | 65K | Stable/GA. Set `thinkingBudget: 0` in config to disable thinking. 3x cheaper than Haiku on input. |
| `gemini-2.5-flash-lite` | Gemini 2.5 Flash-Lite | $0.10 | $0.40 | 1M | 65K | Ultra-budget. Thinking OFF by default — true non-reasoning model. 10x cheaper than Haiku on input. Cost becomes negligible (~$0.01/day). |

**Why 2.5 and not 3.x?** Two reasons. First, the 3.x models (gemini-3-flash-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview) are still in preview as of March 2026. Second — and more importantly — the 3.x models cannot fully disable thinking (MINIMAL is the lowest setting), while 2.5-flash-lite has thinking OFF by default and 2.5-flash supports `thinkingBudget: 0` to disable it entirely. For classification, we want zero thinking overhead. The 2.5 series is stable/GA. The admin can register 3.x previews manually; when 3.x reaches GA with thinking fully disablable, update the seed data.

**SDK**: `google-genai` Python package. `generateContent` API with `response_mime_type: "application/json"` for structured output.

### Cost Breakdown by Task

**Classification** (~160 articles/day total — ~150 news + ~10 learning, ~22K input + ~5.5K output tokens/day):

| Model | Daily Cost | Monthly Cost | vs. Haiku |
|-------|-----------|-------------|-----------|
| Claude Haiku 4.5 | ~$0.05 | ~$1.40 | — |
| Claude Sonnet 4.6 | ~$0.14 | ~$4.20 | 3x more |
| GPT-5 Mini | ~$0.015 | ~$0.45 | 68% cheaper |
| GPT-5 Nano | ~$0.003 | ~$0.09 | 94% cheaper |
| Gemini 2.5 Flash | ~$0.02 | ~$0.49 | 65% cheaper |
| Gemini 2.5 Flash-Lite | ~$0.004 | ~$0.12 | 91% cheaper |

**Briefing** (1 briefing per day, ~9K input + ~150 output tokens/day):

| Model | Daily Cost | Monthly Cost | Notes |
|-------|-----------|-------------|-------|
| Claude Sonnet 4.6 | ~$0.03 | ~$0.90 | Default. Best prose quality for reader-facing content. |
| Claude Haiku 4.5 | ~$0.01 | ~$0.30 | Cheaper but noticeably weaker synthesis. |
| GPT-5 Mini | ~$0.003 | ~$0.09 | Viable alternative. Test quality before switching. |
| Gemini 2.5 Flash | ~$0.004 | ~$0.11 | Viable alternative. Test quality before switching. |

**Learning Digest** (1 digest per week, ~4K input + ~150 output tokens/week):

| Model | Weekly Cost | Monthly Cost | Notes |
|-------|-----------|-------------|-------|
| Claude Sonnet 4.6 | ~$0.01 | ~$0.05 | Default. Same quality rationale as news briefing. |
| Claude Haiku 4.5 | ~$0.005 | ~$0.02 | Cheaper but weaker synthesis. |

**Total pipeline (default assignment):**

| Task | Model | Monthly Cost |
|------|-------|-------------|
| Classification (news + learning) | Haiku 4.5 | ~$1.50 |
| Cross-source dedup | Haiku 4.5 | ~$0.30 |
| News Briefing | Sonnet 4.6 | ~$0.90 |
| Learning Digest | Sonnet 4.6 | ~$0.05 |
| **Total** | | **~$2.82** |

**Still cheap.** The entire pipeline — classification across both surfaces, cross-source dedup, daily news briefing, and weekly learning digest — costs ~$2.82/month. The dedup cost is low because Phase 1 (free title similarity) filters ~80% of articles before any LLM call. The model choice is about quality, not cost.

### Seed Data

Models and task assignments are inserted via the initial database migration (Alembic). The admin can add, remove, or reassign at any time through the admin panel.

```sql
-- Model registry (catalog of available models)
INSERT INTO llm_models (provider, model_id, display_name, active, input_price_per_mtok, output_price_per_mtok, context_window, max_output_tokens) VALUES
  ('anthropic', 'claude-haiku-4-5',        'Claude Haiku 4.5',        true, 1.00,   5.00, 200000, 64000),
  ('anthropic', 'claude-sonnet-4-6',       'Claude Sonnet 4.6',       true, 3.00,  15.00, 200000, 64000),
  ('openai',   'gpt-5-mini',               'GPT-5 Mini',              true, 0.25,   2.00, 400000, 128000),
  ('openai',   'gpt-5-nano',               'GPT-5 Nano',              true, 0.05,   0.40, 400000, 128000),
  ('google',   'gemini-2.5-flash',         'Gemini 2.5 Flash',        true, 0.30,   2.50, 1000000, 65000),
  ('google',   'gemini-2.5-flash-lite',    'Gemini 2.5 Flash-Lite',   true, 0.10,   0.40, 1000000, 65000);

-- Pipeline task → model assignment
INSERT INTO pipeline_tasks (task, model_id, active, config) VALUES
  ('classification',   'claude-haiku-4-5',  true, '{}'),
  ('dedup',            'claude-haiku-4-5',  true, '{"similarity_threshold": 0.35, "window_hours": 48, "max_candidates": 5}'),
  ('briefing',         'claude-sonnet-4-6', true, '{"max_sentences": 5}'),
  ('learning_digest',  'claude-sonnet-4-6', true, '{"max_sentences": 5}');
```

---

## 11. Deployment Architecture

### Single-VPS Setup (initial)

```
                    ┌─────────────────────────────────────┐
                    │            VPS (4GB RAM)             │
                    │                                      │
   Internet ──────▶│  Caddy (reverse proxy + HTTPS)       │
                    │    ├── headlines.example.com ──▶ Next.js (:3000)
                    │    └── headlines.example.com/api ──▶ FastAPI (:8000)
                    │                                      │
                    │  FastAPI (backend API)               │
                    │  Worker (scheduler + fetch + classify)│
                    │  PostgreSQL                           │
                    │  Next.js (frontend SSR)               │
                    └─────────────────────────────────────┘
```

**Docker Compose services:**

| Service | Image | Purpose |
|---------|-------|---------|
| `db` | postgres:16 | Database |
| `api` | backend Dockerfile | FastAPI app serving API |
| `worker` | backend Dockerfile (different entrypoint) | Background scheduler, fetcher, classifier |
| `frontend` | frontend Dockerfile | Next.js SSR |
| `caddy` | caddy:2 | Reverse proxy, auto-HTTPS |

**Environment variables** (`.env`):

```
DATABASE_URL=postgresql+asyncpg://headlines:password@db:5432/headlines
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_AI_API_KEY=AIza...
ADMIN_PASSWORD=...
NEXTAUTH_SECRET=...
BRIEFING_TIMEZONE=America/New_York
PUBLIC_API_URL=https://headlines.example.com/api
```

**LLM API keys**: All three provider keys are optional — only the keys for providers used by active pipeline tasks must be set. With the default assignment (Anthropic for both classification and editorial), only `ANTHROPIC_API_KEY` is required. If the admin reassigns a task to a model whose provider key is missing, the update endpoint returns an error. The admin UI shows key status per provider (configured/missing/invalid).

### Scaling Path (if needed later)

1. **More readers**: Put Cloudflare in front. The reader site is highly cacheable.
2. **More sources**: APScheduler handles ~50 sources easily in one worker. Beyond that, switch to Celery + Redis.
3. **More analytics**: Partition `analytics_events` by month. Or offload to a dedicated analytics service.
4. **High availability**: Move Postgres to managed (e.g., RDS, Neon). Run 2 API replicas behind a load balancer.

This is unlikely to be needed soon. A single VPS handles thousands of daily readers for a text-heavy site with proper caching.

---

## 12. Key Workflows

### Adding a New Source

1. Admin opens Sources page → clicks "Add Source"
2. Fills in: name, homepage URL, feed URL, **surface** (News or Learning), adapter type (rss), fetch interval
3. Clicks "Test Fetch" → system runs the adapter, displays sample articles
4. If results look good, clicks "Save" with active=true
5. Scheduler picks it up on the next cycle, starts fetching
6. New articles flow through surface-aware classification automatically (news categories for news sources, learning categories for learning sources)

**Time to add a source: ~2 minutes. Zero code changes.**

### Adding a New Category

1. Admin opens Categories page → clicks "Add Category"
2. Fills in: name (slug auto-generates), selects surface (News / Learning), writes description
3. Clicks "Preview" → system runs LLM on recent articles from that surface, shows what would be assigned
4. Tweaks description if needed, re-previews — this is a fast iteration loop (preview takes ~3 seconds)
5. Drags the new category to the desired position in the order
6. Saves → category is created with `active = true`
7. Category appears in reader navigation within ≤ 10 minutes (or immediately with cache flush)
8. Optionally triggers reclassification of last 24h or 7d of articles from that surface

**Time to add a category: ~5 minutes. Zero code changes.**

### Rearranging Categories

1. Admin opens Categories page
2. Drags categories within a surface group to the desired order
3. Order saves automatically (or on "Save Order" button)
4. Reader site reflects new tab order within ≤ 10 minutes (or immediately with cache flush)
5. No reclassification needed — ordering is display-only

**Time to rearrange: ~10 seconds. Zero code changes.**

### Renaming a Category

1. Admin edits the category name (e.g., "Tech" → "Technology & AI")
2. Slug remains unchanged by default (preserving `/tech` URLs)
3. If admin also changes the slug (e.g., `tech` → `technology-ai`), the system creates a redirect: `/tech` → `/technology-ai`
4. Reader site shows new name within ≤ 10 minutes (or immediately with cache flush)
5. No reclassification needed — name is display-only. If the admin also updated the description, reclassification is recommended.

**Time to rename: ~30 seconds. Zero code changes. Old URLs keep working.**

### Merging Two Categories

1. Admin selects a category and clicks "Merge into..."
2. Picks the target category from a dropdown (same surface only)
3. System shows: "X articles will be reassigned from [Source] to [Target]. The slug /source-slug will redirect to /target-slug."
4. Admin confirms → `article_categories` rows reassigned → redirect created → source category deleted
5. Reader site reflects the merge within ≤ 10 minutes (or immediately with cache flush)

**Time to merge: ~1 minute. Zero code changes. Old URLs redirect.**

### Switching a Task's Model

1. Admin opens LLM Models & Pipeline Tasks page → reviews per-task cost breakdown
2. Optionally clicks "Test" on the target model → verifies API key works and output looks correct
3. Changes the model dropdown for the desired task (e.g., classification or briefing)
4. Confirmation dialog shows cost delta → confirms → `pipeline_tasks.model_id` updates
5. Next run of that task uses the new model
6. Admin monitors quality in Articles page (classification) or Daily Briefings (editorial)

**Time to switch: ~30 seconds. Zero code changes. Zero restarts. Each task is independent — switching the classification model doesn't affect the editorial model.**

### Daily Operation (steady state)

```
News sources — every 15 minutes (automatic, per source's fetch_interval):
  - Scheduler calls scrape(source, trigger="scheduled")
  - Scraper: fetch RSS (conditional — 304 if unchanged) → dedup → insert → write fetch_log
  - Classifier picks up unclassified batch → calls LLM with news categories
    → writes categories → writes pipeline_log
  - Dedup runs on newly classified articles → clusters same-story duplicates
    → marks non-representatives → writes pipeline_log (task='dedup')

Learning sources — every 6-12 hours (per source's fetch_interval):
  - Same scrape() flow as news
  - Classifier picks up unclassified batch → calls LLM with learning categories
    → writes categories → writes pipeline_log
  - Dedup runs on newly classified articles (less common for learning — HBR/MIT SMR rarely overlap)

Once daily (after first morning classification):
  - Editorial worker checks if briefing task is active
  - If active: generates The Brief from last 24h of classified news articles (representatives only)
    → stores in briefings (type='daily_news') → writes pipeline_log (task='briefing')
  - News surface shows The Brief above categorized headlines

Once weekly (Monday morning):
  - Editorial worker checks if learning_digest task is active
  - If active: generates The Learning Digest from last 7 days of classified learning articles
    → stores in briefings (type='weekly_learning') → writes pipeline_log (task='learning_digest')
  - Learning surface shows The Learning Digest above topic-grouped articles

On demand (admin):
  - "Refresh All" / per-source "Refresh" → same scrape() + classify + dedup flow (surface-aware)
  - "Regenerate Briefing" → re-runs news briefing or learning digest for current period
  - Reader site updated within minutes

Daily cleanup:
  - Retention worker removes articles older than 30 days
  - Retention worker removes briefings older than 30 days
  - Retention worker removes fetch_logs and pipeline_logs older than 90 days
  - Admin optionally reviews "Uncategorized" articles (both surfaces)
  - Analytics dashboard shows previous day's engagement (both surfaces)
```

---

## 13. Resolved & Open Design Questions

### Resolved

1. **Source content depth**: Headlines + short summaries are sufficient. No need to fetch full article text.
2. **Category set**: Two sets by surface — 9 news categories (Economy, Markets, Tech, Politics, US, Europe, World, Business, Opinion) and 8 learning categories (Strategy, Leadership, Innovation, Technology & AI, Operations, Marketing & Growth, People & Culture, Entrepreneurship). Both modular — changeable via admin panel.
3. **Fetch interval**: Every 15 minutes (default for news). Per-source configuration via admin — financial news sources at 15 min, analysis sources (Stratechery) at 120 min, learning sources at 6-12h. Conditional fetching with HTTP ETags keeps frequent polling polite and efficient.
4. **Reader auth**: None. Fully public. No login, no cookies beyond anonymous analytics session.
5. **Multi-label display**: Yes — an article in both "Markets" and "Tech" appears in both tabs. This is correct. Same for learning: an article in "Strategy" and "Innovation" appears in both.
6. **Cross-source dedup**: Cluster and deduplicate. When Bloomberg, FT, and WSJ all cover the same story, the reader shows one representative headline with "Also in: Bloomberg, Financial Times" beneath it. All articles are stored — nothing is deleted — but only representatives are shown. A two-phase pipeline (fast title similarity → LLM semantic confirmation) detects duplicates after classification. The admin can override representative selection or disable dedup entirely. See §4.2.2.
7. **LLM provider lock-in**: Avoided. Multi-provider model registry with task-based assignment. Any model can be assigned to any task. Anthropic, OpenAI, and Google adapters. Prompts are provider-agnostic.
8. **Single model vs. multi-model**: Different tasks use different models. Classification (structured output) uses Haiku for cost. Editorial synthesis (reader-facing prose) uses Sonnet for quality. The `pipeline_tasks` table makes this a configuration choice, not an architectural one.
9. **News vs. learning as separate surfaces**: Yes. HBR/MIT SMR content is fundamentally different from news — evergreen, topic-organized, summary-visible, weekly-digested. Mixing them into a single feed would create a jarring reading experience. The `surface` column on `sources` and `categories` cleanly separates the two content types while sharing all infrastructure (pipeline, admin, analytics).

### Still Open

1. **Domain name**: What domain will this run on?
2. **Breaking news / priority**: Should certain articles be pinned or highlighted? (Recommendation: defer. Start with pure chronological ordering.)
3. **Feed freshness auto-tuning**: Should fetch intervals auto-adjust based on observed source update frequency? (Recommendation: start with manual per-source intervals via admin.)

---

## 14. Implementation Phases

### Phase 1: Core Pipeline + News Reader

- Set up project structure, Docker Compose, database schema (including fetch_logs, pipeline_logs, llm_models, pipeline_tasks, `surface` column on sources and categories)
- Implement adapter pattern (RSSAdapter first)
- Implement the scraper function with full fetch logging
- Implement LLM provider adapters (Anthropic, OpenAI, Google) + model registry
- Implement task-based model dispatch (pipeline_tasks → model lookup → provider adapter)
- Implement surface-aware LLM classifier with classification logging
- Implement cross-source story deduplication pipeline (fast title similarity → LLM confirmation → cluster management)
- Build News reader surface with headlines list, surface navigation, category filtering, and "Also in:" display
- Build three-layer CSS token architecture (primitives → semantic → component) with Tailwind integration and dark mode
- Seed with 5 news sources, 9 news categories, 6 LLM models, 4 pipeline tasks (classification, dedup, briefing, learning_digest)
- **Result**: A working news headlines site with full pipeline observability, cross-source dedup, and task-based LLM assignment from day one

### Phase 2: Learning Surface

- Add HBR and MIT SMR as learning sources (`surface='learning'`)
- Seed 8 learning categories
- Build Learning reader surface with topic-grouped layout, summaries visible, date-based timestamps
- Implement `SurfaceNav` component for News/Learning switching
- Extend `/api/headlines` and `/api/categories` with `surface` parameter
- Verify surface-aware classification (learning categories for learning sources)
- **Result**: Two content surfaces — News for time-sensitive headlines, Learning for enduring management insights

### Phase 3: Briefings

- Implement editorial worker (news briefing + learning digest generation)
- Implement editorial prompts (The Brief daily thematic summary + The Learning Digest weekly summary)
- Add `briefings` table (with `type` column) and public API endpoints
- Build EditorialSummary component (config-driven, serves both surfaces)
- Add admin briefing management (view, regenerate — both types)
- **Result**: Both surfaces open with AI-generated editorial summaries — daily for news, weekly for learning

### Phase 4: Admin Panel

- Source management CRUD + test fetch (with surface assignment: news/learning)
- Category management CRUD + preview + reorder (with surface filter)
- LLM model management: list, add, test
- Pipeline task management: model assignment, active toggles, cost breakdown (4 tasks: classification, dedup, briefing, learning_digest)
- Article management with search and manual overrides (filterable by surface)
- System health dashboard with per-task cost tracking
- Briefing management for both types (daily news + weekly learning)
- **Result**: Full operational control without touching code or database

### Phase 5: Analytics

- Event tracking on reader site
- Analytics event ingestion endpoint
- Analytics dashboard with core metrics
- **Result**: Understand how people use the site

### Phase 6: Polish

- Mobile responsiveness pass
- Performance optimization (caching, query tuning)
- Error alerting (email or Slack webhook on persistent fetch failures)
- RSS feed output (so others can subscribe to your curated feed)

### Phase 7: In Focus (deferred)

- Add `analysis` pipeline task (top story cross-source synthesis, assigned to Sonnet 4.6)
- Add `focus_topic`, `focus_body`, `focus_model` columns to `briefings`
- Implement analysis.py editorial worker + prompts
- Build In Focus component on reader site (below The Brief, above headlines)
- **Result**: The aggregator's unique editorial value — showing how each source frames the same story differently
