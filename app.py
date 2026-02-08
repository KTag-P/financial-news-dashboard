import streamlit as st
import news_fetcher
import deduplicator
import report_generator
import company_data
import market_data_fetcher
import socket

st.set_page_config(page_title="금융 뉴스 대시보드", layout="wide")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Sidebar
st.sidebar.title("설정 (Configuration)")
days_lookback = st.sidebar.slider("검색 기간 (일)", 1, 7, 3) # Default changed to 3 for more news

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
</style>
""", unsafe_allow_html=True)

st.title("🏦 캐피탈사 채용 대비 (화면: Bright Mode)")

# Market Data Widget
with st.container():
    st.markdown("### 🌏 실시간 시장 지표 (Market Indicators)")
    market_data = market_data_fetcher.get_market_data()
    
    if market_data:
        cols = st.columns(6)
        metrics = [
            ("KOSPI", "KOSPI"), ("USD/KRW", "USD/KRW"), 
            ("국고채 10년", "US 10Y Bond"), # US 10Y as proxy or label simply 'Gold' etc
            ("금 (Gold)", "Gold"), ("은 (Silver)", "Silver"), ("구리 (Copper)", "Copper")
        ]
        
        for i, (label, key) in enumerate(metrics):
            if key in market_data:
                item = market_data[key]
                cols[i].metric(label, item['price'], item['change'])
    else:
        st.warning("시장 데이터를 불러오는 중 오류가 발생했습니다.")
    st.markdown("---")

# Session State Init
if 'news_data' not in st.session_state:
    st.session_state['news_data'] = {}

if st.sidebar.button("뉴스 가져오기 (Fetch News)"):
    with st.spinner("뉴스를 가져오는 중입니다... (내용 분석에 시간이 소요될 수 있습니다)"):
        # Fetch IBK
        raw_ibk = news_fetcher.fetch_news("IBK Capital", days=days_lookback)
        st.session_state['news_data']['IBK'] = deduplicator.deduplicate_news(raw_ibk)
        
        # Fetch KDB
        raw_kdb = news_fetcher.fetch_news("KDB Capital", days=days_lookback)
        st.session_state['news_data']['KDB'] = deduplicator.deduplicate_news(raw_kdb)
        
        # Fetch Industry
        raw_ind = news_fetcher.fetch_news("Capital Industry", days=days_lookback)
        st.session_state['news_data']['Capital Industry'] = deduplicator.deduplicate_news(raw_ind)
        
        # Fetch Macro
        raw_mac = news_fetcher.fetch_news("Macro Economy", days=days_lookback)
        st.session_state['news_data']['Macro Economy'] = deduplicator.deduplicate_news(raw_mac)
        
        st.success(f"완료! IBK: {len(st.session_state['news_data']['IBK'])}건, 산은: {len(st.session_state['news_data']['KDB'])}건, 업황: {len(st.session_state['news_data']['Capital Industry'])}건, 경제: {len(st.session_state['news_data']['Macro Economy'])}건")

def display_company_info(company_name, key):
    # (Function body assumes unchanged, but need to ensure it's not duplicated/broken by previous edits)
    # Re-declaring here to be safe if previous replace messed up 
    data = company_data.company_info.get(company_name)
    if not data:
        st.error(f"{company_name} 정보를 찾을 수 없습니다.")
        return

    st.header(f"🏢 {company_name} 기업 개요")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 주요 재무 (Financials)")
        fin = data['financials']
        for year, stats in fin.items():
            st.markdown(f"**{year}년**")
            st.write(f"- 자산: {stats['Assets']}")
            st.write(f"- 당기순이익: {stats['Net Income']}")
            if stats.get("Revenue") != "N/A":
                st.write(f"- 매출(영업수익): {stats['Revenue']}")

    with col2:
        st.subheader("💼 주요 사업 (Business Areas)")
        for biz in data['business']:
            with st.expander(biz['name']):
                st.write(f"**규모**: {biz['scale']}")
                st.write(f"**상세**: {biz['desc']}")
            
    st.markdown("---")
    st.subheader("🧑‍🤝‍🧑 채용 정보 (Recruitment)")
    recruitment_list = data.get('recruitment')
    recruitment_values = data.get('recruitment_values')
    recruitment_link = data.get('recruitment_link')

    if recruitment_list:
        st.info(f"💡 **인재상 & 핵심가치**: {', '.join(recruitment_values)}")
        
        st.markdown("##### 📅 최근 채용 이력 (2024-2025)")
        for rec in recruitment_list:
            with st.expander(f"{rec['title']} ({rec['period']})"):
                st.write(f"**모집 분야**: {', '.join(rec['roles'])}")
                if rec.get('note'):
                    st.write(f"**특이사항**: {rec['note']}")
        
        st.markdown(f"👉 [채용 홈페이지 바로가기]({recruitment_link})")
    else:
        st.write("채용 정보가 없습니다.")

    st.markdown("---")
    st.subheader("📜 주요 연혁 및 이슈 (2020-2025)")
    
    for event in data['history']:
        st.markdown(f"**{event['year']}**")
        st.write(f"  └ {event['event']}")

def display_news_tab(company_name, news_items, key_prefix):
    st.header(f"📰 {company_name} 뉴스 ({len(news_items)}건)")
    
    major_keywords = ['실적', '최대', '순이익', '배당', 'CEO', '대표', '인수', '합병', 'M&A', '발행']
    
    # 1. Daily Summary
    if news_items:
        with st.container():
            st.info(f"📢 **오늘의 주요 헤드라인 (Top 5)**")
            for i, item in enumerate(news_items[:5]):
                title = item['title']
                published = item.get('published', '')[:10] 
                st.write(f"{i+1}. {title} ({published})")
            
            if st.button(f"📄 {company_name} 요약 보고서 생성", key=f"{key_prefix}_btn"):
                report = report_generator.generate_markdown_report(news_items, title=f"{company_name} 일일 요약 보고서")
                with st.expander("📄 보고서 보기 (클릭하여 펼치기)", expanded=True):
                    st.markdown(report) 

    st.markdown("---")

    # 2. News List
    for i, news in enumerate(news_items):
        title = news['title']
        is_major = any(k in title for k in major_keywords)
        
        display_title = title
        if is_major:
            display_title = f"🔥 {title}"
            
        with st.expander(display_title):
            if is_major:
                st.markdown('<span class="major-issue">Major Issue</span>', unsafe_allow_html=True)

            if news.get('image'):
                st.image(news['image'], use_container_width=True)
                
            st.write(f"**출처**: {news.get('link', '')}")
            st.write(f"**발행일**: {news.get('published', 'N/A')}")
            
            content = news.get('summary', '')
            if content:
                st.markdown(content)
            else:
                st.warning("내용을 가져오지 못했습니다.")
            
            original = news.get('original_link') or news['link']
            st.markdown(f"[🔗 원문 보러가기]({original})")

# Main Layout
tab1, tab2, tab3, tab4 = st.tabs(["IBK캐피탈", "산은캐피탈", "캐피탈 업황", "거시경제 (Macro)"])

with tab1:
    display_company_info("IBK Capital", "ibk_info")
    st.markdown("---")
    if 'news_data' in st.session_state and 'IBK' in st.session_state['news_data']:
        display_news_tab("IBK Capital", st.session_state['news_data']['IBK'], "ibk")
    else:
        st.info("왼쪽 사이드바에서 '뉴스 가져오기' 버튼을 눌러주세요.")

with tab2:
    display_company_info("KDB Capital", "kdb_info")
    st.markdown("---")
    if 'news_data' in st.session_state and 'KDB' in st.session_state['news_data']:
        display_news_tab("KDB Capital", st.session_state['news_data']['KDB'], "kdb")
    else:
        st.info("왼쪽 사이드바에서 '뉴스 가져오기' 버튼을 눌러주세요.")
        
with tab3:
    st.info("📊 **캐피탈 산업 전반의 주요 이슈 (PF, 채권, 규제 등)**")
    if 'news_data' in st.session_state and 'Capital Industry' in st.session_state['news_data']:
        display_news_tab("Capital Industry", st.session_state['news_data']['Capital Industry'], "industry")
    else:
        st.info("왼쪽 사이드바에서 '뉴스 가져오기' 버튼을 눌러주세요.")
        
with tab4:
    st.info("🌍 **환율, 금리, 유가 등 거시경제 동향**")
    if 'news_data' in st.session_state and 'Macro Economy' in st.session_state['news_data']:
        display_news_tab("Macro Economy", st.session_state['news_data']['Macro Economy'], "macro")
    else:
        st.info("왼쪽 사이드바에서 '뉴스 가져오기' 버튼을 눌러주세요.")

st.sidebar.markdown("---")
st.sidebar.header("NotebookLM 활용")
st.sidebar.write("1. 생성된 보고서를 복사하세요.")
st.sidebar.write("2. NotebookLM에 '소스'로 추가하세요.")
st.sidebar.write("3. AI에게 질문하거나 오디오 개요를 들어보세요!")

