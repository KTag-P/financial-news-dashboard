import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import quote
from dateutil import parser
import time
from time import mktime
import googlenewsdecoder
from newspaper import Article

def fetch_1year_key_issues(company_name, max_items=5):
    """
    Fetches key issues (CEO, M&A) from the last 365 days.
    """
    keywords = ['CEO', '대표이사', '인수', '합병', 'M&A', '신용등급', '배당', '최대실적']
    query = ' OR '.join(keywords)
    encoded_query = quote(f'{company_name} ({query}) when:1y')
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    issues = []
    
    for entry in feed.entries:
        if len(issues) >= max_items:
            break
            
        title = entry.title
        published = entry.published
        
        # Simple relevance check
        if any(k in title for k in keywords):
             issues.append({
                'title': title,
                'link': entry.link,
                'published': published,
                'summary': "핵심 키워드 포함 기사"
             })
             
    return issues

def fetch_recruitment_news(company_name):
    """
    Fetches specific recruitment related news/notices.
    """
    keywords = ['채용', '공채', '신입', '인턴', '모집', '선발']
    query = ' OR '.join(keywords)
    encoded_query = quote(f'{company_name} ({query}) when:30d') # Look back 30 days for recruitment
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    items = []
    
    for entry in feed.entries:
        if len(items) >= 3: # Limit to top 3
            break
        
        items.append({
            'title': f"[채용] {entry.title}",
            'link': entry.link,
            'published': entry.published,
            'summary': "채용 관련 최신 뉴스/공고입니다."
        })
    return items

def fetch_news_period(company_name, start_date, end_date, max_items=10):
    """
    Fetches news for a specific date range.
    """
    # Query Logic (Same as fetch_news)
    if company_name == "Capital Industry":
        query = "캐피탈 (업황 OR 전망 OR 연체율 OR PF OR 부동산 OR 금리)"
    elif company_name == "Macro Economy":
        query = "(기준금리 OR 국고채 OR 환율 OR 소비자물가 OR 경기침체) -주식 -종목"
    elif company_name == "IBK Capital":
        query = "IBK캐피탈"
    elif company_name == "IBK Parent":
        query = "IBK기업은행"
    elif company_name == "KDB Capital":
        query = "산은캐피탈"
    elif company_name == "KDB Parent":
        query = "KDB산업은행"
    else:
        query = company_name

    # Check for KDB CEO keywords if KDB
    if company_name == "KDB Capital" and start_date.year == 2024:
         query += " OR 산은캐피탈 (이병호 OR 대표)"

    # Format: after:YYYY-MM-DD before:YYYY-MM-DD
    # Note: Google News 'after/before' often works better than 'when' for archives
    google_period = f"after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
    
    final_query = f'{query} {google_period}'
    encoded_query = quote(final_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    
    news_items = []
    # ... (Rest is similar, reuse logic ideally, but for now copying core loop for safety)
    
    headers_list = [
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'}
    ]

    for entry in feed.entries:
        if len(news_items) >= max_items:
            break
            
        title = entry.title
        link = entry.link
        published = entry.published
        
        # ... (Decode & Scrape logic reuse)
        try:
             decoded_link = googlenewsdecoder.new_decoderv1(link, interval=0.0)['decoded_url']
        except:
             decoded_link = link
             
        # Scrape
        content = ""
        summary = ""
        try:
            article = Article(decoded_link, language='ko')
            article.download()
            article.parse()
            try:
                article.nlp()
                summary = article.summary
            except:
                summary = ""
            
            content = article.text
            if not summary:
                 summary = content[:500] + "..." if len(content) > 500 else content
                 
        except:
            summary = "요약 실패"
            
        news_items.append({
            'title': title,
            'link': decoded_link,
            'published': published,
            'summary': summary,
            'full_content': content,  # Save full text
            'original_link': decoded_link
        })
        time.sleep(0.1)
        
    return news_items

def fetch_news(company_name, days=1, max_items=10, is_retry=False):
    # Search Query Logic (Separated)
    if company_name == "Capital Industry":
        query = "캐피탈 (업황 OR 전망 OR 연체율 OR PF OR 부동산 OR 금리 OR 여전채)"
    elif company_name == "Macro Economy":
        query = "(기준금리 OR 국고채 OR 환율 OR 소비자물가 OR 경기침체 OR 유가) -주식 -종목"
    elif company_name == "IBK Capital":
        query = "IBK캐피탈"
    elif company_name == "IBK Parent":
        query = "IBK기업은행"
    elif company_name == "KDB Capital":
        query = "산은캐피탈"
    elif company_name == "KDB Parent":
        query = "KDB산업은행"
    else:
        query = company_name

    today = datetime.now()
    
    # Date Logic
    if is_retry:
        google_period = "when:1y" # Fallback to 1 year
        cutoff_date = today - timedelta(days=365)
    else:
        if days <= 1:
            google_period = "when:1d"
            cutoff_date = today - timedelta(hours=24)
        elif days <= 7:
            google_period = "when:7d"
            cutoff_date = today - timedelta(days=days)
        elif days <= 30:
            google_period = "when:30d"
            cutoff_date = today - timedelta(days=days)
        else:
            google_period = "when:1y"
            cutoff_date = today - timedelta(days=days)

    cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Final Query
    final_query = f'{query} {google_period}'
    encoded_query = quote(final_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    
    news_items = []
    seen_titles = set()

    headers_list = [
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'},
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'}
    ]

    for entry in feed.entries:
        if len(news_items) >= max_items:
            break
            
        title = entry.title
        link = entry.link
        published = entry.published
        
        if title in seen_titles:
            continue
        seen_titles.add(title)

        # Strict Date Filter (Python Side)
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                pub_struct = entry.published_parsed
                pub_dt = datetime.fromtimestamp(mktime(pub_struct))
                
                if pub_dt < cutoff_date:
                    continue
            except Exception:
                pass 
        
        # Resolve Google News Redirect
        try:
            decoded_link = googlenewsdecoder.new_decoderv1(link, interval=0.1)['decoded_url']
        except:
            decoded_link = link
            
        # Scrape Content with Fallback
        content = ""
        image_url = None
        
        if not is_retry: # Optimize: Don't deep scrape on retry/fallback to save time, or keep it if needed.
                         # User wants content, so we scrape.
            try:
                headers = headers_list[len(news_items) % len(headers_list)]
                
                # 1. Try Newspaper3k with NLP Summary
                article = Article(decoded_link, language='ko') # Set language to Korean
                article.download()
                article.parse()
                
                # Attempt NLP Summarization
                try:
                    article.nlp()
                    summary = article.summary
                except:
                    summary = ""

                content = article.text
                image_url = article.top_image
                
                # Fallback if NLP summary fails or is empty
                if not summary or len(summary) < 50:
                     if len(content) > 500:
                         summary = content[:400] + "..." # Fallback to slice
                     else:
                         summary = content
                
                # 2. Fallback if newspaper3k failed completely
                if len(content) < 100:
                    response = requests.get(decoded_link, headers=headers, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                    if meta_desc:
                        content = meta_desc.get('content', '')
                        summary = content
                        
                if not content:
                     content = "내용을 가져올 수 없습니다."
                     summary = "요약 불가 (원문 참조)"

            except Exception as e:
                content = f"스크래핑 실패: {str(e)}"
                summary = "스크래핑 오류"
        else:
            content = "과거 기사입니다."
            summary = "과거 기사 (원문 참조)"

            
        # Tag as recent-past if retry
        if is_retry:
            title = f"[최근] {title}"

        news_items.append({
            'title': title,
            'link': decoded_link,
            'published': published,
            'summary': summary,
            'full_content': content, # Save full text
            'image': image_url,
            'original_link': decoded_link
        })
        
        if not is_retry:
            time.sleep(0.5) 
        
    # Auto-Fallback Logic
    if not news_items and not is_retry and company_name not in ["Capital Industry", "Macro Economy"]:
        # If no news in period, try fetching recent 1 year (limit 3)
        # print(f"DEBUG: No news for {company_name} in {days}d. Retrying with 1y fallback.")
        return fetch_news(company_name, days=365, max_items=3, is_retry=True)

    return news_items
