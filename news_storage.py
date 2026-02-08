import json
import os

FILE_PATH = "news_history.json"

def load_news_history():
    """
    Loads news history from JSON.
    Returns empty dict if file not found or error.
    """
    if not os.path.exists(FILE_PATH):
        return {}
        
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading news history: {e}")
        return {}

def save_news_history(news_data):
    """
    Saves news data to JSON.
    """
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(news_data, f, ensure_ascii=False, indent=4)
        print("News history saved.")
    except Exception as e:
        print(f"Error saving news history: {e}")
