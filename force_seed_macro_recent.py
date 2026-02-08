import news_fetcher
import news_storage
from datetime import datetime
import time

def force_seed_macro_recent():
    print("[INFO] Force Seeding Macro Economy (2025-2026 Only)...")
    
    # Load Existing
    data = news_storage.load_news_history() or {}
    key = 'Macro Economy'
    if key not in data:
        data[key] = []
    
    # Specific keywords for recent economic trends
    queries = [
        (key, "한국은행 금리 OR 소비자물가 OR GDP 성장률 OR 환율 전망", 30),
        (key, "미국 연준 금리 OR FOMC OR 달러 환율", 30)
    ]
    
    years = [2025, 2026]
    
    total_added = 0
    
    for year in years:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        if year == 2026:
            end_date = datetime.now()
            
        print(f"  - Fetching Macro data for {year}...")
            
        for k, query, limit in queries:
             try:
                 items = news_fetcher.fetch_news_period(query, start_date, end_date, max_items=limit)
                 
                 # Deduplicate
                 existing_links = {x['link'] for x in data[key]}
                 new_items = []
                 for item in items:
                     if item['link'] not in existing_links:
                         # VALIDATION: Check if year matches
                         try:
                             pub_year = datetime.strptime(item['published'][:10], "%Y-%m-%d").year
                             if pub_year == year:
                                 new_items.append(item)
                                 existing_links.add(item['link'])
                         except:
                             pass
                 
                 data[key].extend(new_items)
                 count = len(new_items)
                 total_added += count
                 print(f"    -> Added {count} items for {year}.")
                 
                 # Save
                 data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 news_storage.save_news_history(data)
                 
             except Exception as e:
                 print(f"    [ERROR] {e}")
                 
    print(f"[SUCCESS] Macro Seeding Completed! Total Added: {total_added}")

if __name__ == "__main__":
    force_seed_macro_recent()
