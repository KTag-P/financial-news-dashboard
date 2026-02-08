import news_fetcher
import news_storage
import deduplicator
from datetime import datetime

# Load existing
data = news_storage.load_news_history()

print("Fetching FRESH Macro Economy news with new strict query...")
# Fetch 5 days to get a good baseline of quality articles
new_macro = news_fetcher.fetch_news("Macro Economy", days=5, max_items=20)
print(f"Fetched {len(new_macro)} items.")

# Deduplicate
deduped_macro = deduplicator.deduplicate_news(new_macro)
print(f"After deduplication: {len(deduped_macro)} items.")

# Show Titles for verification
print("=== New Macro News Titles ===")
for n in deduped_macro[:10]:
    print(f"- {n['title']}")

# Overwrite in data
data['Macro Economy'] = deduped_macro
data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Save
news_storage.save_news_history(data)
print("Saved refreshed Macro Economy data.")
