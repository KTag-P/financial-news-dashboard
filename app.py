import streamlit as st
import news_fetcher
import deduplicator
import report_generator
import company_data
import market_data_fetcher
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
    except:
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
</style>
""", unsafe_allow_html=True)

import simple_summarizer

# ... (imports)

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


def display_archive(company_key, title, filter_mode="all"):
    # ... (Headings)
    
    # ... (Filters)
    
    # ... (Sort)
    
    for i, news in enumerate(filtered_news):
        # 1. Robust Date Parsing
        try:
            dt_obj = parser.parse(news.get('published', str(datetime.now())))
            date_label = dt_obj.strftime("%Y-%m-%d") # YYYY-MM-DD
            day_kor = ["월", "화", "수", "목", "금", "토", "일"][dt_obj.weekday()]
            full_date_str = f"{dt_obj.strftime('%Y년 %m월 %d일')} ({day_kor})"
        except:
            date_label = "날짜 미상"
            full_date_str = news.get('published', '')

        # 2. Expander Title: [YYYY-MM-DD] Title
        with st.expander(f"[{date_label}] {news['title']}"):
             st.caption(f"📅 게시일: {full_date_str}")
             
             # Real Summarization
             full_text = news.get('full_content', '')
             if not full_text:
                 full_text = news.get('summary', '내용 없음')

             # Pass to summarizer
             summary_text = simple_summarizer.summarize_korean(full_text, num_sentences=4)
             
             st.info(f"💡 **AI 요약**: {summary_text}")
             
             if news.get('link'):
                st.markdown(f"👉 [📰 기사 원문 링크 바로가기]({news['link']})")
            
             st.text_area("📜 뉴스 원문 전체 (Original Text)", full_text, height=400, key=f"orig_{company_key}_{i}")

# ... (Tabs)
with st.container():
    st.markdown("### 🌏 실시간 시장 지표 (Market Indicators)")
    
    if 'selected_market_ticker' not in st.session_state:
        st.session_state['selected_market_ticker'] = "KOSPI" 
        
    market_data = market_data_fetcher.get_market_data()
    
    if market_data:
        metrics = [
            ("KOSPI", "KOSPI"), ("KOSDAQ", "KOSDAQ"), ("USD/KRW", "USD/KRW"), 
            ("미국채 10년", "US 10Y Bond"), 
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
                    cols[i].metric(label, item['price'], item['change'])
    else:
        st.warning("시장 데이터를 불러오는 중 오류가 발생했습니다.")
        
    st.markdown("---")
    
    # Chart Selection UI
    st.write("📉 **1년간 시세 변화 추이 (클릭하여 선택)**")
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
# days_lookback = st.sidebar.slider("검색 기간 (일)", 1, 30, 3) 
st.sidebar.markdown("---")
st.sidebar.header("NotebookLM 바로가기")
st.sidebar.markdown("[📘 NotebookLM 열기](https://notebooklm.google.com/)")

def auto_update_news():
    st.toast("⏳ 최신 뉴스를 업데이트 중입니다... 잠시만 기다려주세요.")
    days_lookback = 2 
    new_data = {}
    
    # IBK
    raw_ibk = news_fetcher.fetch_news("IBK Capital", days=days_lookback, max_items=20)
    new_data['IBK'] = deduplicator.deduplicate_news(raw_ibk)
    
    # KDB
    raw_kdb = news_fetcher.fetch_news("KDB Capital", days=days_lookback, max_items=20)
    new_data['KDB'] = deduplicator.deduplicate_news(raw_kdb)
    
    # Industry
    new_data['Capital Industry'] = news_fetcher.fetch_news("Capital Industry", days=days_lookback, max_items=10)
    new_data['Macro Economy'] = news_fetcher.fetch_news("Macro Economy", days=days_lookback, max_items=10)
    
    # Merge
    for key, items in new_data.items():
        if key in st.session_state['news_data']:
             st.session_state['news_data'][key] = deduplicator.deduplicate_news(items + st.session_state['news_data'][key])
        else:
             st.session_state['news_data'][key] = items
             
    st.session_state['news_data']['_last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    news_storage.save_news_history(st.session_state['news_data'])
    st.toast("✅ 최신 뉴스 업데이트 완료!")

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
        except:
            pass
    else:
        st.session_state['news_data'] = {}

# Sidebar: Data Info
st.sidebar.markdown("### 🗄️ 데이터 상태")
if '_last_updated' in st.session_state.get('news_data', {}):
    st.sidebar.info(f"📅 데이터 기준:\n{st.session_state['news_data']['_last_updated']}")
else:
    st.sidebar.warning("데이터가 없습니다.\n관리자에게 문의하세요.")

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
        for year, stats in fin.items():
            st.markdown(f"**{year}**")
            st.write(f"- 자산: {stats['Assets']}")
            st.write(f"- 당기순이익: {stats['Net Income']}")
            if stats.get("Revenue") != "N/A":
                st.write(f"- 매출: {stats['Revenue']}")
    
    with col2:
         st.subheader("📜 주요 연혁 (History)")
         for event in data['history'][-5:]:
            year_text = event['year']
            if "2025" in year_text:
                st.markdown(f"🔴 **{year_text}**: {event['event']}")
            else:
                st.markdown(f"**{year_text}**: {event['event']}")

    st.markdown("---")
    st.subheader("🧑‍🤝‍🧑 채용 정보 (Recruitment)")
    recruitment_list = data.get('recruitment')
    recruitment_values = data.get('recruitment_values')
    recruitment_link = data.get('recruitment_link')

    if recruitment_list:
        st.info(f"💡 **핵심 가치**: {', '.join(recruitment_values)}")
        for rec in recruitment_list:
            title = rec['title']
            if "2025" in title:
                 title = f"🔴 {title}"
            with st.expander(f"{title} ({rec['period']})"):
                st.write(f"**분야**: {', '.join(rec['roles'])}")
                if rec.get('note'):
                    st.write(f"**Note**: {rec['note']}")
                if rec.get('link'):
                     st.markdown(f"👉 [공고 상세 보기]({rec['link']})")
        st.markdown(f"👉 [채용 홈페이지 바로가기]({recruitment_link})")

# Main Layout
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["기업 개요", "IBK캐피탈 뉴스", "산은캐피탈 뉴스", "캐피탈 업황", "거시경제", "모회사/그룹 뉴스"])

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
        all_news = st.session_state['news_data'].get('IBK', []) + st.session_state['news_data'].get('KDB', [])
    else:
        all_news = st.session_state['news_data'].get(company_key, [])
    
    if not all_news:
         st.info("뉴스 데이터가 없습니다.")
         return

    # Date Filtering
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
         selected_year = st.selectbox(f"{title} 연도 Archive", ["All", 2026, 2025, 2024, 2023, 2022, 2021], key=f"year_{company_key}")
    with col_filter2:
         selected_month = st.selectbox(f"월(Month) 선택", ["All"] + list(range(1, 13)), key=f"month_{company_key}")
    
    filtered_news = []
    for item in all_news:
        try:
            pub_dt = parser.parse(item['published'])
            # Year Filter
            if selected_year != "All" and pub_dt.year != selected_year:
                continue
            # Month Filter
            if selected_month != "All" and pub_dt.month != selected_month:
                continue
            
            # Special Keyword Filtering based on mode
            content_check = (item['title'] + item.get('summary', '')).replace(" ", "")
            
            if filter_mode == "capital_only":
                target_keyword = "캐피탈"
                if company_key == "KDB": target_keyword = "산은캐피탈"
                if company_key == "IBK": target_keyword = "IBK캐피탈"
                if target_keyword not in content_check and "캐피탈" not in content_check:
                    continue
            elif filter_mode == "group_only":
                # Exclude if it mentions Capital explicitly (since those are in Capital tabs)
                if "IBK캐피탈" in content_check or "산은캐피탈" in content_check:
                    continue
                    
            filtered_news.append(item)
        except:
            continue
            
    # Sort by Date (Newest First)
    filtered_news.sort(key=lambda x: parser.parse(x.get('published', '2000-01-01')), reverse=True)
            
    st.info(f"📚 선택된 기간의 아카이브: {len(filtered_news)}건")
    
    if st.button(f"📊 {selected_year}년 {selected_month}월 AI 핵심 리포트 생성", key=f"analyze_{company_key}"):
         if filtered_news:
             with st.spinner("AI가 해당 기간의 뉴스를 종합하여 심층 분석 보고서를 작성 중입니다... (약 10초 소요)"):
                 # Use Enhanced Report Generator
                 report = report_generator.generate_synthesis_report(filtered_news, title=f"{title} - {selected_year}년 {selected_month}월 종합 분석")
                 
                 with st.expander("📄 생성된 AI 리포트 보기", expanded=True):
                    st.markdown(report)
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
        except:
            date_label = "날짜 미상"
            full_date_str = news.get("published", "")

        # 2. Expander Title: [YYYY-MM-DD] Title
        with st.expander(f"[{date_label}] {news['title']}"):
             st.caption(f"📅 게시일: {full_date_str}")
             
             # Real Summarization
             full_text = news.get('full_content', '')
             if not full_text:
                 full_text = news.get('summary', '내용 없음')

             # Pass to summarizer
             summary_text = simple_summarizer.summarize_korean(full_text, num_sentences=4)
             
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
    display_archive('GROUP', '모회사/그룹(IBK/KDB) 뉴스 아카이브', filter_mode="group_only")
