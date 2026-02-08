import json
import os
import shutil
from datetime import datetime

# Backup
if os.path.exists("news_history.json"):
    shutil.copy("news_history.json", f"news_history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

with open("news_history.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def clean_ibk(items):
    cleaned = []
    removed_count = 0
    for item in items:
        text = (item.get('title', '') + " " + item.get('summary', '') + " " + item.get('full_content', '')).lower()
        
        # Keep if explicitly mentions Industrial Bank
        has_bank = "기업은행" in text or "ibk기업은행" in text
        
        # Exclude if primarily Capital (and not Bank)
        is_capital = "ibk캐피탈" in text or "캐피탈" in item.get('title', '')
        
        # Rule: Keep if (Has Bank) AND (Not strictly Capital title)
        # Actually, if it mentions both, it might be synergy. 
        # But User said "Keep only Corporate Bank data".
        # Let's be strict: Title must NOT contain "IBK캐피탈"
        
        if "ibk캐피탈" in item.get('title', ''):
            removed_count += 1
            continue
            
        if has_bank:
            cleaned.append(item)
        else:
            removed_count += 1
            
    print(f"IBK: Removed {removed_count} items. Remaining: {len(cleaned)}")
    return cleaned

def clean_kdb(items):
    cleaned = []
    removed_count = 0
    for item in items:
        text = (item.get('title', '') + " " + item.get('summary', '') + " " + item.get('full_content', '')).lower()
        
        has_bank = "산업은행" in text or "kdb산업은행" in text
        
        if "산은캐피탈" in item.get('title', '') or "kdb캐피탈" in item.get('title', ''):
            removed_count += 1
            continue
            
        if has_bank:
            cleaned.append(item)
        else:
            removed_count += 1

    print(f"KDB: Removed {removed_count} items. Remaining: {len(cleaned)}")
    return cleaned

if "IBK" in data:
    data["IBK"] = clean_ibk(data["IBK"])

if "KDB" in data:
    data["KDB"] = clean_kdb(data["KDB"])

# Also check for "General" junk in other keys if needed, but user specified IBK/KDB group.

with open("news_history.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Cleanup Complete.")
