"""
One-time migration from news_history.json to news_history.db (SQLite).
Run: python migrate_json_to_sqlite.py

The migration is also done automatically on first app load,
but this script allows manual verification.
"""
import json
import os
import news_storage

JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_history.json")


def migrate():
    if not os.path.exists(JSON_PATH):
        print(f"JSON file not found: {JSON_PATH}")
        print("Nothing to migrate.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    news_storage._init_db()
    news_storage.save_news_history(data)

    # Verify
    loaded = news_storage.load_news_history()
    print("\n=== Migration Results ===")
    for key in data:
        if key.startswith('_'):
            print(f"  Metadata '{key}': migrated")
            continue
        json_count = len(data[key]) if isinstance(data[key], list) else 0
        db_count = len(loaded.get(key, []))
        status = "OK" if db_count > 0 else "WARN"
        print(f"  [{status}] {key}: JSON={json_count}, DB={db_count}")

    total = news_storage.get_news_count()
    print(f"\nTotal news items in DB: {total}")
    print("Migration complete. JSON file preserved as backup.")


if __name__ == "__main__":
    migrate()
