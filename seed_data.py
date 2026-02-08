import news_fetcher
import news_storage
from datetime import datetime
from dateutil import parser
import time
import os
import json

def seed_5_years():
    print("[INFO] Starting Smart Seeding (Resume Capable)...")
    
    # Load Existing Data
    existing_data = news_storage.load_news_history() or {}
    for key in ['IBK', 'KDB', 'Capital Industry']:
        if key not in existing_data:
            existing_data[key] = []
            
    years = [2021, 2022, 2023, 2024, 2025]
    companies = [
        ("IBK", "IBK Capital", 50),
        ("KDB", "KDB Capital", 50),
        ("Capital Industry", "Capital Industry", 30)
    ]
    
    for year in years:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        for key, query_name, limit in companies:
            # Skip Industry for old years if desired (keeping logic same)
            if key == "Capital Industry" and year < 2023:
                continue

            # Check if year already exists in data
            # Heuristic: If we have > 5 items for this year, assume done.
            existing_items = existing_data.get(key, [])
            count_in_year = 0
            for x in existing_items:
                try:
                    p = x.get('published', '')
                    if not p: continue
                    # Robust Parse
                    y = parser.parse(p).year
                    if y == year:
                        count_in_year += 1
                except:
                    pass
            
            if count_in_year >= 5: # Threshold to skip (assuming 5 from prev run is enough? No, user wants 50)
                 # Wait, user wants 50. If we have only 5 (from old short run), we should RE-FETCH.
                 # Only skip if we have a significant number (e.g. > 10)
                 if count_in_year >= 30:
                     print(f"  - Skipping {key} {year} (Found {count_in_year} items)")
                     continue
            
            # Actually, to be safe, let's just fetch and DEDUPLICATE.
            # But fetching takes time.
            # If we really want to resume, we need to know if we *finished* that year.
            # Let's just fetch and append, relying on deduplicator? 
            # No, deduplicator is in app.py logic, not here.
            # Let's clean the list for that year if we re-fetch.
            
            print(f"  - Fetching {key} for {year}...")
            try:
                new_items = news_fetcher.fetch_news_period(query_name, start_date, end_date, max_items=limit)
                
                # Filter out old items for this year from existing data to avoid dups
                # We need to be careful not to delete items if fetch failed or returned 0.
                if new_items:
                    # Remove items for this year
                    kept_items = []
                    for x in existing_data[key]:
                        try:
                            if parser.parse(x.get('published')).year != year:
                                kept_items.append(x)
                        except:
                            kept_items.append(x)
                    existing_data[key] = kept_items
                    
                    # Add new items
                    existing_data[key].extend(new_items)
                
                # Save Immediately (Incremental)
                existing_data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                news_storage.save_news_history(existing_data)
                print(f"    -> Saved {len(new_items)} items for {year}. (Total {key}: {len(existing_data[key])})")
                
            except Exception as e:
                print(f"    [ERROR] Failed {key} {year}: {e}")
                
    print("[SUCCESS] Seeding Completed!")

if __name__ == "__main__":
    seed_5_years()

