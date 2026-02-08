import json
import deduplicator  # Uses the new logic we just wrote

# Load valid data
with open("news_history.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned_data = {}
total_removed = 0

for key, items in data.items():
    original_count = len(items)
    
    # Apply new deduplication (Sorts by length -> Aggressive Cluster)
    dedrupled_items = deduplicator.deduplicate_news(items)
    
    cleaned_data[key] = dedrupled_items
    removed = original_count - len(dedrupled_items)
    total_removed += removed
    print(f"[{key}] {original_count} -> {len(dedrupled_items)} (-{removed})")

with open("news_history.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

print(f"Total Duplicates Removed: {total_removed}")
