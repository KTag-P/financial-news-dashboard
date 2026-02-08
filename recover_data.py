
import news_fetcher
import news_storage
import deduplicator
from datetime import datetime

def seed_missing():
    print("Seeding Missing Data...")
    current_data = news_storage.load_news_history()
    
    # 1. Macro Economy 2026 (Recovery)
    print("  - Fetching Macro 2026...")
    start_2026 = datetime(2026, 1, 1)
    end_now = datetime.now()
    macro_2026 = news_fetcher.fetch_news_period("거시경제 전망 2026", start_2026, end_now, max_items=40)
    current_data['Macro Economy'] = deduplicator.deduplicate_news(current_data.get('Macro Economy', []) + macro_2026)
    
    # 2. Capital Industry 2021-2022
    print("  - Fetching Industry 2021-2022...")
    ind_2021 = news_fetcher.fetch_news_period("캐피탈 업황 전망", datetime(2021, 1, 1), datetime(2021, 12, 31), max_items=20)
    ind_2022 = news_fetcher.fetch_news_period("캐피탈 업황 전망", datetime(2022, 1, 1), datetime(2022, 12, 31), max_items=20)
    current_data['Capital Industry'] = deduplicator.deduplicate_news(current_data.get('Capital Industry', []) + ind_2021 + ind_2022)
    
    # 3. Macro 2021-2022 (Just in case)
    print("  - Fetching Macro 2021-2022...")
    macro_2021 = news_fetcher.fetch_news_period("거시경제", datetime(2021, 1, 1), datetime(2021, 12, 31), max_items=20)
    macro_2022 = news_fetcher.fetch_news_period("거시경제", datetime(2022, 1, 1), datetime(2022, 12, 31), max_items=20)
    current_data['Macro Economy'] = deduplicator.deduplicate_news(current_data.get('Macro Economy', []) + macro_2021 + macro_2022)

    current_data['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    news_storage.save_news_history(current_data)
    print("Recovery Complete.")

if __name__ == "__main__":
    seed_missing()
