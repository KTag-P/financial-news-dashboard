import json
import os

def verify_content():
    if not os.path.exists('news_history.json'):
        print("[FAIL] news_history.json not found.")
        return

    with open('news_history.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"[OK] Loaded {len(data)} keys.")
    
    total_items = 0
    full_content_count = 0
    
    for key in ['IBK', 'KDB', 'Capital Industry']:
        items = data.get(key, [])
        total_items += len(items)
        
        for item in items:
            if 'full_content' in item and len(item['full_content']) > 50:
                full_content_count += 1
                
        print(f"  - {key}: {len(items)} items")

    print(f"--------------------------------------------------")
    print(f"Total Items: {total_items}")
    print(f"Items with Full Content: {full_content_count}")
    
    if total_items > 0:
        ratio = (full_content_count / total_items) * 100
        print(f"Full Content Cover Rate: {ratio:.1f}%")
        
    if full_content_count > 0:
        print("[SUCCESS] Full content is being saved!")
    else:
        print("[WARNING] No full content found. Check news_fetcher.py.")

if __name__ == "__main__":
    verify_content()
