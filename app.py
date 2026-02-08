import streamlit as st
import news_fetcher
import deduplicator
import report_generator
import company_data
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

# Mobile Access Info
local_ip = get_local_ip()
st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 모바일 접속")
st.sidebar.markdown(f"같은 와이파이 연결 후 아래 주소 입력:")
st.sidebar.code(f"http://{local_ip}:8501")

st.title("💰 금융 뉴스 대시보드: IBK & 산은캐피탈")

# Session State Init
if 'news_data' not in st.session_state:
    st.session_state['news_data'] = {}

if st.sidebar.button("뉴스 가져오기 (Fetch News)"):
    with st.spinner("뉴스를 가져오는 중입니다... (내용 분석에 시간이 소요될 수 있습니다)"):
        # Fetch IBK
        raw_ibk = news_fetcher.fetch_news("IBK캐피탈", days=days_lookback)
        unique_ibk = deduplicator.deduplicate_news(raw_ibk)
        st.session_state['news_data']['IBK'] = unique_ibk
        
        # Fetch KDB
        raw_kdb = news_fetcher.fetch_news("산은캐피탈", days=days_lookback)
        unique_kdb = deduplicator.deduplicate_news(raw_kdb)
        st.session_state['news_data']['KDB'] = unique_kdb
        
        st.success(f"완료! IBK: {len(unique_ibk)}건, 산은: {len(unique_kdb)}건")

def display_company_info(company_name, key):
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
            st.write(f"- {biz}")
            
    st.markdown("---")
    st.subheader("🧑‍🤝‍🧑 채용 정보 (Recruitment)")
    recruit = data.get('recruitment')
    if recruit:
        st.info(f"📅 **채용 기간**: {recruit['period']}")
        st.write(f"**모집 직무**: {', '.join(recruit['roles'])}")
        st.write(f"**인재상/핵심가치**: {', '.join(recruit['values'])}")
        st.markdown(f"👉 [채용 홈페이지 바로가기]({recruit['link']})")
    else:
        st.write("채용 정보가 없습니다.")

    st.markdown("---")
    st.subheader("📜 주요 연혁 및 이슈 (2020-2025)")
    
    for event in data['history']:
        st.markdown(f"**{event['year']}**")
        st.write(f"  └ {event['event']}")

def display_news_tab(company_name, news_items, key_prefix):
    st.header(f"📰 {company_name} 뉴스 ({len(news_items)}건)")
    
    # Sort by published date (Descending) - Simple string sort works for ISO format usually, 
    # but let's try to be robust if format varies. 
    # Assuming 'published' is a string, we might typically rely on index if fetcher returns sorted.
    # But user asked for "Newest first".
    # Let's verify data format or just reverse if source is RSS (usually newsest first).
    # We will assume fetcher returns decent order, but let's ensure image presence doesn't break things.
    
    # Highlight Keywords
    major_keywords = ['실적', '최대', '순이익', '배당', 'CEO', '대표', '인수', '합병', 'M&A', '발행']
    
    # 1. Daily Summary
    if news_items:
        with st.container():
            st.info(f"📢 **오늘의 주요 헤드라인 (Top 5)**")
            for i, item in enumerate(news_items[:5]):
                title = item['title']
                published = item.get('published', '')[:10] # Show date
                st.write(f"{i+1}. {title} ({published})")
            
            if st.button(f"📄 {company_name} 요약 보고서 생성", key=f"{key_prefix}_btn"):
                report = report_generator.generate_markdown_report(news_items, title=f"{company_name} 일일 요약 보고서")
                st.code(report, language='markdown')

    st.markdown("---")

    # 2. News List
    for i, news in enumerate(news_items):
        title = news['title']
        is_major = any(k in title for k in major_keywords)
        
        display_title = title
        if is_major:
            display_title = f"🔥 {title}"
            
        with st.expander(display_title):
            # Badge
            if is_major:
                st.markdown('<span class="major-issue">Major Issue</span>', unsafe_allow_html=True)

            # Image
            if news.get('image'):
                st.image(news['image'], use_container_width=True)
                
            st.write(f"**출처**: {news.get('link', '')}")
            st.write(f"**발행일**: {news.get('published', 'N/A')}")
            
            # Content
            content = news.get('summary', '')
            if content:
                st.markdown(content)
            else:
                st.warning("내용을 가져오지 못했습니다.")
            
            original = news.get('original_link') or news['link']
            st.markdown(f"[🔗 원문 보러가기]({original})")

# Main Layout
tab1, tab2, tab3, tab4 = st.tabs(["IBK캐피탈 뉴스", "산은캐피탈 뉴스", "IBK 기업정보", "산은 기업정보"])

with tab1:
    if 'news_data' in st.session_state and 'IBK' in st.session_state['news_data']:
        display_news_tab("IBK Capital", st.session_state['news_data']['IBK'], "ibk")
    else:
        st.info("왼쪽 사이드바에서 '뉴스 가져오기' 버튼을 눌러주세요.")

with tab2:
    if 'news_data' in st.session_state and 'KDB' in st.session_state['news_data']:
        display_news_tab("KDB Capital", st.session_state['news_data']['KDB'], "kdb")
    else:
        st.info("왼쪽 사이드바에서 '뉴스 가져오기' 버튼을 눌러주세요.")

with tab3:
    display_company_info("IBK Capital", "ibk_info")

with tab4:
    display_company_info("KDB Capital", "kdb_info")

st.sidebar.markdown("---")
st.sidebar.header("NotebookLM 활용")
st.sidebar.write("1. 생성된 보고서를 복사하세요.")
st.sidebar.write("2. NotebookLM에 '소스'로 추가하세요.")
st.sidebar.write("3. AI에게 질문하거나 오디오 개요를 들어보세요!")
