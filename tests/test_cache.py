import time

import pytest

from app.cache.response_cache import ResponseCache


@pytest.fixture
def cache() -> ResponseCache:
    return ResponseCache(ttl_seconds=300)


def test_get_cache_returns_none_on_miss(cache: ResponseCache) -> None:
    assert cache.GetCache("What is Python?") is None
    assert cache.stats["misses"] == 1
    assert cache.stats["hits"] == 0


def test_set_and_get_returns_cached_response(cache: ResponseCache) -> None:
    cache.SetCache("What is Python?", "Python is a programming language.")

    assert cache.GetCache("What is Python?") == "Python is a programming language."
    assert cache.stats["hits"] == 1
    assert cache.stats["misses"] == 0


def test_get_cache_normalizes_query(cache: ResponseCache) -> None:
    cache.SetCache("What is Python?", "Python is a programming language.")

    assert cache.GetCache("   WHAT IS PYTHON?   ") == "Python is a programming language."
    assert cache.stats["hits"] == 1


def test_different_queries_are_cached_separately(cache: ResponseCache) -> None:
    cache.SetCache("What is Python?", "Python answer")
    cache.SetCache("What is FastAPI?", "FastAPI answer")

    assert cache.GetCache("What is Python?") == "Python answer"
    assert cache.GetCache("What is FastAPI?") == "FastAPI answer"
    assert cache.stats["cached_entries"] == 2


def test_expired_entry_returns_none_and_is_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = ResponseCache(ttl_seconds=60)
    current_time = 1_000.0

    monkeypatch.setattr(time, "time", lambda: current_time)
    cache.SetCache("What is Python?", "Python is a programming language.")

    current_time += 61
    monkeypatch.setattr(time, "time", lambda: current_time)

    assert cache.GetCache("What is Python?") is None
    assert cache.stats["misses"] == 1
    assert cache.stats["cached_entries"] == 0


def test_non_expired_entry_is_still_available(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = ResponseCache(ttl_seconds=60)
    current_time = 1_000.0

    monkeypatch.setattr(time, "time", lambda: current_time)
    cache.SetCache("What is Python?", "Python is a programming language.")

    current_time += 30
    monkeypatch.setattr(time, "time", lambda: current_time)

    assert cache.GetCache("What is Python?") == "Python is a programming language."
    assert cache.stats["hits"] == 1


def test_stats_reflect_hit_rate(cache: ResponseCache) -> None:
    cache.SetCache("What is Python?", "Python is a programming language.")

    cache.GetCache("What is Python?")
    cache.GetCache("What is FastAPI?")

    stats = cache.stats

    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == "50.0%"
    assert stats["cached_entries"] == 1


def test_stats_with_no_requests(cache: ResponseCache) -> None:
    stats = cache.stats

    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["hit_rate"] == "0.0%"
    assert stats["cached_entries"] == 0
