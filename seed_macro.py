import news_fetcher
import news_storage
from datetime import datetime
from dateutil import parser
import time

def seed_macro():
    print("[INFO] Seeding Macro Economy Data (2021-2026)...")
    
    # Load Existing
    data = news_storage.load_news_history() or {}
    if 'Macro Economy' not in data:
        data['Macro Economy'] = []
        
    # Macro Queries
    queries = [
        ("Macro Economy", "금리 인상 OR 물가 상승 OR 환율 전망 OR GDP 성장률", 30)
    ]
    
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    
    for year in years:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        # Skip future if unnecessary, but 2026 is needed
        if year == 2026 and datetime.now().year < 2026:
             # Just fetch up to now
             end_date = datetime.now()
             
        for key, query, limit in queries:
             print(f"  - Fetching {key} for {year}...")
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
                 print(f"    -> Added {len(new_items)} items.")
                 
                 # Save incrementally
                 data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 news_storage.save_news_history(data)
                 
             except Exception as e:
                 print(f"    [ERROR] {e}")
                 
    print("[SUCCESS] Macro Data Seeding Completed!")

if __name__ == "__main__":
    seed_macro()
