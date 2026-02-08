import news_fetcher
import news_storage
from datetime import datetime
import time

def force_seed_2026():
    print("[INFO] Force Seeding 2026 Data (Korean Keywords)...")
    
    # Load Existing
    data = news_storage.load_news_history() or {}
    
    # Expanded Categories with Korean Keywords
    targets = [
        ("IBK", "IBK캐피탈 OR \"IBK Capital\"", 50),
        ("KDB", "산은캐피탈 OR KDB캐피탈 OR \"KDB Capital\"", 50),
        ("Capital Industry", "여신전문금융 OR 캐피탈 산업", 30)
    ]
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    total_added = 0
    
    for key, query, limit in targets:
         print(f"  - Fetching {key} with query '{query}'...")
         if key not in data:
             data[key] = []
             
         try:
             # Fetch
             items = news_fetcher.fetch_news_period(query, start_date, end_date, max_items=limit)
             
             # Deduplicate
             existing_links = {x['link'] for x in data[key]}
             new_items = []
             for item in items:
                 if item['link'] not in existing_links:
                     new_items.append(item)
                     existing_links.add(item['link'])
             
             data[key].extend(new_items)
             count = len(new_items)
             total_added += count
             print(f"    -> Added {count} new items for {key}.")
             
             # Save immediately
             data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             news_storage.save_news_history(data)
             
         except Exception as e:
             print(f"    [ERROR] {e}")
                 
    print(f"[SUCCESS] Force Seeding Completed! Total Added: {total_added}")

if __name__ == "__main__":
    force_seed_2026()
