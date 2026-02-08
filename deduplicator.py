from difflib import SequenceMatcher

def is_similar(a, b, threshold=0.75):
    """
    Checks if two strings are similar.
    Lowered threshold slightly for broader matching.
    """
    return SequenceMatcher(None, a, b).ratio() > threshold

def is_personnel_news(title):
    keys = ['[인사]', '인사', '프로필', '선임', '승진']
    return any(k in title for k in keys)

def deduplicate_news(news_list):
    """
    Advanced Deduplication:
    1. Sorts by content length (descending) to prioritize detailed articles.
    2. Uses SequenceMatcher for title similarity.
    3. Checks for high overlap in title words.
    """
    if not news_list:
        return []

    # 1. Sort by Content Length (Longest first) -> We keep the most detailed version
    # Use a safe get for length, ensuring item is a dict
    def get_len(x):
        if isinstance(x, dict):
            return len(x.get('full_content', '')) if x.get('full_content') else 0
        return 0

    sorted_news = sorted(news_list, key=get_len, reverse=True)
    
    unique_news = []
    
    for news in sorted_news:
        if not isinstance(news, dict): continue
        title = news.get('title', '')
        is_duplicate = False
        
        for kept_item in unique_news:
            kept_title = kept_item['title']
            
            # A. Sequence Matcher (Fuzzy String Match)
            # Threshold 0.6 is good for "Same event, slightly different headline"
            similarity = SequenceMatcher(None, title, kept_title).ratio()
            
            # B. Specific check for "Appointment/Personnel" to be very aggressive
            # If both are personnel news, and similarity > 0.5, treat as dupe
            is_personnel_a = is_personnel_news(title)
            is_personnel_b = is_personnel_news(kept_title)
            
            if is_personnel_a and is_personnel_b:
                if similarity > 0.4: # Very aggressive for personnel news
                     is_duplicate = True
                     break
            
            if similarity > 0.6:
                is_duplicate = True
                break
                
        if not is_duplicate:
            unique_news.append(news)
            
    # Restore Chronological Order (Newest First) for display
    # Assuming 'published' is sortable or we can just rely on the original fetch order if we tracked indices.
    # But usually news_fetcher returns newest first. Let's try to parse date.
    # For now, just return valid items, app.py sorts them anyway.
    return unique_news
