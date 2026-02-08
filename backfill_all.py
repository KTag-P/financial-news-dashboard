import news_fetcher
import news_storage
import deduplicator
from datetime import datetime
import time

# Load existing
data = news_storage.load_news_history()

print("Starting Complete Backfill with Full Content Scraping (2021-2026)...")
print("This will take several minutes as we scrape each article...")

# Define all categories to backfill
categories = [
    ("Macro Economy", "거시경제"),
    ("IBK Parent", "IBK기업은행"),
    ("KDB Parent", "KDB산업은행"),
]

years = [2021, 2022, 2023, 2024, 2025, 2026]

for company_key, display_name in categories:
    print(f"\n=== Backfilling {display_name} ({company_key}) ===")
    all_items = []
    
    for year in years:
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        print(f"  Fetching {year}...")
        
        try:
            items = news_fetcher.fetch_news_period(company_key, start_date, end_date, max_items=15)
            print(f"    -> Found {len(items)} items with full content.")
            all_items.extend(items)
        except Exception as e:
            print(f"    Error: {e}")
            
        time.sleep(1)
    
    print(f"  Total {display_name}: {len(all_items)} items")
    
    # Deduplicate
    deduped = deduplicator.deduplicate_news(all_items)
    print(f"  After dedup: {len(deduped)} items")
    
    # Save to data
    data[company_key] = deduped

# Update timestamp
data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Save
news_storage.save_news_history(data)
print("\n✅ Complete! All categories backfilled with full content.")
