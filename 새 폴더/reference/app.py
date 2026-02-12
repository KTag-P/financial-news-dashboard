import streamlit as st
import news_fetcher
import deduplicator
import report_generator
import company_data
import market_data_fetcher
import recruitment_fetcher
import socket
import notebooklm_client
import pandas as pd
import altair as alt
from dateutil import parser
import news_storage
from datetime import datetime

st.set_page_config(page_title="캐피탈사 채용 대비", layout="wide")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"

# Custom CSS for Fonts and Badges
st.markdown("""
<style>
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, "Helvetica Neue", Arial, "Noto Sans KR", sans-serif !important;
    }
    .major-issue {
        background-color: #ffebee;
        color: #c62828;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8em;
        margin-right: 5px;
    }
    div[data-testid="stHorizontalBlock"] > div {
        text-align: center;
    }
    /* Mobile Optimization */
    @media only screen and (max-width: 600px) {
        .stButton button {
            width: 100% !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 auto !important;
            min-width: 0px !important;
        }
        /* Title Adjustment for Mobile */
        .title-container h2 {
            font-size: 1.5rem !important;
        }
        /* Reduce Padding on Mobile */
        .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* Desktop Padding */
    @media only screen and (min-width: 601px) {
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 5rem !important;
            max-width: 1200px !important; /* Center content on wide screens */
        }
    }
    
    /* Compact Metrics (Global) */
    div[data-testid="metric-container"] {
        padding: 4px 8px !important;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background-color: #f9f9f9;
        margin-bottom: 8px !important;
    }
    
    /* Scroll to Top Button */
    .scroll-top-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: transform 0.2s, box-shadow 0.2s;
        text-decoration: none;
    }
    .scroll-top-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)

import simple_summarizer
import llm_summarizer

CURRENT_YEAR = str(datetime.now().year)

# 1. Clean Title (Responsive)
st.markdown("""
    <style>
        .title-container {
            margin-top: 10px !important;
            margin-bottom: 20px !important; 
            text-align: center;
        }
        @media only screen and (min-width: 601px) {
             .title-container {
                margin-top: 30px !important;
             }
        }
    </style>
    <div class="title-container">
        <h2>🏦 캐피탈사 채용 대비 Dashboard</h2>
    </div>
""", unsafe_allow_html=True)


# ... (Market Data)


# ... (Tabs)
with st.container():
    st.markdown("### 🌏 실시간 시장 지표 (Market Indicators)")
    
    if 'selected_market_ticker' not in st.session_state:
        st.session_state['selected_market_ticker'] = "KOSPI" 
        
    market_data = market_data_fetcher.get_market_data()
    
    if market_data:
        metrics = [
            ("KOSPI", "KOSPI"), ("KOSDAQ", "KOSDAQ"), ("USD/KRW", "USD/KRW"), 
            ("JPY/KRW", "JPY/KRW"), ("미국채 10년", "US 10Y Bond"), 
            ("나스닥", "NASDAQ"), ("니케이", "Nikkei 225"),
            ("금", "Gold"), ("은", "Silver"), ("구리", "Copper")
        ]
        
        # Responsive Grid: Split into rows of 3
        # On Desktop: 3x3 grid (cleaner than 9 in a row)
        # On Mobile: Stacks naturally
        rows = [metrics[i:i + 3] for i in range(0, len(metrics), 3)]
        
        for row in rows:
            cols = st.columns(3)
            for i, (label, key) in enumerate(row):
                 if key in market_data:
                    item = market_data[key]
                    # Color the main price value: red for +, blue for -
                    price_color = "#e53935" if item['color'] == "red" else "#1976d2" if item['color'] == "blue" else "#333333"
                    change_color = "#e53935" if item['color'] == "red" else "#1976d2" if item['color'] == "blue" else "#666666"
                    
                    cols[i].markdown(f"""
                        <div style="text-align: center; padding: 8px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa;">
                            <div style="font-size: 14px; color: #666; margin-bottom: 4px;">{label}</div>
                            <div style="font-size: 20px; font-weight: bold; color: {price_color};">{item['price']}</div>
                            <div style="font-size: 13px; color: {change_color};">{item['change']}</div>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("시장 데이터를 불러오는 중 오류가 발생했습니다.")
        
    st.markdown("---")
    
    # Chart Selection UI
    st.write("📉 **5년간 시세 변화 추이 (클릭하여 선택)**")
    chart_options = [m[0] for m in metrics]
    selection = st.radio("지표 선택", chart_options, horizontal=True, label_visibility="collapsed")
    
    if selection and market_data:
        selected_key = next((k for l, k in metrics if l == selection), None)
        if selected_key and selected_key in market_data:
            symbol = market_data[selected_key]['symbol']
            
            with st.spinner(f"{selection} 과거 데이터 로딩 중..."):
                hist_data = market_data_fetcher.get_historical_data(symbol)
            
            if not hist_data.empty:
                df_chart = hist_data.reset_index()
                df_chart.columns = ['Date', 'Price']
                
                c = alt.Chart(df_chart).mark_line(color='#ff2b2b', strokeWidth=2).encode(
                    x=alt.X('Date', axis=alt.Axis(format='%Y-%m', title='날짜')),
                    y=alt.Y('Price', scale=alt.Scale(zero=False), title='가격'),
                    tooltip=['Date', 'Price']
                ).properties(height=300).interactive()
                
                st.altair_chart(c, use_container_width=True)
            else:
                st.warning("차트 데이터를 불러올 수 없습니다.")

    st.markdown("---")

# 3. Sidebar Configuration (Removed as per user request)
# st.sidebar.title("설정 (Configuration)")
# st.sidebar.slider("검색 기간 (일)", 1, 30, 3) 
st.sidebar.markdown("---")
st.sidebar.header("NotebookLM 바로가기")
st.sidebar.markdown("[📘 NotebookLM 열기](https://notebooklm.google.com/)")

def auto_update_news():
    from concurrent.futures import ThreadPoolExecutor, as_completed

    st.toast("⏳ 최신 뉴스를 병렬 수집 중입니다...")
    days_lookback = 3
    new_data = {}

    def fetch_ibk():
        raw = news_fetcher.fetch_news("IBK Capital", days=days_lookback, max_items=20)
        rep = news_fetcher.fetch_business_reports("IBK캐피탈")
        return 'IBK', deduplicator.deduplicate_news(raw + rep)

    def fetch_ibk_parent():
        raw = news_fetcher.fetch_news("IBK Parent", days=days_lookback, max_items=20)
        rep = news_fetcher.fetch_business_reports("IBK기업은행")
        return 'IBK_Parent', deduplicator.deduplicate_news(raw + rep)

    def fetch_kdb():
        raw = news_fetcher.fetch_news("KDB Capital", days=days_lookback, max_items=20)
        rep = news_fetcher.fetch_business_reports("산은캐피탈")
        return 'KDB', deduplicator.deduplicate_news(raw + rep)

    def fetch_kdb_parent():
        raw = news_fetcher.fetch_news("KDB Parent", days=days_lookback, max_items=20)
        rep = news_fetcher.fetch_business_reports("KDB산업은행")
        return 'KDB_Parent', deduplicator.deduplicate_news(raw + rep)

    def fetch_industry():
        items = news_fetcher.fetch_news("Capital Industry", days=days_lookback, max_items=10)
        return 'Capital Industry', items

    def fetch_macro():
        items = news_fetcher.fetch_news("Macro Economy", days=days_lookback, max_items=10)
        return 'Macro Economy', items

    tasks = [fetch_ibk, fetch_ibk_parent, fetch_kdb, fetch_kdb_parent,
             fetch_industry, fetch_macro]

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(task): task.__name__ for task in tasks}
        for future in as_completed(futures):
            try:
                key, items = future.result()
                new_data[key] = items
            except Exception as e:
                st.toast(f"⚠️ {futures[future]} 수집 실패: {e}")

    # Merge with existing archive
    for key, items in new_data.items():
        if key in st.session_state['news_data']:
            combined = items + st.session_state['news_data'][key]
            st.session_state['news_data'][key] = deduplicator.deduplicate_news(combined)
        else:
            st.session_state['news_data'][key] = items

    st.session_state['news_data']['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    news_storage.save_news_history(st.session_state['news_data'])
    st.toast("✅ 통합 뉴스 업데이트 완료!")

# Session State Init with Persistence
if 'news_data' not in st.session_state:
    loaded_data = news_storage.load_news_history()
    if loaded_data:
        st.session_state['news_data'] = loaded_data
        
        # Auto-Update Logic
        last_updated_str = loaded_data.get('_last_updated', '2000-01-01 00:00:00')
        try:
            last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d %H:%M:%S")
            if last_updated.date() < datetime.now().date():
                 with st.spinner("🔄 최신 뉴스 업데이트 중..."):
                     try:
                         auto_update_news()
                     except Exception as e:
                         st.error(f"뉴스 업데이트 실패: {e}")
        except (ValueError, TypeError):
            pass
    else:
        st.session_state['news_data'] = {}

# 채용공고 자동 크롤링 (하루 1회)
if 'recruitment_checked' not in st.session_state:
    try:
        recruitment_result = recruitment_fetcher.check_for_new_recruitment()
        new_found = recruitment_result.get('_new_found', 0)
        if new_found > 0:
            st.toast(f"🔔 새로운 채용공고 {new_found}건 발견!")
        st.session_state['recruitment_checked'] = True
    except Exception:
        st.session_state['recruitment_checked'] = True

# Sidebar: Data Info
if '_last_updated' in st.session_state.get('news_data', {}):
    st.sidebar.info(f"📅 데이터 기준:\n{st.session_state['news_data']['_last_updated']}")
else:
    st.sidebar.warning("데이터가 없습니다.\n관리자에게 문의하세요.")

# Claude API Status
if llm_summarizer.is_available():
    st.sidebar.success("🤖 Claude API: 활성")
else:
    st.sidebar.caption("💡 Claude API: 비활성 (규칙 기반 요약)")

# if st.sidebar.button("🗑️ 뉴스 기록 초기화"):
#     st.session_state['news_data'] = {}
#     news_storage.save_news_history({})
#     st.experimental_rerun()

def display_company_info(company_name, key):
    data = company_data.company_info.get(company_name)
    if not data:
        st.error(f"{company_name} 정보를 찾을 수 없습니다.")
        return

    st.header(f"🏢 {company_name} 기업 개요")
    st.subheader(f"🔑 {company_name} 2026 경영 전략 (Key Issues)")
    
    # Use Curated Data (Business Plan Based)
    if company_name in company_data.key_issues_curated:
        issues = company_data.key_issues_curated[company_name]
        for i, news in enumerate(issues):
            with st.expander(f"📌 {news['title']}", expanded=(i==0)):
                st.write(news.get('summary', ''))
                if news.get('link'):
                    st.caption(f"[관련 링크]({news['link']})")
    
    # Fallback to session state if needed (or remove)
    elif f'{key}_issues' in st.session_state:
        issues = st.session_state[f'{key}_issues']
        for i, news in enumerate(issues):
            with st.expander(f"🔥 {news['title']}", expanded=(i==0)):
                st.write(news.get('summary', ''))
                
    st.markdown("---")
    st.subheader("💼 주요 사업 (Business Areas)")
    for biz in data['business']:
        with st.expander(f"{biz['name']} ({biz['scale']})"):
            st.write(f"**개요**: {biz['desc']}")
            st.markdown("**상세 내용**:")
            if 'details' in biz:
                for detail in biz['details']:
                    st.markdown(f"- {detail}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 주요 재무 (Financials)")
        fin = data['financials']
        metric_names = {
            "Assets": "자산", "Net Income": "당기순이익", "Revenue": "매출",
            "ROE": "자기자본이익률(ROE)", "Delinquency Rate": "연체율",
            "NPL Ratio": "고정이하여신비율(NPL)"
        }
        for year, stats in fin.items():
            st.markdown(f"**{year}**")
            for metric_key, value in stats.items():
                if value and value != "N/A":
                    label = metric_names.get(metric_key, metric_key)
                    st.write(f"- {label}: {value}")
    
    with col2:
         st.subheader("📜 주요 연혁 (History)")
         for event in data['history'][-5:]:
            year_text = event['year']
            if CURRENT_YEAR in year_text:
                st.markdown(f"🔴 **{year_text}**: {event['event']}")
            else:
                st.markdown(f"**{year_text}**: {event['event']}")

    st.markdown("---")
    st.subheader("🧑‍🤝‍🧑 채용 정보 (Recruitment)")
    recruitment_values = data.get('recruitment_values')
    recruitment_link = data.get('recruitment_link')

    if recruitment_values:
        st.info(f"💡 **핵심 가치**: {', '.join(recruitment_values)}")

    # 자동수집 + 하드코딩 통합 채용 데이터
    recruit_key = "IBK" if "IBK" in company_name else "KDB"
    all_recruitment = recruitment_fetcher.get_all_recruitment_info(recruit_key)

    if all_recruitment:
        # 자동수집 최신 공고 (있으면 우선 표시)
        auto_items = [r for r in all_recruitment if r.get('is_auto')]
        static_items = [r for r in all_recruitment if not r.get('is_auto')]

        if auto_items:
            st.success(f"🔔 **실시간 채용공고 {len(auto_items)}건 발견!**")
            for rec in auto_items:
                with st.expander(f"🔔 {rec['title']}", expanded=True):
                    st.write(f"**게시일**: {rec['period']}")
                    if rec.get('deadline'):
                        st.write(f"**마감**: {rec['deadline']}")
                    if rec.get('note'):
                        st.write(f"**상세**: {rec['note']}")
                    if rec.get('link'):
                        st.markdown(f"👉 [공고 바로가기]({rec['link']})")

        # 기존 하드코딩 채용 데이터
        if static_items:
            if auto_items:
                st.markdown("#### 📋 과거 채용 이력")
            for rec in static_items:
                title = rec['title']
                if CURRENT_YEAR in title:
                    title = f"🔴 {title}"
                with st.expander(f"{title} ({rec['period']})"):
                    if rec.get('roles'):
                        st.write(f"**분야**: {', '.join(rec['roles'])}")
                    if rec.get('scale'):
                        st.write(f"**규모**: {rec['scale']}")
                    if rec.get('note'):
                        st.write(f"**Note**: {rec['note']}")
                    if rec.get('link'):
                        st.markdown(f"👉 [공고 상세 보기]({rec['link']})")

    if recruitment_link:
        st.markdown(f"👉 [채용 홈페이지 바로가기]({recruitment_link})")

    # Case Studies Section
    st.markdown("---")
    st.subheader("📋 주요 사업 사례 (Case Studies)")

    cases = company_data.case_studies.get(company_name, {})

    if cases.get("success"):
        st.markdown("#### ✅ 성공 사례")
        for case in cases["success"]:
            with st.expander(f"✅ {case['title']} [{case['category']}]"):
                st.write(f"**기간**: {case['period']}")
                st.write(f"**개요**: {case['summary']}")
                st.markdown("**상세**:")
                for d in case['details']:
                    st.markdown(f"- {d}")
                st.info(f"**시사점**: {case['lesson']}")

    if cases.get("failure"):
        st.markdown("#### ⚠️ 실패/교훈 사례")
        for case in cases["failure"]:
            with st.expander(f"⚠️ {case['title']} [{case['category']}]"):
                st.write(f"**기간**: {case['period']}")
                st.write(f"**개요**: {case['summary']}")
                st.markdown("**상세**:")
                for d in case['details']:
                    st.markdown(f"- {d}")
                st.warning(f"**교훈**: {case['lesson']}")

# Main Layout
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["기업 개요", "IBK캐피탈 뉴스", "산은캐피탈 뉴스", "캐피탈 업황", "거시경제", "IBK기업은행", "KDB산업은행"])

with tab1:
     col_info1, col_info2 = st.columns(2)
     with col_info1:
         display_company_info("IBK Capital", "ibk_info")
     with col_info2:
         display_company_info("KDB Capital", "kdb_info")

def display_archive(company_key, title, filter_mode="all"):
    st.header(f"🗄️ {title}")
    
    if 'news_data' not in st.session_state:
        st.warning("데이터가 없습니다.")
        return

    # specific logic for Group News Tab
    if company_key == "GROUP":
        # Aggregate IBK and KDB news, then filter for NON-Capital
        # Now using Explicit Parent Keys
        all_news = st.session_state['news_data'].get('IBK_Parent', []) + st.session_state['news_data'].get('KDB_Parent', [])
    else:
        all_news = st.session_state['news_data'].get(company_key, [])
    
    if not all_news:
         st.info("뉴스 데이터가 없습니다.")
         return

    # Keyword Search
    search_query = st.text_input(
        "🔍 키워드 검색 (제목 + 본문)",
        placeholder="예: PF, 금리, 실적, 인수합병...",
        key=f"search_{company_key}"
    )

    # Date Filtering
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
         selected_year = st.selectbox(f"{title} 연도 Archive", ["All", 2026, 2025, 2024, 2023, 2022, 2021, 2020], key=f"year_{company_key}")
    with col_filter2:
         selected_month = st.selectbox(f"월(Month) 선택", ["All"] + list(range(1, 13)), key=f"month_{company_key}")

    # Use FTS5 search if query is provided
    if search_query and search_query.strip():
        try:
            fts_results = news_storage.search_news(search_query.strip(), company_key=company_key if company_key != "GROUP" else None, limit=200)
            # Apply year/month filter on FTS results
            filtered_news = []
            for item in fts_results:
                try:
                    pub_dt = parser.parse(item['published'])
                    if selected_year != "All" and pub_dt.year != selected_year:
                        continue
                    if selected_month != "All" and pub_dt.month != selected_month:
                        continue
                    filtered_news.append(item)
                except (ValueError, TypeError):
                    continue
        except Exception:
            # Fallback to in-memory search if FTS fails
            filtered_news = []
            for item in all_news:
                try:
                    content_text = (item.get('title', '') + ' ' + item.get('full_content', '') + ' ' + item.get('summary', '')).lower()
                    if search_query.strip().lower() not in content_text:
                        continue
                    pub_dt = parser.parse(item['published'])
                    if selected_year != "All" and pub_dt.year != selected_year:
                        continue
                    if selected_month != "All" and pub_dt.month != selected_month:
                        continue
                    filtered_news.append(item)
                except (ValueError, TypeError):
                    continue
    else:
        filtered_news = []
        for item in all_news:
            try:
                pub_dt = parser.parse(item['published'])
                if selected_year != "All" and pub_dt.year != selected_year:
                    continue
                if selected_month != "All" and pub_dt.month != selected_month:
                    continue

                content_check = (item['title'] + item.get('summary', '')).replace(" ", "")

                if filter_mode == "capital_only":
                    if "캐피탈" not in content_check and "Capital" not in item.get('title', ''):
                        continue
                elif filter_mode == "group_only":
                    if "IBK캐피탈" in content_check or "산은캐피탈" in content_check:
                        continue
                elif filter_mode == "parent_only":
                    if "캐피탈" in content_check or "Capital" in item.get('title', ''):
                        continue

                filtered_news.append(item)
            except (ValueError, TypeError):
                continue

            
    # Sort by Date (Newest First)
    filtered_news.sort(key=lambda x: parser.parse(x.get('published', '2000-01-01')), reverse=True)
            
    st.info(f"📚 선택된 기간의 아카이브: {len(filtered_news)}건")
    
    # Separate Business Reports from General News
    business_reports = []
    general_news = []
    
    report_keywords = ["[공시", "[보고서", "사업보고서", "경영공시", "감사보고서", "실적발표"]
    
    for item in filtered_news:
        title_item = item.get('title', '')
        if any(k in title_item for k in report_keywords):
            business_reports.append(item)
        else:
            general_news.append(item)
            
    # Display Business Reports Section (if any)
    if business_reports:
        st.markdown(f"### 📑 {title.split(' ')[0]} 주요 사업보고서 및 공시")
        for i, news in enumerate(business_reports):
            # Report Style Display (Simpler, more formal)
            with st.expander(f"📄 {news['title']}", expanded=True):
                 st.caption(f"📅 공시일: {news.get('published', '')[:10]}")
                 if news.get('link'):
                    st.markdown(f"👉 [원문 확인]({news['link']})")
                 st.write(news.get('summary', ''))
        st.markdown("---")
        st.markdown("### 📰 뉴스 아카이브")
        # Update filtered_news to only show general news below
        filtered_news = general_news

    if st.button(f"📊 {selected_year}년 {selected_month}월 AI 핵심 리포트 생성", key=f"analyze_{company_key}"):
         if filtered_news or business_reports:
             if llm_summarizer.is_available():
                 spinner_msg = "🤖 Claude AI가 심층 분석 보고서를 작성 중입니다... (약 15초 소요)"
             else:
                 spinner_msg = "📊 분석 보고서를 생성 중입니다... (약 3초 소요)"
             with st.spinner(spinner_msg):
                 target_comp = "IBK캐피탈" if company_key == "IBK" else "산은캐피탈" if company_key == "KDB" else "캐피탈 업계"
                 report = llm_summarizer.generate_synthesis_report(filtered_news + business_reports, title=f"{title} - {selected_year}년 {selected_month}월 종합 분석", company_name=target_comp)
                 
                 with st.expander("📄 생성된 AI 리포트 보기", expanded=True):
                    st.markdown(report)
                 
                 # Feature for NotebookLM manual usage
                 with st.expander("📋 NotebookLM 업로드용 소스 텍스트 복사 (Copy Source)"):
                     st.info("아래 텍스트를 복사하여 Google NotebookLM에 '소스 추가' 하시면 더 정교한 질의응답이 가능합니다.")
                     source_text = ""
                     for item in business_reports + filtered_news:
                         source_text += f"[{item.get('published','')[:10]}] {item.get('title')}\n{item.get('full_content')}\n\n"
                     st.text_area("Whole Text Source", source_text, height=200)

         else:
             st.warning("분석할 뉴스가 없습니다.")

    st.markdown("---")
    
    for i, news in enumerate(filtered_news):
        # 1. Robust Date Parsing
        try:
            dt_obj = parser.parse(news.get('published', str(datetime.now())))
            date_label = dt_obj.strftime("%Y-%m-%d") # YYYY-MM-DD
            day_kor = ["월", "화", "수", "목", "금", "토", "일"][dt_obj.weekday()]
            full_date_str = f"{dt_obj.strftime('%Y년 %m월 %d일')} ({day_kor})"
        except (ValueError, TypeError):
            date_label = "날짜 미상"
            full_date_str = news.get("published", "")

        # 2. Expander Title: [YYYY-MM-DD] Title (highlight search match)
        display_title = news['title']
        if search_query and search_query.strip():
            display_title = display_title.replace(search_query.strip(), f"**{search_query.strip()}**")
        with st.expander(f"[{date_label}] {display_title}"):
             st.caption(f"📅 게시일: {full_date_str}")
             
             # Real Summarization
             full_text = news.get('full_content', '')
             if not full_text:
                 full_text = news.get('summary', '내용 없음')

             # Map company_key to Korean name for focus
             focus_map = {"IBK": "IBK캐피탈", "KDB": "산은캐피탈", "IBK_Parent": "IBK기업은행", "KDB_Parent": "KDB산업은행", "Capital Industry": None, "Macro Economy": None}
             focus_kw = focus_map.get(company_key)

             # Cache summaries in session_state to avoid re-calling API
             cache_key = f"summary_{hash(full_text[:200])}_{focus_kw}"
             if cache_key in st.session_state:
                 summary_text = st.session_state[cache_key]
             else:
                 summary_text = llm_summarizer.summarize(full_text, num_sentences=4, focus_keyword=focus_kw)
                 st.session_state[cache_key] = summary_text

             if llm_summarizer.is_available():
                 st.info(f"🤖 **Claude AI 요약**: {summary_text}")
             else:
                 st.info(f"💡 **AI 요약**: {summary_text}")
             
             if news.get('link'):
                st.markdown(f"👉 [📰 기사 원문 링크 바로가기]({news['link']})")
            
             st.text_area("📜 뉴스 원문 전체 (Original Text)", full_text, height=400, key=f"orig_{company_key}_{i}")

with tab2:
    display_archive('IBK', 'IBK캐피탈 뉴스 아카이브', filter_mode="capital_only")
with tab3:
    display_archive('KDB', '산은캐피탈 뉴스 아카이브', filter_mode="capital_only")
with tab4:
    display_archive('Capital Industry', '캐피탈 업황 아카이브')
with tab5:
    display_archive('Macro Economy', '거시경제 아카이브')
with tab6:
    display_archive('IBK Parent', 'IBK기업은행 뉴스 아카이브', filter_mode="parent_only")
with tab7:
    display_archive('KDB Parent', 'KDB산업은행 뉴스 아카이브', filter_mode="parent_only")

# Scroll to Top Button (Fixed Position with JS)
st.markdown("""
    <style>
        .scroll-top-btn {
            position: fixed !important;
            bottom: 30px;
            right: 30px;
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none !important;
        }
        .scroll-top-btn:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.7);
        }
    </style>
    <div class="scroll-top-btn" onclick="window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});">
        ↑
    </div>
    <script>
        // Alternative scroll method for Streamlit iframe
        document.querySelector('.scroll-top-btn').addEventListener('click', function() {
            var main = window.parent.document.querySelector('section.main');
            if (main) {
                main.scrollTo({top: 0, behavior: 'smooth'});
            } else {
                window.scrollTo({top: 0, behavior: 'smooth'});
            }
        });
    </script>
""", unsafe_allow_html=True)
