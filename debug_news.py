import news_fetcher
from datetime import datetime, timedelta

def test_fetch():
    print("--- Debugging News Fetcher ---")
    
    # Test 1: Capital Industry, 7 days
    print("\n[Test 1] Capital Industry (7 days)")
    items = news_fetcher.fetch_news("Capital Industry", days=7)
    print(f"Items found: {len(items)}")
    for item in items[:3]:
        print(f"- {item['title']} ({item['published']})")

    # Print the URL logic from news_fetcher (by copying logic or modifying fetcher)
    # Actually, let's just modify the fetcher to print URL for debugging, or import logic.
    # Simpler: just call fetch_news, it's already importing.
    # I will rely on the fact that I'm about to change the fetcher.
    # But for now, let's just see if we can get ANY results with a simpler query.
    
    print("\n[Test 3] Simple Query (No Date)")
    # We can't easily bypass the date logic in fetch_news without changing code.
    # So I will update news_fetcher.py to print the URL it uses.
    pass
    
if __name__ == "__main__":
    test_fetch()
