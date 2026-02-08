import news_fetcher
import news_storage
import deduplicator
from datetime import datetime
import time

# Load existing
data = news_storage.load_news_history()

print("Starting Historical Backfill for Macro Economy (2021-2026)...")
all_macro = []

# UPDATED: Added 2026
years = [2021, 2022, 2023, 2024, 2025, 2026]

for year in years:
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    print(f"Fetching {year} ({start_date} ~ {end_date})...")
    
    try:
        items = news_fetcher.fetch_news_period("Macro Economy", start_date, end_date, max_items=20)
        print(f" -> Found {len(items)} items.")
        all_macro.extend(items)
    except Exception as e:
        print(f"Error fetching {year}: {e}")
        
    time.sleep(1) # Be nice to Google

print(f"Total Fetched: {len(all_macro)}")

# Deduplicate
deduped_macro = deduplicator.deduplicate_news(all_macro)
print(f"After deduplication: {len(deduped_macro)} items.")

# Overwrite Macro Economy with fresh data
data['Macro Economy'] = deduped_macro
data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

news_storage.save_news_history(data)
print("Saved Historical Macro Data (2021-2026).")
