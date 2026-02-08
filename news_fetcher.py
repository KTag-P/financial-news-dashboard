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
import re

def is_valid_content(text):
    """Check if scraped text is actual article content, not garbage."""
    if not text or len(text) < 50:
        return False
    
    # Garbage patterns to reject
    garbage_patterns = [
        "SNS 기사보내기",
        "카카오스토리",
        "카카오톡",
        "네이버밴드",
        "네이버블로그",
        "핀터레스트",
        "기사스크랩하기",
        "다른 공유 찾기",
        "이메일(으)로 기사보내기",
        "좋아요 공유하기",
        "트위터 공유",
        "페이스북 공유",
        "클릭해 주세요",
        "구독하기",
        "로그인이 필요합니다",
    ]
    
    # Check if content is mostly garbage
    garbage_count = sum(1 for p in garbage_patterns if p in text)
    if garbage_count >= 2:
        return False
    
    # Check if content is too short after cleaning
    clean = re.sub(r'\s+', ' ', text).strip()
    if len(clean) < 80:
        return False
    
    # Check for actual Korean sentences (should have more than just buttons)
    korean_chars = len(re.findall(r'[가-힣]', text))
    if korean_chars < 50:
        return False
        
    return True

def scrape_with_naver_fallback(title, original_link, headers):
    """
    Scrapes article content with quality validation.
    Rejects garbage content like SNS buttons and tries fallbacks.
    
    Returns: (content, summary)
    """
    content = ""
    summary = ""
    
    # 1. Try direct scraping with newspaper3k
    try:
        article = Article(original_link, language='ko')
        article.download()
        article.parse()
        content = article.text
        
        # CRITICAL: Validate content quality
        if is_valid_content(content):
            try:
                article.nlp()
                summary = article.summary
            except:
                summary = content[:400] + "..." if len(content) > 400 else content
            return content, summary
        else:
            content = ""  # Reset and try fallback
    except:
        pass
    
    # 2. Fallback: Search Naver News with article title
    try:
        search_title = re.sub(r'\s*-\s*[가-힣A-Za-z0-9.]+$', '', title)[:50]
        naver_search_url = f"https://search.naver.com/search.naver?where=news&query={quote(search_title)}"
        
        response = requests.get(naver_search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_links = soup.select('a.news_tit')
        if news_links:
            naver_link = news_links[0].get('href', '')
            
            if naver_link and 'naver.com' in naver_link:
                article = Article(naver_link, language='ko')
                article.download()
                article.parse()
                content = article.text
                
                if is_valid_content(content):
                    try:
                        article.nlp()
                        summary = article.summary
                    except:
                        summary = content[:400] + "..." if len(content) > 400 else content
                    return content, summary
    except:
        pass
    
    # 3. Try Daum search
    try:
        search_title = re.sub(r'\s*-\s*[가-힣A-Za-z0-9.]+$', '', title)[:40]
        daum_url = f"https://search.daum.net/search?w=news&q={quote(search_title)}"
        resp = requests.get(daum_url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        news_links = soup.select('a.tit_main') or soup.select('a.f_link_b')
        if news_links:
            daum_link = news_links[0].get('href', '')
            if daum_link:
                article = Article(daum_link, language='ko')
                article.download()
                article.parse()
                content = article.text
                
                if is_valid_content(content):
                    summary = content[:400] + "..." if len(content) > 400 else content
                    return content, summary
    except:
        pass
    
    # 4. Final fallback: Meta description
    try:
        response = requests.get(original_link, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                    soup.find('meta', attrs={'property': 'og:description'})
        
        if meta_desc:
            content = meta_desc.get('content', '')
            if content and len(content) > 30:
                return content, content
    except:
        pass
    
    # 5. Last resort: Use title as content
    return title, title

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

def fetch_business_reports(company_name):
    """
    Fetches specific business reports/disclosures (Management, Audit, Earnings).
    """
    keywords = ['사업보고서', '경영공시', '실적발표', '영업실적', '감사보고서', '주주총회', '신년사']
    query = ' OR '.join(keywords)
    encoded_query = quote(f'{company_name} ({query}) when:1y') # 1 year lookback for reports
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    items = []
    
    for entry in feed.entries:
        if len(items) >= 3: 
            break
        
        items.append({
            'title': f"[공시/보고서] {entry.title}",
            'link': entry.link,
            'published': entry.published,
            'summary': "주요 경영 공시 및 사업 보고서 관련 뉴스입니다.",
            'full_content': "원문 참조 요망." 
        })
    return items

def _get_query(company_name):
    exclusions = "-기부 -봉사 -인사 -동정 -화촉 -부고 -포토 -사진 -개최 -참석"
    
    if company_name == "Capital Industry":
        return f"캐피탈 (업황 OR 전망 OR 연체율 OR PF OR 부동산 OR 금리 OR 여전채) {exclusions}"
    elif company_name == "Macro Economy":
        # Simplified but focused query for Google News RSS
        q1 = "경제성장률 OR GDP 성장률 OR 한국은행 경제전망 OR KDI 전망"
        q2 = "코스피 전망 OR 증시 전망 OR 환율 전망 OR 국고채 금리 OR 기준금리 동결 OR 기준금리 인하"
        return f"({q1} OR {q2}) -비트코인 -가상화폐 -특징주 -급등주 -AI속보"
    elif company_name == "IBK Capital":
        return f"IBK캐피탈 (사업 OR 실적 OR 투자 OR 펀드 OR 금융 OR 지원 OR MOU OR 경영) {exclusions}"
    elif company_name == "IBK Parent":
        return f"IBK기업은행 (사업 OR 실적 OR 투자 OR 지원 OR 정책 OR 금융) {exclusions}"
    elif company_name == "KDB Capital":
        return f"산은캐피탈 (사업 OR 실적 OR 투자 OR 펀드 OR 금융 OR 지원 OR MOU) {exclusions}"
    elif company_name == "KDB Parent":
        return f"KDB산업은행 (사업 OR 실적 OR 투자 OR 펀드 OR 구조조정 OR 지원) {exclusions}"
    else:
        return f"{company_name} {exclusions}"

def fetch_news_period(company_name, start_date, end_date, max_items=50):
    """
    Fetches news for a specific period (YYYY-MM-DD to YYYY-MM-DD).
    Actually scrapes full content using multiple fallback methods.
    """
    query = _get_query(company_name)
    
    # Google News supports 'after:YYYY-MM-DD before:YYYY-MM-DD'
    google_period = f"after:{start_date} before:{end_date}"
    
    final_query = f'{query} {google_period}'
    encoded_query = quote(final_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    items = []
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    for entry in feed.entries:
        if len(items) >= max_items: break
        
        title = entry.title
        
        # Decode Google News redirect
        try:
             decoded_link = googlenewsdecoder.new_decoderv1(entry.link, interval=0.1)['decoded_url']
        except:
             decoded_link = entry.link
             
        # ACTUALLY SCRAPE FULL CONTENT with fallbacks
        content, summary = scrape_with_naver_fallback(title, decoded_link, headers)
        
        # If still no content, try Daum search as additional fallback
        if not content or len(content) < 50:
            try:
                search_title = re.sub(r'\s*-\s*[가-힣A-Za-z0-9.]+$', '', title)[:40]
                daum_url = f"https://search.daum.net/search?w=news&q={quote(search_title)}"
                resp = requests.get(daum_url, headers=headers, timeout=5)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Find news link
                news_links = soup.select('a.tit_main') or soup.select('a.f_link_b')
                if news_links:
                    daum_link = news_links[0].get('href', '')
                    if daum_link:
                        article = Article(daum_link, language='ko')
                        article.download()
                        article.parse()
                        if len(article.text) > 100:
                            content = article.text
                            summary = content[:400] + "..." if len(content) > 400 else content
            except:
                pass
        
        # Final fallback: use RSS snippet
        if not content or len(content) < 50:
            snippet = ""
            if hasattr(entry, 'summary'):
                snippet = entry.summary
            elif hasattr(entry, 'description'):
                snippet = entry.description
            snippet = re.sub(r'<[^>]+>', '', snippet)
            snippet = re.sub(r'&nbsp;', ' ', snippet)
            snippet = re.sub(r'&amp;', '&', snippet)
            content = snippet.strip() if snippet else title
            summary = content
              
        items.append({
            'title': title,
            'link': decoded_link,
            'published': entry.published,
            'summary': summary if summary else content[:300], 
            'full_content': content, 
        })
        time.sleep(0.3)  # Be nice to servers
        
    return items

def fetch_news(company_name, days=1, max_items=10, is_retry=False):
    query = _get_query(company_name)


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
                 
                # Tag if content is very short (likely just meta description)
                if len(content) < 200:
                    content = f"[요약본] {content} (상세 내용은 원문 링크를 참조하세요)"

            except Exception as e:
                content = f"스크래핑 실패: {str(e)}"
                summary = "스크래핑 오류"
        else:
            # is_retry: Still try to scrape content using Naver fallback
            headers = headers_list[len(news_items) % len(headers_list)]
            content, summary = scrape_with_naver_fallback(title, decoded_link, headers)
            if not content:
                content = "원문 내용을 가져올 수 없습니다. 원문 링크를 확인해 주세요."
                summary = title

            
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
