import time
from app.cache.response_cache import ResponseCache

def test_response_cache():
    cache = ResponseCache(ttl_seconds=3)

    print("\n=== Response Cache Test ===")

    # 1. Cache miss
    print("\n1. Testing cache miss...")

    result = cache.GetCache("What is Python?")

    print(f"Result: {result}")
    print(f"Stats: {cache.stats}")

    # 2. Store response
    print("\n2. Storing response...")

    cache.SetCache(
        "What is Python?",
        "Python is a high-level programming language."
    )

    print(f"Stats: {cache.stats}")

    # 3. Cache hit
    print("\n3. Testing cache hit...")

    result = cache.GetCache("What is Python?")

    print(f"Result: {result}")
    print(f"Stats: {cache.stats}")

    # 4. Test normalization
    print("\n4. Testing query normalization...")

    result = cache.GetCache("   WHAT IS PYTHON?   ")

    print(f"Result: {result}")
    print(f"Stats: {cache.stats}")

    # 5. Test another query
    print("\n5. Testing another query...")

    result = cache.GetCache("What is FastAPI?")

    print(f"Result: {result}")
    print(f"Stats: {cache.stats}")

    # 6. Test expiration
    print("\n6. Testing cache expiration...")

    print("Waiting 4 seconds...")
    time.sleep(4)

    result = cache.GetCache("What is Python?")

    print(f"Result after expiration: {result}")
    print(f"Stats: {cache.stats}")


if __name__ == "__main__":
    test_response_cache()