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
    Removes duplicate news items based on title similarity.
    Groups 'Personnel' news aggressively.
    """
    unique_news = []
    seen_titles = []
    
    has_personnel_news = False
    
    for news in news_list:
        title = news['title']
        
        # Special handling for Personnel news
        if is_personnel_news(title):
            if has_personnel_news:
                continue # Skip subsequent personnel news
            has_personnel_news = True
            unique_news.append(news)
            continue
            
        is_duplicate = False
        for seen_title in seen_titles:
            # Check similarity
            if is_similar(title, seen_title):
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_news.append(news)
            seen_titles.append(title)
            
    return unique_news
