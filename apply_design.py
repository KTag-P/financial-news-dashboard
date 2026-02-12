"""Apply the new premium design from 새 폴더 to app.py"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print(f"Original lines: {len(lines)}")

# ============================================
# PART 1: Replace CSS block (lines 28 to 538)
# The CSS+header block starts at line 28 and ends at line 538
# ============================================

NEW_CSS_AND_HEADER = r'''# Premium Dashboard CSS + Header
import simple_summarizer
import llm_summarizer

CURRENT_YEAR = str(datetime.now().year)
_now = datetime.now()
_date_str = _now.strftime("%Y년 %m월 %d일")
_day_kor = ["월", "화", "수", "목", "금", "토", "일"][_now.weekday()]

st.markdown("""
<style>
    /* ============================================
       Premium Dashboard Design System
       ============================================ */
    
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
    
    /* === CSS VARIABLES === */
    :root {
        --primary-500: #4150f0;
        --primary-400: #6773f3;
        --primary-100: #d9dcfc;
        --primary-50: #eff1fe;
        --accent-500: #f97316;
        --accent-400: #fb923c;
        --accent-50: #fff7ed;
        --success: #22c55e;
        --danger: #ef4444;
        --info: #3b82f6;
        --warning: #f59e0b;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-400: #94a3b8;
        --gray-500: #64748b;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-800: #1e293b;
        --gray-900: #0f172a;
        --bg-body: #f0f4f8;
        --bg-card: #ffffff;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --radius-md: 12px;
        --radius-lg: 16px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* === BASE TYPOGRAPHY === */
    html, body, [class*="css"] {
        font-family: "Pretendard", -apple-system, BlinkMacSystemFont, system-ui, Roboto, "Noto Sans KR", sans-serif !important;
        letter-spacing: -0.01em;
        color: var(--text-primary);
    }
    
    /* === BACKGROUND === */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-body) !important;
    }
    
    /* === MAIN CONTAINER === */
    .block-container {
        max-width: 1200px !important;
        padding-top: 0 !important;
        padding-bottom: 4rem !important;
    }
    
    /* === CUSTOM HEADER === */
    .dashboard-header {
        background: linear-gradient(135deg, var(--gray-900) 0%, var(--gray-800) 40%, var(--gray-700) 100%);
        padding: 20px 28px 16px;
        margin: -1rem -1rem 24px -1rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .header-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .logo-icon {
        width: 42px;
        height: 42px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }
    .header-brand h1 {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-brand .subtitle {
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
        margin-top: 2px;
    }
    .header-controls {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        color: rgba(255,255,255,0.7);
        font-size: 12px;
        font-weight: 500;
    }
    
    /* === STREAMLIT TABS STYLING === */
    [data-baseweb="tab-list"] {
        background: var(--gray-800) !important;
        border-radius: 0 !important;
        gap: 0 !important;
        padding: 0 20px !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        margin: -1rem -1rem 20px -1rem !important;
    }
    [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: rgba(255,255,255,0.55) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
        border-radius: 0 !important;
        transition: all 0.2s !important;
        white-space: nowrap !important;
    }
    [data-baseweb="tab"]:hover {
        color: rgba(255,255,255,0.85) !important;
        background: rgba(255,255,255,0.05) !important;
    }
    [aria-selected="true"][data-baseweb="tab"] {
        color: #ffffff !important;
        background: rgba(255,255,255,0.1) !important;
        border-bottom: 2px solid var(--primary-400) !important;
    }
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {
        display: none !important;
    }
    
    /* === STAT CARDS === */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-lg);
        padding: 20px;
        transition: all 0.2s;
        box-shadow: var(--shadow-sm);
    }
    .stat-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .stat-card .stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 12px;
    }
    .stat-card.ibk .stat-icon { background: var(--primary-50); color: var(--primary-500); }
    .stat-card.kdb .stat-icon { background: #ecfdf5; color: #059669; }
    .stat-card.accent .stat-icon { background: var(--accent-50); color: var(--accent-500); }
    .stat-card.info .stat-icon { background: #eff6ff; color: var(--info); }
    .stat-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
    .stat-value { font-size: 28px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em; }
    .stat-change { font-size: 12px; font-weight: 600; margin-top: 6px; display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 20px; }
    .stat-change.up { color: #059669; background: #ecfdf5; }
    .stat-change.down { color: var(--danger); background: #fef2f2; }
    
    /* === MARKET CARDS === */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title .icon { font-size: 20px; }
    .market-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
        margin-bottom: 28px;
    }
    .market-card {
        background: var(--bg-card);
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-md);
        padding: 16px;
        text-align: center;
        transition: all 0.2s;
        cursor: pointer;
        box-shadow: var(--shadow-sm);
    }
    .market-card:hover {
        border-color: var(--primary-400);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .market-card .label {
        font-size: 12px;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .market-card .price {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .market-card .change {
        font-size: 12px;
        font-weight: 600;
    }
    .price-up, .price-up .price, .price-up .change { color: #dc2626 !important; }
    .price-down, .price-down .price, .price-down .change { color: #2563eb !important; }
    .price-flat, .price-flat .price, .price-flat .change { color: var(--text-secondary) !important; }
    
    /* === COMPANY PANELS === */
    .company-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 28px;
    }
    .company-panel {
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-lg);
        overflow: hidden;
        background: var(--bg-card);
        box-shadow: var(--shadow-sm);
    }
    .company-panel-header {
        padding: 18px 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        font-weight: 700;
        font-size: 15px;
    }
    .company-panel-header.ibk { background: linear-gradient(135deg, #1e40af, #3b82f6); }
    .company-panel-header.kdb { background: linear-gradient(135deg, #065f46, #10b981); }
    .company-panel-header h3 { margin: 0; font-size: 16px; }
    .badge-tag {
        padding: 4px 10px;
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* === STREAMLIT COMPONENTS STYLING === */
    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid var(--gray-200) !important;
        border-radius: var(--radius-md) !important;
        background: var(--bg-card) !important;
        box-shadow: var(--shadow-sm) !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-400)) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(65,80,240,0.3) !important;
    }
    
    /* Info/Warning/Success boxes */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: none !important;
    }
    
    /* Text inputs */
    [data-testid="stTextInput"] input {
        border-radius: 8px !important;
        border-color: var(--gray-200) !important;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        border-radius: 8px !important;
    }
    
    /* Radio buttons (horizontal) */
    [data-testid="stRadio"] > div {
        gap: 8px !important;
    }
    [data-testid="stRadio"] label {
        border-radius: 20px !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--gray-900) !important;
    }
    [data-testid="stSidebar"] * {
        color: rgba(255,255,255,0.8) !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background: rgba(255,255,255,0.06) !important;
    }
    
    /* Hide Streamlit default header/footer */
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { visibility: hidden; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--gray-300); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--gray-400); }
    
    /* === SECTION DIVIDERS === */
    hr {
        border: none;
        border-top: 1px solid var(--gray-200);
        margin: 24px 0;
    }
    
    /* === SCROLL TOP BUTTON === */
    .scroll-top-btn {
        position: fixed !important;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, var(--primary-500), var(--primary-400));
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 4px 15px rgba(65,80,240,0.4);
        transition: transform 0.2s, box-shadow 0.2s;
        text-decoration: none !important;
    }
    .scroll-top-btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 6px 20px rgba(65,80,240,0.6);
    }
    
    /* === MOBILE RESPONSIVE === */
    @media only screen and (max-width: 768px) {
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
        .market-grid { grid-template-columns: repeat(2, 1fr); }
        .company-grid { grid-template-columns: 1fr; }
        .dashboard-header { padding: 16px 20px 12px; }
        .header-brand h1 { font-size: 1.1rem; }
        .stat-value { font-size: 22px; }
        .stButton button { width: 100% !important; }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 auto !important;
            min-width: 0px !important;
        }
        [data-baseweb="tab-list"] { padding: 0 10px !important; overflow-x: auto !important; }
        [data-baseweb="tab"] { font-size: 12px !important; padding: 10px 12px !important; }
    }
</style>
""", unsafe_allow_html=True)

# Custom Header
st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-top">
            <div class="header-brand">
                <div class="logo-icon">🏦</div>
                <div>
                    <h1>캐피탈사 채용 대비 Dashboard</h1>
                    <div class="subtitle">IBK캐피탈 · 산은캐피탈 종합 분석</div>
                </div>
            </div>
            <div class="header-controls">
                <span class="badge">📅 {_date_str} ({_day_kor})</span>
                <span class="badge">🕐 {CURRENT_YEAR}.{_now.strftime("%m.%d")} 기준</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Stat Cards
st.markdown("""
    <div class="stats-grid">
        <div class="stat-card ibk">
            <div class="stat-icon">🏢</div>
            <div class="stat-label">IBK캐피탈 총자산</div>
            <div class="stat-value">12.8조원</div>
            <span class="stat-change up">↑ +11.3% YoY</span>
        </div>
        <div class="stat-card kdb">
            <div class="stat-icon">🏛️</div>
            <div class="stat-label">산은캐피탈 총자산</div>
            <div class="stat-value">10.2조원</div>
            <span class="stat-change down">↓ -24.4% YoY</span>
        </div>
        <div class="stat-card accent">
            <div class="stat-icon">🏆</div>
            <div class="stat-label">IBK 순이익 (역대최대)</div>
            <div class="stat-value">2,142억</div>
            <span class="stat-change up">↑ +19% YoY</span>
        </div>
        <div class="stat-card info">
            <div class="stat-icon">🛡️</div>
            <div class="stat-label">KDB 연체율 (업계 최저)</div>
            <div class="stat-value">0.10%</div>
            <span class="stat-change up">↓ -0.05%p</span>
        </div>
    </div>
""", unsafe_allow_html=True)'''

# ============================================
# PART 2: Replace the market card section
# Find "st.markdown("### 🌏 실시간 시장 지표 (Market Indicators)")"
# and replace with custom HTML version
# ============================================

MARKET_SECTION = r'''    st.markdown('<div class="section-title"><span class="icon">🌏</span> 실시간 시장 지표</div>', unsafe_allow_html=True)
    
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
        
        # Build market grid HTML
        market_html = '<div class="market-grid">'
        for label, key in metrics:
            if key in market_data:
                item = market_data[key]
                color_cls = "price-up" if item['color'] == "red" else "price-down" if item['color'] == "blue" else "price-flat"
                market_html += f"""
                    <div class="market-card">
                        <div class="label">{label}</div>
                        <div class="price {color_cls}">{item['price']}</div>
                        <div class="change {color_cls}">{item['change']}</div>
                    </div>"""
        market_html += '</div>'
        st.markdown(market_html, unsafe_allow_html=True)'''

OLD_MARKET_LINE = '    st.markdown("### 🌏 실시간 시장 지표 (Market Indicators)")'
OLD_MARKET_SECTION_END = "        st.warning(\"시장 데이터를 불러오는 중 오류가 발생했습니다.\")"

# ============================================
# Apply changes
# ============================================

# Read the file freshly
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Find and replace the CSS+header block (lines 28 to ~538)
# Find the marker for old CSS start and end
css_start_marker = "# Premium Financial Dashboard CSS"
if css_start_marker not in content:
    css_start_marker = "# Custom CSS for Fonts and Badges"
    if css_start_marker not in content:
        css_start_marker = "# Premium Dashboard CSS"

header_end_marker = '""", unsafe_allow_html=True)\n'

# Find the CSS block
css_start_idx = content.index(css_start_marker)

# Find the closing of the header markdown block (after stat cards area)
# We need the one that comes after the header section, before "# ... (Market Data)"
market_data_comment = "# ... (Market Data)"
market_comment_idx = content.index(market_data_comment)

# Find the last '""", unsafe_allow_html=True)' before the market comment
search_region = content[:market_comment_idx]
last_close_idx = search_region.rfind(header_end_marker)
end_of_old_block = last_close_idx + len(header_end_marker)

# Replace
content = content[:css_start_idx] + NEW_CSS_AND_HEADER + "\n" + content[end_of_old_block:]

# Step 2: Replace the market section
old_market_start = content.index(OLD_MARKET_LINE)
old_market_end_text = "        st.warning(\"시장 데이터를 불러오는 중 오류가 발생했습니다.\")"
old_market_end = content.index(old_market_end_text, old_market_start)
old_market_end += len(old_market_end_text)

content = content[:old_market_start] + MARKET_SECTION + "\n" + content[old_market_end:]

# Step 3: Also update the company comparison section header
# Replace "### 🏢 IBK캐피탈 vs 산은캐피탈 비교 분석" styling
old_company_title = 'st.header(f"🏢 {company_name} 기업 개요")'
new_company_title = 'st.markdown(f\'<div class="section-title"><span class="icon">🏢</span> {company_name} 기업 개요</div>\', unsafe_allow_html=True)'
content = content.replace(old_company_title, new_company_title)

# Write the result
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

new_lines = content.split('\n')
print(f"New lines: {len(new_lines)}")
print("Done! Design applied successfully.")
