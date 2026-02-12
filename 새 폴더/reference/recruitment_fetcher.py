"""
채용공고 자동 크롤링 모듈.
Google News RSS + 사람인/잡코리아 검색으로 IBK캐피탈, 산은캐피탈 채용정보를 수집합니다.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import quote
import re
import json
import os

# 크롤링 대상 회사 설정
COMPANIES = {
    "IBK": {
        "name": "IBK캐피탈",
        "aliases": ["IBK캐피탈", "IBK Capital", "아이비케이캐피탈"],
        "career_url": "https://ibkcapital.co.kr/recruit",
        "saramin_keyword": "IBK캐피탈",
    },
    "KDB": {
        "name": "산은캐피탈",
        "aliases": ["산은캐피탈", "KDB캐피탈", "KDB Capital"],
        "career_url": "https://www.kdbcapital.co.kr",
        "saramin_keyword": "산은캐피탈",
    }
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

RECRUITMENT_KEYWORDS = ['채용', '공채', '신입', '인턴', '모집', '선발', '경력', '수시채용', '채용형']
STORAGE_FILE = "recruitment_data.json"


def _load_stored_recruitment():
    """저장된 채용 데이터 로드."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"IBK": [], "KDB": [], "_last_checked": ""}


def _save_recruitment(data):
    """채용 데이터 저장."""
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def fetch_recruitment_from_news(company_key):
    """Google News RSS로 채용 관련 뉴스 수집."""
    config = COMPANIES.get(company_key)
    if not config:
        return []

    items = []
    queries = [
        f'"{config["name"]}" (채용 OR 공채 OR 모집 OR 인턴)',
        f'"{config["name"]}" (신입 OR 경력 OR 수시채용)',
    ]

    for query in queries:
        try:
            encoded_query = quote(f'{query} when:90d')
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss_url)

            for entry in feed.entries:
                if len(items) >= 10:
                    break

                title = entry.title
                # 채용 관련 키워드 포함 여부 확인
                if not any(kw in title for kw in RECRUITMENT_KEYWORDS):
                    continue

                # 중복 체크
                if any(item['title'] == title for item in items):
                    continue

                items.append({
                    'title': title,
                    'link': entry.link,
                    'published': entry.published,
                    'source': 'google_news',
                    'company_key': company_key,
                })
        except Exception:
            continue

    return items


def fetch_recruitment_from_saramin(company_key):
    """사람인에서 채용공고 검색."""
    config = COMPANIES.get(company_key)
    if not config:
        return []

    items = []
    try:
        search_url = f"https://www.saramin.co.kr/zf_user/search?searchType=search&searchword={quote(config['saramin_keyword'])}&recruitSort=relation"
        response = requests.get(search_url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # 채용공고 리스트 파싱
        job_cards = soup.select('.item_recruit') or soup.select('.list_body .list_item')

        for card in job_cards[:5]:
            try:
                title_elem = card.select_one('.job_tit a') or card.select_one('.str_tit a')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = f"https://www.saramin.co.kr{link}"

                # 회사명 확인
                company_elem = card.select_one('.corp_name a') or card.select_one('.company_nm a')
                company_name = company_elem.get_text(strip=True) if company_elem else ""

                # 해당 회사 공고인지 확인
                if not any(alias in company_name for alias in config['aliases']):
                    if not any(alias in title for alias in config['aliases']):
                        continue

                # 마감일 추출
                deadline_elem = card.select_one('.job_date .date') or card.select_one('.date')
                deadline = deadline_elem.get_text(strip=True) if deadline_elem else ""

                # 조건 추출
                conditions_elem = card.select_one('.job_condition')
                conditions = conditions_elem.get_text(strip=True, separator=' | ') if conditions_elem else ""

                items.append({
                    'title': f"[사람인] {title}",
                    'link': link,
                    'published': datetime.now().strftime("%Y-%m-%d"),
                    'deadline': deadline,
                    'conditions': conditions,
                    'source': 'saramin',
                    'company_key': company_key,
                })
            except Exception:
                continue

    except Exception:
        pass

    return items


def fetch_recruitment_from_jobkorea(company_key):
    """잡코리아에서 채용공고 검색."""
    config = COMPANIES.get(company_key)
    if not config:
        return []

    items = []
    try:
        search_url = f"https://www.jobkorea.co.kr/Search/?stext={quote(config['name'])}&tabType=recruit"
        response = requests.get(search_url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        job_items = soup.select('.list-default .list-post') or soup.select('.recruit-info')

        for item in job_items[:5]:
            try:
                title_elem = item.select_one('.title a') or item.select_one('.post-list-info a')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = f"https://www.jobkorea.co.kr{link}"

                # 회사명 확인
                company_elem = item.select_one('.name a') or item.select_one('.corp-name a')
                company_name = company_elem.get_text(strip=True) if company_elem else ""

                if not any(alias in company_name for alias in config['aliases']):
                    if not any(alias in title for alias in config['aliases']):
                        continue

                items.append({
                    'title': f"[잡코리아] {title}",
                    'link': link,
                    'published': datetime.now().strftime("%Y-%m-%d"),
                    'source': 'jobkorea',
                    'company_key': company_key,
                })
            except Exception:
                continue

    except Exception:
        pass

    return items


def check_for_new_recruitment():
    """
    모든 소스에서 새 채용공고 확인.
    하루 1회만 실행하도록 체크합니다.
    Returns: dict with 'IBK' and 'KDB' lists, plus '_new_found' count
    """
    stored = _load_stored_recruitment()

    # 하루 1회 체크 제한
    last_checked = stored.get('_last_checked', '')
    today = datetime.now().strftime("%Y-%m-%d")

    if last_checked == today:
        return stored

    new_count = 0

    for company_key in ["IBK", "KDB"]:
        existing_titles = {item['title'] for item in stored.get(company_key, [])}

        # 각 소스에서 수집
        news_items = fetch_recruitment_from_news(company_key)
        saramin_items = fetch_recruitment_from_saramin(company_key)
        jobkorea_items = fetch_recruitment_from_jobkorea(company_key)

        all_new = news_items + saramin_items + jobkorea_items

        for item in all_new:
            # 제목 기반 중복 제거 (정규화)
            normalized_title = re.sub(r'\[.*?\]\s*', '', item['title']).strip()
            if normalized_title not in existing_titles and item['title'] not in existing_titles:
                stored.setdefault(company_key, []).insert(0, item)
                existing_titles.add(normalized_title)
                existing_titles.add(item['title'])
                new_count += 1

    stored['_last_checked'] = today
    stored['_new_found'] = new_count
    _save_recruitment(stored)

    return stored


def get_all_recruitment_info(company_key):
    """
    하드코딩된 과거 채용정보 + 자동수집된 최신 데이터를 통합하여 반환.
    Returns: list of recruitment items (최신순 정렬)
    """
    import company_data

    # 1. 하드코딩된 과거 데이터 가져오기
    company_name = "IBK Capital" if company_key == "IBK" else "KDB Capital"
    static_data = company_data.company_info.get(company_name, {})
    static_recruitment = static_data.get('recruitment', [])

    # 2. 자동수집 데이터 로드
    stored = _load_stored_recruitment()
    auto_items = stored.get(company_key, [])

    # 3. 자동수집 데이터를 표시 형식으로 변환
    auto_recruitment = []
    for item in auto_items:
        auto_recruitment.append({
            'title': f"🔄 {item['title']}",
            'period': item.get('published', '')[:10],
            'roles': [],
            'scale': '',
            'note': f"출처: {item.get('source', 'auto')} | {item.get('conditions', '')}".strip(' |'),
            'link': item.get('link', ''),
            'deadline': item.get('deadline', ''),
            'is_auto': True,
        })

    # 4. 통합 (자동수집 최신 데이터 + 하드코딩 과거 데이터)
    return auto_recruitment + static_recruitment
