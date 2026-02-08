from news_fetcher import fetch_news
import json

def test_fetches():
    print("Testing IBK Capital news fetch...")
    ibk_news = fetch_news("IBK캐피탈", max_items=3)
    print(f"Found {len(ibk_news)} items for IBK Capital")
    if ibk_news:
        first = ibk_news[0]
        print(f"Title: {first['title']}")
        print(f"Link: {first['link']}")
        print(f"Summary Length: {len(first['summary'])}")
        print(f"Summary Preview: {first['summary'][:200]}...")

    print("\nTesting KDB Capital news fetch...")
    kdb_news = fetch_news("산은캐피탈", max_items=3)
    print(f"Found {len(kdb_news)} items for KDB Capital")
    
if __name__ == "__main__":
    test_fetches()
