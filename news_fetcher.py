import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
from time import mktime
from urllib.parse import quote
import requests
import re

try:
    from googlenewsdecoder import new_decoderv1
except ImportError:
    new_decoderv1 = None

try:
    from newspaper import Article
except ImportError:
    Article = None

def decode_url(url):
    """
    Decodes Google News RSS URL to the original publisher URL.
    """
    if new_decoderv1:
        try:
            decoded = new_decoderv1(url)
            if decoded.get('status'):
                return decoded['decoded_url']
        except Exception as e:
            print(f"Error decoding URL {url}: {e}")
    return url

def search_naver_news_content(title):
    try:
        # Search Naver News for the title
        search_url = f"https://search.naver.com/search.naver?where=news&query={title}"
        headers = { 'User-Agent': 'Mozilla/5.0' }
        resp = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Find first news link that is 'news.naver.com' (smart fallback)
        # Look for 'info_group' > 'a' tags
        
        links = soup.select('a.info')
        target_url = None
        for link in links:
            href = link.get('href')
            if href and 'news.naver.com' in href:
                target_url = href
                break
        
        if target_url:
            # Scrape Naver News directly (easy to scrape)
            # Naver scraping doesn't extract image yet, so return None for image
            return scrape_naver_news(target_url), None, target_url
            
    except Exception as e:
        print(f"Naver Search failed: {e}")
    return None, None, None

def scrape_naver_news(url):
    try:
        headers = { 'User-Agent': 'Mozilla/5.0' }
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Naver news content id is usually 'dic_area'
        content_div = soup.find('div', {'id': 'dic_area'})
        if content_div:
            return content_div.get_text(separator='\n\n', strip=True)
        else:
            # Fallback for entertainment/sports?
            content_div = soup.find('div', {'id': 'newsEndContents'})
            if content_div:
                return content_div.get_text(separator='\n\n', strip=True)
                
    except Exception as e:
        print(f"Naver Scrape failed: {e}")
    return None

def scrape_content(url, title=''):
    """
    Scrapes the full content of the article using newspaper3k.
    If fails or content is short, searches Naver News.
    Returns (text, error_message, final_url).
    """
    if not Article:
        return None, None, "newspaper3k not installed", url
        
    text = None
    image = None # Initialize image
    error = None
    
    # 1. Try Original URL
    try:
        # Attempt to download and parse article
        article = Article(url, language='ko') # Added language='ko'
        article.download()
        article.parse()
        
        # Check if content is substantial
        if len(article.text) > 50: # Changed threshold from 200 to 50
            text = article.text
            image = article.top_image
        else:
            # Fallback message if content is too short
            text = "내용을 불러올 수 없습니다. 원문 링크를 확인해주세요."
            image = None
            # Do not raise an exception here, allow Naver fallback if title is present
            # or return this message if no Naver fallback.
            
        return text, image, None, url
        
    except Exception as e:
        error = str(e)
        # print(f"Error scraping {url}: {e}") # Uncomment for debugging
        text = "스크래핑 중 오류가 발생했습니다." # Set text to error message
        image = None # Ensure image is None on error
        
        # 2. Naver Fallback
        if title:
            print(f"Falling back to Naver for: {title}")
            naver_text, naver_image, naver_url = search_naver_news_content(title)
            if naver_text:
                return naver_text, naver_image, None, naver_url
    
    return text, None, error, url

def fetch_news(query, days=1, max_items=10):
    """
    Fetches news for a given query from Google News RSS.
    Includes full content scraping.
    """
    today = datetime.now()
    # Strict 24h lookback if days=1, otherwise days-based
    if days <= 1:
        cutoff_date = today - timedelta(hours=24)
    else:
        cutoff_date = today - timedelta(days=days)
        cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Expanded Keywords for Industry & Macro
    keywords = {
        'IBK Capital': ['IBK캐피탈', 'IBK기업은행 캐피탈'],
        'KDB Capital': ['산은캐피탈', 'KDB산업은행 캐피탈'],
        'Capital Industry': ['캐피탈사 업황', '여신전문금융', '캐피탈 채권', 'PF 대출 부실'],
        'Macro Economy': ['한국 기준금리', '원달러 환율 전망', '국고채 금리', '회사채 금리']
    }
    
    # The original 'query' parameter is now treated as 'company_name' for keyword lookup
    # If 'query' is not in keywords, it will be used directly in the search.
    search_terms = keywords.get(query, [query])
    
    # Construct Query
    # For Google News RSS, 'when:1d' works well for recent.
    # We combine it with python-side filtering for precision.
    term_query = ' OR '.join([f'"{t}"' for t in search_terms])
    if days <= 1:
         encoded_query = quote(f"({term_query}) when:1d")
    else:
         encoded_query = quote(f"({term_query}) when:{days}d")
    
    # Using Google News RSS for broader coverage
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    
    news_items = []
    seen_titles = set() # Added to prevent duplicate articles

    # Process only the top N items to avoid timeouts
    entries = feed.entries[:max_items]
    
    for entry in entries:
        # Strict Date Filter
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                pub_struct = entry.published_parsed
                pub_dt = datetime.fromtimestamp(mktime(pub_struct))
                
                if pub_dt < cutoff_date:
                    continue
            except Exception:
                pass # If parsing fails, maybe include? or safe skip. Safe skip.
        else:
            # If no date, and we want strict 24h, safer to skip unless it's very relevant?
            # Google News usually has dates.
            pass

        title = entry.title
        link = entry.link
        published = entry.published
        
        # 1. Decode URL
        real_url = decode_url(link)
        
        # 2. Scrape Content
        full_text, image_url, error, final_link = scrape_content(real_url, title)
        
        # 3. Fallback to RSS summary if scraping failed or text is empty
        summary_text = ''
        if full_text and len(full_text) > 50:
             summary_text = full_text
        else:
             # Fallback to cleaning the RSS summary
             if 'summary' in entry:
                soup = BeautifulSoup(entry.summary, 'html.parser')
                summary_text = soup.get_text(separator=' ', strip=True)
             if error:
                 print(f"Scraping failed for {real_url}: {error}")

        news_items.append({
            'title': title,
            'link': final_link, # Use the final resolved URL (Naver or Original)
            'published': published,
            'summary': summary_text,
            'image': image_url,
            'original_link': link
        })
        
        # Be polite to servers? 
        # Since we are scraping different domains, we don't strictly need a sleep 
        # but decoding might hit google.
        time.sleep(0.5) 
        
    return news_items
