import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import quote
from dateutil import parser
import time
from time import mktime
import googlenewsdecoder
import trafilatura
import re


def _scrape_article(url):
    """
    Scrapes article content using trafilatura (better Korean support).
    Returns: (content, summary)
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "", ""

        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
            target_language='ko'
        )

        if content and len(content) > 100:
            summary = content[:400] + "..." if len(content) > 400 else content
            return content, summary
    except Exception:
        pass

    return "", ""


def _scrape_with_meta_fallback(url, headers):
    """Try meta description as final fallback."""
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                    soup.find('meta', attrs={'property': 'og:description'}) or \
                    soup.find('meta', attrs={'name': 'twitter:description'})

        if meta_desc:
            content = meta_desc.get('content', '')
            if content:
                return content, content
    except Exception:
        pass
    return "", ""


def scrape_with_naver_fallback(title, original_link, headers):
    """
    Scrapes article content with multiple fallbacks:
    1. trafilatura (direct)
    2. Naver News search + trafilatura
    3. Meta description
    """
    # 1. Try direct scraping with trafilatura
    content, summary = _scrape_article(original_link)
    if content and len(content) > 100:
        return content, summary

    # 2. Fallback: Search Naver News with article title
    try:
        search_title = re.sub(r'\s*-\s*[가-힣A-Za-z0-9]+$', '', title)
        search_title = search_title[:50]

        naver_search_url = f"https://search.naver.com/search.naver?where=news&query={quote(search_title)}"

        response = requests.get(naver_search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        news_links = soup.select('a.news_tit')
        if news_links:
            naver_link = news_links[0].get('href', '')
            if naver_link and 'naver.com' in naver_link:
                content, summary = _scrape_article(naver_link)
                if content and len(content) > 100:
                    return content, summary
    except Exception:
        pass

    # 3. Final fallback: meta description
    return _scrape_with_meta_fallback(original_link, headers)


def fetch_1year_key_issues(company_name, max_items=5):
    """Fetches key issues (CEO, M&A) from the last 365 days."""
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

        if any(k in title for k in keywords):
            issues.append({
                'title': title,
                'link': entry.link,
                'published': published,
                'summary': "핵심 키워드 포함 기사"
            })

    return issues


def fetch_recruitment_news(company_name):
    """Fetches specific recruitment related news/notices."""
    keywords = ['채용', '공채', '신입', '인턴', '모집', '선발']
    query = ' OR '.join(keywords)
    encoded_query = quote(f'{company_name} ({query}) when:30d')
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

    feed = feedparser.parse(rss_url)
    items = []

    for entry in feed.entries:
        if len(items) >= 3:
            break
        items.append({
            'title': f"[채용] {entry.title}",
            'link': entry.link,
            'published': entry.published,
            'summary': "채용 관련 최신 뉴스/공고입니다."
        })
    return items


def fetch_business_reports(company_name):
    """Fetches specific business reports/disclosures."""
    keywords = ['사업보고서', '경영공시', '실적발표', '영업실적', '감사보고서', '주주총회', '신년사']
    query = ' OR '.join(keywords)
    encoded_query = quote(f'{company_name} ({query}) when:1y')
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
    Scrapes full content using trafilatura with multiple fallbacks.
    """
    query = _get_query(company_name)

    google_period = f"after:{start_date} before:{end_date}"
    final_query = f'{query} {google_period}'
    encoded_query = quote(final_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

    feed = feedparser.parse(rss_url)
    items = []

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for entry in feed.entries:
        if len(items) >= max_items:
            break

        title = entry.title

        # Decode Google News redirect
        try:
            decoded_link = googlenewsdecoder.new_decoderv1(entry.link, interval=0.1)['decoded_url']
        except Exception:
            decoded_link = entry.link

        # Scrape full content with fallbacks
        content, summary = scrape_with_naver_fallback(title, decoded_link, headers)

        # Daum search fallback
        if not content or len(content) < 50:
            try:
                search_title = re.sub(r'\s*-\s*[가-힣A-Za-z0-9.]+$', '', title)[:40]
                daum_url = f"https://search.daum.net/search?w=news&q={quote(search_title)}"
                resp = requests.get(daum_url, headers=headers, timeout=5)
                soup = BeautifulSoup(resp.text, 'html.parser')

                news_links = soup.select('a.tit_main') or soup.select('a.f_link_b')
                if news_links:
                    daum_link = news_links[0].get('href', '')
                    if daum_link:
                        content, summary = _scrape_article(daum_link)
            except Exception:
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
        time.sleep(0.3)

    return items


def fetch_news(company_name, days=1, max_items=10, is_retry=False):
    """
    Main news fetching function.
    Uses Google News RSS + trafilatura scraping with fallbacks.
    """
    query = _get_query(company_name)

    today = datetime.now()

    # Date Logic
    if is_retry:
        google_period = "when:1y"
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

    final_query = f'{query} {google_period}'
    encoded_query = quote(final_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

    feed = feedparser.parse(rss_url)

    news_items = []
    seen_titles = set()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

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
        except Exception:
            decoded_link = link

        # Scrape Content with Fallback
        content = ""
        summary = ""

        # trafilatura + Naver fallback
        content, summary = scrape_with_naver_fallback(title, decoded_link, headers)

        if not content or len(content) < 100:
            # Meta description fallback
            content_meta, summary_meta = _scrape_with_meta_fallback(decoded_link, headers)
            if content_meta:
                content = content_meta
                summary = summary_meta

        if not content:
            content = "내용을 가져올 수 없습니다."
            summary = "요약 불가 (원문 참조)"

        if len(content) < 200 and not content.startswith("[요약본]"):
            content = f"[요약본] {content} (상세 내용은 원문 링크를 참조하세요)"

        if not summary or len(summary) < 50:
            if len(content) > 500:
                summary = content[:400] + "..."
            else:
                summary = content

        # Tag as recent-past if retry
        if is_retry:
            title = f"[최근] {title}"

        news_items.append({
            'title': title,
            'link': decoded_link,
            'published': published,
            'summary': summary,
            'full_content': content,
            'original_link': decoded_link
        })

        if not is_retry:
            time.sleep(0.5)

    # Auto-Fallback Logic
    if not news_items and not is_retry and company_name not in ["Capital Industry", "Macro Economy"]:
        return fetch_news(company_name, days=365, max_items=3, is_retry=True)

    return news_items
