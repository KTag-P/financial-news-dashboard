
import news_storage
import json

data = news_storage.load_news_history()
print("Total Keys:", data.keys())

for key in data:
    if key == '_last_updated': continue
    print(f"--- {key} ---")
    items = data[key][:5]
    for item in items:
        print(f"Published: '{item.get('published')}'")
