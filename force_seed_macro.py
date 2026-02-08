import news_fetcher
import news_storage
from datetime import datetime
import time

def force_seed_macro():
    print("[INFO] Force Seeding Macro Economy (2023-2026)...")
    
    # Load Existing
    data = news_storage.load_news_history() or {}
    if 'Macro Economy' not in data:
        data['Macro Economy'] = []
    
    # Categories with Korean Keywords
    # Broad economic terms
    queries = [
        ("Macro Economy", "경제 전망 OR 금리 인상 OR 물가 상승 OR 환율", 40)
    ]
    
    years = [2023, 2024, 2025, 2026]
    
    total_added = 0
    
    for year in years:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        if year == 2026:
            end_date = datetime.now()
            
        print(f"  - Fetching Macro data for {year}...")
            
        for key, query, limit in queries:
             try:
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
                 print(f"    -> Added {count} items.")
                 
                 # Save incrementally
                 data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 news_storage.save_news_history(data)
                 
             except Exception as e:
                 print(f"    [ERROR] {e}")
                 
    print(f"[SUCCESS] Macro Seeding Completed! Total Added: {total_added}")

if __name__ == "__main__":
    force_seed_macro()
