from __future__ import annotations

from .base import BaseAdapter
from .rss import RSSAdapter

ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {
    "rss": RSSAdapter,
}


def get_adapter(adapter_type: str) -> BaseAdapter:
    cls = ADAPTER_REGISTRY.get(adapter_type)
    if cls is None:
        raise ValueError(f"Unknown adapter type: {adapter_type}. Available: {list(ADAPTER_REGISTRY)}")
    return cls()
