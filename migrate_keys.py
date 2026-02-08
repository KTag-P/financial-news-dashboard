import json

# Current (Bank Only)
with open("news_history.json", "r", encoding="utf-8") as f:
    current_data = json.load(f)

# Backup (Mixed)
with open("news_history_backup_20260208_225312.json", "r", encoding="utf-8") as f:
    backup_data = json.load(f)

# Initialize New Structure
new_data = current_data.copy()
new_data["IBK_Parent"] = current_data.get("IBK", [])
new_data["KDB_Parent"] = current_data.get("KDB", [])
new_data["IBK"] = [] # Clear for Capital restoration
new_data["KDB"] = [] 

def extract_capital(items):
    capital_news = []
    seen_titles = set()
    for item in items:
        # Handle strict string items if any
        if isinstance(item, str): continue
        
        title = item.get('title', '')
        if title in seen_titles: continue
        
        text = (title + " " + item.get('summary', '')).lower()
        if "캐피탈" in text:
            capital_news.append(item)
            seen_titles.add(title)
    return capital_news

# Restore Capital News from Backup
if "IBK" in backup_data:
    new_data["IBK"] = extract_capital(backup_data["IBK"])
    print(f"Restored {len(new_data['IBK'])} IBK Capital items.")

if "KDB" in backup_data:
    new_data["KDB"] = extract_capital(backup_data["KDB"])
    print(f"Restored {len(new_data['KDB'])} KDB Capital items.")

# Save
with open("news_history.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

print("Migration Complete: Created IBK_Parent/KDB_Parent and Restored Capital Keys.")
