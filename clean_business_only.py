import json
import os
import shutil
from datetime import datetime

# Backup (Already done in previous run, but checking)
if not os.path.exists("news_history_clean_backup_RETRY.json"):
     if os.path.exists("news_history.json"):
        shutil.copy("news_history.json", "news_history_clean_backup_RETRY.json")

with open("news_history.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Define Junk Keywords
junk_keywords = ["기부", "성금", "봉사", "승진", "인사", "위촉", "선임", "취임", "방문", "참석", "전달", "나눔", "후원"]
mismatch_marker = "김병훈" 

def clean_items(items, company_code):
    cleaned = []
    removed_count = 0
    corruption_fixed = 0
    
    for item in items:
        # Handle malformed items (strings instead of dicts)
        if isinstance(item, str):
            # If it's just a string, it's likely junk or legacy data.
            # Convert to dict if possible or just skip.
            # Let's try to keep it if it looks like a title, but for now, just skip to be safe?
            # Or print it.
            # print(f"[{company_code}] Skipping string item: {item[:30]}...")
            continue
            
        if not isinstance(item, dict):
            continue

        title = item.get('title', '')
        content = item.get('full_content', '')
        summary = item.get('summary', '')
        
        # 1. Detect Mismatch Corruption
        if mismatch_marker in content and "푸르메" in title:
             corruption_fixed += 1
             print(f"[{company_code}] Found Mismatched Item: {title}")
             continue 

        # 2. Filter Junk
        is_junk = any(k in title for k in junk_keywords)
        if is_junk:
            removed_count += 1
            continue

        cleaned.append(item)

    print(f"[{company_code}] Removed {removed_count} junk. Fixed {corruption_fixed} corruptions. Remaining: {len(cleaned)}")
    return cleaned

for key in data:
    # Ensure value is list
    if isinstance(data[key], list):
        data[key] = clean_items(data[key], key)

with open("news_history.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Business Cleanup Complete.")
