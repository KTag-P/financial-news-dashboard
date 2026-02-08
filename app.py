import streamlit as st
import news_fetcher
import deduplicator
import report_generator
import datetime
import socket

st.set_page_config(page_title="Financial News Dashboard", layout="wide")

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
st.sidebar.title("Configuration")
days_lookback = st.sidebar.slider("Days Lookback", 1, 7, 1)

# Mobile Access Info
local_ip = get_local_ip()
st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Mobile Access")
st.sidebar.markdown(f"Connect to same Wi-Fi and go to:")
st.sidebar.code(f"http://{local_ip}:8501")

st.title("Financial News Dashboard")

if st.sidebar.button("Fetch News"):
    st.session_state['news_data'] = {}
    
    with st.spinner("Fetching news... (This may take a while for full content scraping)"):
        # Fetch IBK
        raw_ibk = news_fetcher.fetch_news("IBK캐피탈", days=days_lookback)
        unique_ibk = deduplicator.deduplicate_news(raw_ibk)
        st.session_state['news_data']['IBK'] = unique_ibk
        
        # Fetch KDB
        raw_kdb = news_fetcher.fetch_news("산은캐피탈", days=days_lookback)
        unique_kdb = deduplicator.deduplicate_news(raw_kdb)
        st.session_state['news_data']['KDB'] = unique_kdb
        
        st.success("News fetched successfully!")

def display_company_news(company_name, news_items):
    st.header(f"{company_name} News ({len(news_items)})")
    
    # 1. Daily Summary Section (Heuristic)
    if news_items:
        with st.container():
            st.subheader("📢 Daily Briefing (Top Headlines)")
            summary_box = ""
            for i, item in enumerate(news_items[:5]):
                summary_box += f"{i+1}. {item['title']}\n"
            st.info(summary_box)
            
            # Button to generate full markdown for this company
            if st.button(f"Generate {company_name} Report", key=f"btn_{company_name}"):
                report = report_generator.generate_markdown_report(news_items, title=f"{company_name} News Report")
                st.code(report, language='markdown')

    # 2. News List
    for news in news_items:
        with st.expander(news['title']):
            st.write(f"**Source**: {news.get('link', '')}")
            st.write(f"**Published**: {news.get('published', 'N/A')}")
            
            # Show summary or full content
            content = news.get('summary', '')
            if content:
                st.markdown(content)
            else:
                st.warning("No content available.")
            
            original = news.get('original_link') or news['link']
            st.markdown(f"[Read Original]({original})")

if 'news_data' in st.session_state:
    tab1, tab2 = st.tabs(["IBK Capital", "KDB Capital"])
    
    with tab1:
        display_company_news("IBK Capital", st.session_state['news_data'].get('IBK', []))
        
    with tab2:
        display_company_news("KDB Capital", st.session_state['news_data'].get('KDB', []))
else:
    st.info("Click 'Fetch News' to start.")

st.sidebar.markdown("---")
st.sidebar.header("NotebookLM Integration")
st.sidebar.write("1. Copy the generated report.")
st.sidebar.write("2. Upload to NotebookLM as a source.")
