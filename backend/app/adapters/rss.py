from __future__ import annotations

import asyncio
import hashlib
import html
import logging
import re
from datetime import datetime, timedelta, timezone

import feedparser
import httpx
from dateutil import parser as dateutil_parser

from .base import AdapterResult, BaseAdapter, RawArticle

logger = logging.getLogger(__name__)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _clean_text(text: str | None) -> str | None:
    if not text:
        return None
    text = html.unescape(text)
    text = _HTML_TAG_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text or None


def _extract_guid(entry) -> str:
    if getattr(entry, "id", None):
        return entry.id
    if getattr(entry, "link", None):
        return entry.link
    return hashlib.sha256(entry.get("title", "").encode()).hexdigest()


def _parse_date(entry) -> datetime | None:
    # Try feedparser's parsed tuple first
    parsed = getattr(entry, "published_parsed", None)
    if parsed:
        try:
            from time import mktime
            return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
        except (ValueError, OverflowError):
            pass

    # Try dateutil on the raw string
    raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if raw:
        try:
            dt = dateutil_parser.parse(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            pass

    return None


def _validate_date(dt: datetime | None) -> datetime:
    now = datetime.now(timezone.utc)
    if dt is None:
        return now
    if dt > now + timedelta(hours=1):
        return now
    if dt < now - timedelta(days=7):
        return now
    return dt


def _extract_summary(entry) -> str | None:
    summary = getattr(entry, "summary", None)
    if summary:
        return _clean_text(summary)[:500] if _clean_text(summary) else None
    content = getattr(entry, "content", None)
    if content and len(content) > 0:
        val = content[0].get("value", "")
        return _clean_text(val)[:500] if _clean_text(val) else None
    return None


class RSSAdapter(BaseAdapter):
    async def fetch(self, source) -> AdapterResult:
        headers = {}
        adapter_config = source.adapter_config or {}
        if adapter_config.get("headers"):
            headers.update(adapter_config["headers"])
        if source.last_etag:
            headers["If-None-Match"] = source.last_etag
        if source.last_modified:
            headers["If-Modified-Since"] = source.last_modified

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(source.feed_url, headers=headers, follow_redirects=True)

        if response.status_code == 304:
            return AdapterResult(
                http_status=304,
                etag=source.last_etag,
                last_modified=source.last_modified,
                response_bytes=0,
            )

        response.raise_for_status()

        content = response.text
        response_bytes = len(response.content)
        etag = response.headers.get("ETag")
        last_modified = response.headers.get("Last-Modified")

        feed = await asyncio.to_thread(feedparser.parse, content)

        articles = []
        errors = []

        for entry in feed.entries:
            try:
                title = _clean_text(getattr(entry, "title", None))
                if not title:
                    errors.append(f"Entry missing title: {getattr(entry, 'link', 'unknown')}")
                    continue

                url = getattr(entry, "link", None)
                if not url:
                    errors.append(f"Entry missing link: {title}")
                    continue

                articles.append(
                    RawArticle(
                        external_id=_extract_guid(entry),
                        title=title,
                        url=url,
                        summary=_extract_summary(entry),
                        author=_clean_text(getattr(entry, "author", None)),
                        image_url=None,
                        published_at=_validate_date(_parse_date(entry)),
                    )
                )
            except Exception as e:
                errors.append(f"Failed to parse entry: {e}")

        return AdapterResult(
            articles=articles,
            http_status=response.status_code,
            etag=etag,
            last_modified=last_modified,
            response_bytes=response_bytes,
            errors=errors,
        )
