import news_fetcher
import market_data_fetcher
import sys
import os

# Set console to utf-8
sys.stdout.reconfigure(encoding='utf-8')

print("--- Testing Market Data ---")
try:
    market = market_data_fetcher.get_market_data()
    print("Market Data Result:", market)
    if not market or 'KOSPI' not in market or market['KOSPI']['price'] == 'N/A':
        print("WARNING: Market Data might be incomplete.")
    else:
        print("SUCCESS: Market Data fetched.")
except Exception as e:
    print(f"FAILED: Market Data fetch error: {e}")

print("\n--- Testing News Fetcher (IBK Capital, 1 Day) ---")
try:
    news = news_fetcher.fetch_news("IBK Capital", days=1, max_items=3)
    print(f"Fetched {len(news)} items.")
    if len(news) > 0:
        print("Sample Title:", news[0]['title'])
        print("Sample Date:", news[0]['published'])
    else:
        print("WARNING: No news found (might be expected if no recent news).")
    print("SUCCESS: News Fetcher executed.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILED: News Fetcher error: {e}")

print("\n--- Testing 1-Year Key Issues ---")
try:
    issues = news_fetcher.fetch_1year_key_issues("IBK Capital", max_items=2)
    print(f"Fetched {len(issues)} key issues.")
    if len(issues) > 0:
        print("Sample Issue:", issues[0]['title'])
    print("SUCCESS: Key Issues Fetcher executed.")
except Exception as e:
    print(f"FAILED: Key Issues Fetcher error: {e}")

print("\n--- Testing Market Data (New Indices) ---")
try:
    import market_data_fetcher
    data = market_data_fetcher.get_market_data()
    keys = ['KOSDAQ', 'NASDAQ', 'Nikkei 225']
    for k in keys:
        if k in data:
            print(f"Fetched {k}: {data[k]['price']}")
        else:
            print(f"FAILED to fetch {k}")
    print("SUCCESS: Market Data fetcher check complete.")
except Exception as e:
    print(f"FAILED: Market Data error: {e}")


print("\n--- Testing Imports ---")
try:
    from urllib.parse import quote
    print("SUCCESS: 'quote' imported.")
except ImportError:
    print("FAILED: 'quote' import failed.")
