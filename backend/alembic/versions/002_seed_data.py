"""seed_data

Revision ID: 002
Revises: 001
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Sources (5 news active, 2 learning inactive) ---
    op.execute("""
        INSERT INTO sources (id, name, slug, surface, homepage_url, feed_url, adapter_type, fetch_interval, active) VALUES
        ('a1000000-0000-0000-0000-000000000001', 'Financial Times', 'ft', 'news', 'https://www.ft.com', 'https://www.ft.com/rss/home', 'rss', 15, true),
        ('a1000000-0000-0000-0000-000000000002', 'Bloomberg', 'bloomberg', 'news', 'https://www.bloomberg.com', 'https://feeds.bloomberg.com/markets/news.rss', 'rss', 15, true),
        ('a1000000-0000-0000-0000-000000000003', 'The Wall Street Journal', 'wsj', 'news', 'https://www.wsj.com', 'https://feeds.a.dj.com/rss/RSSWorldNews.xml', 'rss', 15, true),
        ('a1000000-0000-0000-0000-000000000004', 'The Verge', 'the-verge', 'news', 'https://www.theverge.com', 'https://www.theverge.com/rss/index.xml', 'rss', 30, true),
        ('a1000000-0000-0000-0000-000000000005', 'Stratechery', 'stratechery', 'news', 'https://stratechery.com', 'https://stratechery.com/feed/', 'rss', 120, true),
        ('a1000000-0000-0000-0000-000000000006', 'Harvard Business Review', 'hbr', 'learning', 'https://hbr.org', 'https://hbr.org/rss', 'rss', 360, false),
        ('a1000000-0000-0000-0000-000000000007', 'MIT Sloan Management Review', 'mit-smr', 'learning', 'https://sloanreview.mit.edu', 'https://sloanreview.mit.edu/feed/', 'rss', 720, false)
    """)

    # --- News Categories (9) ---
    op.execute("""
        INSERT INTO categories (id, name, slug, surface, description, display_order) VALUES
        ('b1000000-0000-0000-0000-000000000001', 'Economy', 'economy', 'news',
         'Macroeconomic trends, GDP, inflation, unemployment, economic policy, fiscal policy, economic indicators, recessions, growth forecasts, labor markets, trade balances, economic outlook', 1),
        ('b1000000-0000-0000-0000-000000000002', 'Markets', 'markets', 'news',
         'Stock markets, bonds, commodities, forex, interest rates, central bank policy (Fed, ECB, BoE), trading, IPOs, earnings reports, market analysis, investor sentiment, fund flows', 2),
        ('b1000000-0000-0000-0000-000000000003', 'Tech', 'tech', 'news',
         'Technology companies, products, software, hardware, artificial intelligence, machine learning, startups, gadgets, consumer electronics, apps, social media platforms, cybersecurity, cloud computing', 3),
        ('b1000000-0000-0000-0000-000000000004', 'Politics', 'politics', 'news',
         'Political campaigns, legislation, government policy, partisan politics, elections, political analysis, lobbying, political appointments, congressional/parliamentary proceedings', 4),
        ('b1000000-0000-0000-0000-000000000005', 'US', 'us', 'news',
         'United States domestic affairs — US economy, US policy, US society, US events. Stories primarily about what is happening inside America, including federal and state-level news', 5),
        ('b1000000-0000-0000-0000-000000000006', 'Europe', 'europe', 'news',
         'European affairs — EU policy, European economies, European politics, events in European countries. Stories primarily about what is happening in Europe, including UK post-Brexit', 6),
        ('b1000000-0000-0000-0000-000000000007', 'World', 'world', 'news',
         'International affairs outside US and Europe — Asia, Middle East, Africa, Latin America, global diplomacy, wars and conflicts, international organizations (UN, NATO), global health, climate policy', 7),
        ('b1000000-0000-0000-0000-000000000008', 'Business', 'business', 'news',
         'Corporate strategy, mergers and acquisitions, executive appointments, company earnings, industry trends, regulation, antitrust, supply chains, entrepreneurship, corporate governance', 8),
        ('b1000000-0000-0000-0000-000000000009', 'Opinion', 'opinion', 'news',
         'Editorials, op-eds, columns, analysis and commentary pieces. Often identifiable by URL patterns (/opinion/, /editorial/) or by the presence of a prominent columnist byline', 9)
    """)

    # --- Learning Categories (8) ---
    op.execute("""
        INSERT INTO categories (id, name, slug, surface, description, display_order) VALUES
        ('b2000000-0000-0000-0000-000000000001', 'Strategy', 'strategy', 'learning',
         'Corporate strategy, competitive advantage, business models, strategic planning, disruption, industry analysis, value creation, market positioning, diversification, growth strategy, strategic decision-making', 1),
        ('b2000000-0000-0000-0000-000000000002', 'Leadership', 'leadership', 'learning',
         'Leadership development, executive decision-making, management practices, team building, organizational leadership, influence, coaching, emotional intelligence, leading through change, C-suite challenges', 2),
        ('b2000000-0000-0000-0000-000000000003', 'Innovation', 'innovation', 'learning',
         'Innovation management, R&D, product development, design thinking, creative processes, emerging business models, experimentation, intrapreneurship, disruptive innovation, corporate venturing', 3),
        ('b2000000-0000-0000-0000-000000000004', 'Technology & AI', 'technology-ai', 'learning',
         'Digital transformation, artificial intelligence in business, machine learning applications, automation, data-driven decision making, tech strategy, enterprise technology, AI adoption, algorithmic management', 4),
        ('b2000000-0000-0000-0000-000000000005', 'Operations', 'operations', 'learning',
         'Operations management, supply chain, process improvement, lean management, quality management, scaling operations, operational excellence, logistics, manufacturing, productivity systems', 5),
        ('b2000000-0000-0000-0000-000000000006', 'Marketing & Growth', 'marketing-growth', 'learning',
         'Marketing strategy, customer acquisition, branding, growth strategies, customer experience, market research, go-to-market, pricing strategy, consumer behavior, brand management', 6),
        ('b2000000-0000-0000-0000-000000000007', 'People & Culture', 'people-culture', 'learning',
         'Talent management, organizational culture, diversity and inclusion, employee engagement, hiring, workplace dynamics, remote work, organizational behavior, performance management, team dynamics', 7),
        ('b2000000-0000-0000-0000-000000000008', 'Entrepreneurship', 'entrepreneurship', 'learning',
         'Startups, venture capital, founding teams, scaling businesses, business planning, bootstrapping, founder lessons, lean startup methodology, fundraising, startup strategy', 8)
    """)

    # --- LLM Models (6) ---
    op.execute("""
        INSERT INTO llm_models (id, provider, model_id, display_name, input_price_per_mtok, output_price_per_mtok, context_window, max_output_tokens) VALUES
        ('c1000000-0000-0000-0000-000000000001', 'anthropic', 'claude-haiku-4-5-20251001', 'Claude Haiku 4.5', 1.00, 5.00, 200000, 8192),
        ('c1000000-0000-0000-0000-000000000002', 'anthropic', 'claude-sonnet-4-6-20250514', 'Claude Sonnet 4.6', 3.00, 15.00, 200000, 16384),
        ('c1000000-0000-0000-0000-000000000003', 'openai', 'gpt-5-mini', 'GPT-5 Mini', 0.25, 2.00, 128000, 16384),
        ('c1000000-0000-0000-0000-000000000004', 'openai', 'gpt-5-nano', 'GPT-5 Nano', 0.05, 0.40, 128000, 16384),
        ('c1000000-0000-0000-0000-000000000005', 'google', 'gemini-2.5-flash', 'Gemini 2.5 Flash', 0.30, 2.50, 1000000, 8192),
        ('c1000000-0000-0000-0000-000000000006', 'google', 'gemini-2.5-flash-lite', 'Gemini 2.5 Flash-Lite', 0.10, 0.40, 1000000, 8192)
    """)

    # --- Pipeline Tasks (4) ---
    op.execute("""
        INSERT INTO pipeline_tasks (task, model_id, active, config) VALUES
        ('classification', 'claude-haiku-4-5-20251001', true, '{}'),
        ('dedup', 'claude-haiku-4-5-20251001', true, '{"similarity_threshold": 0.35, "window_hours": 48, "max_candidates": 5}'),
        ('briefing', 'claude-sonnet-4-6-20250514', true, '{"max_sentences": 5}'),
        ('learning_digest', 'claude-sonnet-4-6-20250514', true, '{"max_sentences": 5}')
    """)


def downgrade() -> None:
    op.execute("DELETE FROM pipeline_tasks")
    op.execute("DELETE FROM llm_models")
    op.execute("DELETE FROM categories")
    op.execute("DELETE FROM sources")
