import json
import os

def verify():
    if not os.path.exists('news_history.json'):
        print("[FAIL] news_history.json not found yet.")
        return

    with open('news_history.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"[OK] Loaded {len(data)} keys.")
    
    for key in ['IBK', 'KDB', 'Capital Industry', 'Macro Economy']:
        count = len(data.get(key, []))
        print(f"  - {key}: {count} items")
        
        # Check Years
        years = set()
        from dateutil import parser
        for item in data.get(key, []):
            try:
                dt = parser.parse(item['published'])
                years.add(dt.year)
            except:
                pass
        print(f"    Years found: {sorted(list(years))}")
        
    if '_last_updated' in data:
        print(f"[INFO] Last Updated: {data['_last_updated']}")

if __name__ == "__main__":
    verify()
