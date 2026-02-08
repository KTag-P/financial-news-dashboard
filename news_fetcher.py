import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
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
            return scrape_naver_news(target_url), target_url
            
    except Exception as e:
        print(f"Naver Search failed: {e}")
    return None, None

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
        return None, "newspaper3k not installed", url
        
    text = None
    error = None
    
    # 1. Try Original URL
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
        
        # Check if content is blocked/short (e.g. Hankyung often blocks or redirects)
        if not text or len(text) < 200:
             raise Exception("Content too short or empty")
             
        return text, None, url
        
    except Exception as e:
        error = str(e)
        # 2. Naver Fallback
        if title:
            print(f"Falling back to Naver for: {title}")
            naver_text, naver_url = search_naver_news_content(title)
            if naver_text:
                return naver_text, None, naver_url
    
    return text, error, url

def fetch_news(query, days=1, max_items=10):
    """
    Fetches news for a given query from Google News RSS.
    Includes full content scraping.
    """
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    
    # Process only the top N items to avoid timeouts
    entries = feed.entries[:max_items]
    
    # Create a placeholder for progress if running in streamlit? 
    # No, keep logic pure. Caller handles progress.
    
    for entry in entries:
        title = entry.title
        link = entry.link
        published = entry.published
        
        # 1. Decode URL
        real_url = decode_url(link)
        
        # 2. Scrape Content
        full_text, error, final_link = scrape_content(real_url, title)
        
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
            'original_link': link
        })
        
        # Be polite to servers? 
        # Since we are scraping different domains, we don't strictly need a sleep 
        # but decoding might hit google.
        time.sleep(0.5) 
        
    return news_items
