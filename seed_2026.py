import news_fetcher
import news_storage
from datetime import datetime
from dateutil import parser
import time

def seed_2026():
    print("[INFO] Seeding 2026 Data (YTD)...")
    
    # Load Existing
    data = news_storage.load_news_history() or {}
    
    # Categories
    targets = [
        ("IBK", "IBK Capital", 30),
        ("KDB", "KDB Capital", 30),
        ("Capital Industry", "Capital Industry", 20)
    ]
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now() # Up to today
    
    for key, query, limit in targets:
         print(f"  - Fetching {key} for 2026...")
         if key not in data:
             data[key] = []
             
         try:
             items = news_fetcher.fetch_news_period(query, start_date, end_date, max_items=limit)
             
             # Deduplicate based on link/title
             existing_links = {x['link'] for x in data[key]}
             new_items = []
             for item in items:
                 if item['link'] not in existing_links:
                     new_items.append(item)
                     existing_links.add(item['link'])
             
             data[key].extend(new_items)
             print(f"    -> Added {len(new_items)} items for {key}.")
             
             # Save incrementally
             data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             news_storage.save_news_history(data)
             
         except Exception as e:
             print(f"    [ERROR] {e}")
                 
    print("[SUCCESS] 2026 Data Seeding Completed!")

if __name__ == "__main__":
    seed_2026()
