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

# Premium Dashboard CSS + Header
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

    /* === KEY ISSUES (issue-card) === */
    .issue-card {
        background: var(--gray-50);
        border-radius: var(--radius-md);
        padding: 18px 20px;
        margin-bottom: 12px;
        border-left: 4px solid var(--primary-500);
        transition: all 0.25s;
    }
    .issue-card:hover {
        background: var(--primary-50);
        transform: translateX(4px);
        box-shadow: var(--shadow-sm);
    }
    .issue-card .tag {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-500), #3440c0);
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .issue-card.kdb-issue { border-left-color: #00695c; }
    .issue-card.kdb-issue .tag { background: linear-gradient(135deg, #00897b, #004d40); }
    .issue-card h4 {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
        color: var(--text-primary);
        line-height: 1.4;
    }
    .issue-card p {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.65;
        margin: 0;
    }

    /* === FINANCIAL TABLE === */
    .fin-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 13px;
        border-radius: var(--radius-md);
        overflow: hidden;
        margin: 12px 0 20px;
    }
    .fin-table th {
        background: linear-gradient(135deg, var(--gray-800), var(--gray-900));
        color: white;
        padding: 12px 14px;
        text-align: left;
        font-weight: 600;
        font-size: 12px;
        white-space: nowrap;
    }
    .fin-table.kdb-table th { background: linear-gradient(135deg, #065f46, #004d40); }
    .fin-table td {
        padding: 11px 14px;
        border-bottom: 1px solid var(--gray-100);
    }
    .fin-table tbody tr:last-child td { border-bottom: none; }
    .fin-table tbody tr:hover td { background: var(--gray-50); }
    .fin-table .metric-name {
        font-weight: 700;
        color: var(--primary-500);
        white-space: nowrap;
    }
    .fin-table.kdb-table .metric-name { color: #00695c; }

    /* === TIMELINE === */
    .timeline {
        position: relative;
        padding-left: 28px;
        margin: 12px 0 20px;
    }
    .timeline::before {
        content: '';
        position: absolute;
        left: 9px;
        top: 4px;
        bottom: 4px;
        width: 2px;
        background: linear-gradient(180deg, var(--primary-400), var(--primary-100));
        border-radius: 2px;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 18px;
        padding-left: 22px;
        transition: all 0.25s;
    }
    .timeline-item:hover { transform: translateX(3px); }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -22px;
        top: 6px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: var(--primary-400);
        border: 3px solid var(--bg-card);
        box-shadow: 0 0 0 2px #cbd5e1;
    }
    .timeline-item:hover::before { transform: scale(1.2); }
    .timeline-item.current::before {
        background: #f97316;
        box-shadow: 0 0 0 2px #fb923c, 0 0 12px rgba(249,115,22,0.3);
    }
    .timeline-year {
        font-size: 12px;
        font-weight: 800;
        color: var(--primary-500);
    }
    .timeline-event {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 3px;
        line-height: 1.5;
    }

    /* === BUSINESS AREAS CARD === */
    .biz-card {
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-md);
        margin-bottom: 12px;
        overflow: hidden;
        background: var(--bg-card);
        transition: all 0.25s;
    }
    .biz-card:hover {
        box-shadow: var(--shadow-sm);
        border-color: var(--primary-200);
    }
    .biz-card-header {
        padding: 14px 18px;
        background: var(--gray-50);
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: 600;
        font-size: 14px;
    }
    .biz-card-header .scale {
        font-size: 12px;
        color: var(--text-muted);
        font-weight: 500;
    }

    /* === RECRUITMENT === */
    .recruit-values {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 18px;
    }
    .recruit-values .value-badge {
        background: linear-gradient(135deg, var(--primary-50), var(--primary-100));
        color: #273090;
        padding: 7px 16px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid var(--primary-200);
        transition: all 0.15s;
    }
    .recruit-values .value-badge:hover {
        transform: translateY(-1px);
    }
    .recruit-card {
        background: var(--gray-50);
        border-radius: var(--radius-md);
        padding: 18px 20px;
        margin-bottom: 12px;
        border-left: 4px solid #f59e0b;
        transition: all 0.25s;
    }
    .recruit-card:hover {
        transform: translateX(4px);
        box-shadow: var(--shadow-sm);
    }
    .recruit-card.upcoming {
        border-left-color: #ef4444;
        background: #fef2f2;
    }
    .recruit-card.completed {
        border-left-color: #22c55e;
        background: #ecfdf5;
    }
    .recruit-card h4 {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 10px;
        color: var(--text-primary);
    }
    .recruit-card .meta {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        font-size: 12px;
        color: var(--text-secondary);
    }
    .recruit-card .meta span {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .recruit-card .recruit-note {
        margin-top: 8px;
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.5;
    }

    /* === CASE STUDIES === */
    .case-card {
        border-radius: var(--radius-md);
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: all 0.25s;
        border: 1px solid transparent;
    }
    .case-card.success {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
    }
    .case-card.failure {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
    }
    .case-card:hover {
        transform: translateX(4px);
        box-shadow: var(--shadow-sm);
    }
    .case-card h4 {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
        color: var(--text-primary);
    }
    .case-card .category-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 10px;
        color: white;
    }
    .case-card.success .category-tag { background: #10b981; }
    .case-card.failure .category-tag { background: #f59e0b; }
    .case-card p {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.6;
        margin: 0;
    }

    /* === COMPANY PANEL (for tab1 side-by-side) === */
    .company-panel {
        background: var(--bg-card);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--gray-100);
        transition: all 0.25s;
    }
    .company-panel:hover { box-shadow: var(--shadow-md); }
    .company-panel-header {
        padding: 22px 26px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        font-weight: 700;
        font-size: 15px;
    }
    .company-panel-header.ibk {
        background: linear-gradient(135deg, #1976d2, #0d47a1, #1a237e);
    }
    .company-panel-header.kdb {
        background: linear-gradient(135deg, #00897b, #00695c, #004d40);
    }
    .company-panel-header h3 {
        margin: 0;
        font-size: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .badge-tag {
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.15);
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 500;
    }
    .company-panel-body {
        padding: 26px;
    }

    /* === SECTION SUBTITLE === */
    .section-subtitle {
        font-size: 15px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 28px 0 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* === CHARTS GRID === */
    .charts-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    .charts-grid .chart-full { grid-column: span 2; }
    .chart-container {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 24px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--gray-100);
    }
    .chart-container:hover { box-shadow: var(--shadow-md); }
    @media (max-width: 768px) {
        .charts-grid { grid-template-columns: 1fr; }
        .charts-grid .chart-full { grid-column: span 1; }
    }

    /* === RECRUIT LINK === */
    .recruit-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: var(--primary-500);
        text-decoration: none;
        font-weight: 600;
        font-size: 13px;
        padding: 8px 14px;
        border-radius: 8px;
        transition: all 0.15s;
        margin-top: 12px;
    }
    .recruit-link:hover { background: var(--primary-50); }

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
""", unsafe_allow_html=True)
    

# ... (Market Data)


# ... (Tabs)
with st.container():
    
    st.markdown('<div class="section-title"><span class="icon">🌏</span> 실시간 시장 지표</div>', unsafe_allow_html=True)
    
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
        st.markdown(market_html, unsafe_allow_html=True)

        
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
                
                c = alt.Chart(df_chart).mark_line(color='#4150f0', strokeWidth=2).encode(
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

    is_ibk = "IBK" in company_name
    brand_class = "ibk" if is_ibk else "kdb"
    brand_label = "IBK금융그룹" if is_ibk else "KDB산업은행"
    display_name = "IBK캐피탈" if is_ibk else "산은캐피탈"
    table_class = "" if is_ibk else " kdb-table"
    issue_class = "" if is_ibk else " kdb-issue"

    # Company Panel Header
    st.markdown(f"""
        <div class="company-panel">
            <div class="company-panel-header {brand_class}">
                <h3>🏛 {display_name}</h3>
                <span class="badge-tag">{brand_label}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Key Issues
    st.markdown(f'<div class="section-subtitle">🔑 {CURRENT_YEAR} 경영 전략 (Key Issues)</div>', unsafe_allow_html=True)
    
    if company_name in company_data.key_issues_curated:
        issues = company_data.key_issues_curated[company_name]
        for news in issues:
            tag = news.get('tag', '전략')
            st.markdown(f"""
                <div class="issue-card{issue_class}">
                    <span class="tag">{tag}</span>
                    <h4>{news['title']}</h4>
                    <p>{news.get('summary', '')}</p>
                </div>
            """, unsafe_allow_html=True)
    elif f'{key}_issues' in st.session_state:
        issues = st.session_state[f'{key}_issues']
        for news in issues:
            st.markdown(f"""
                <div class="issue-card{issue_class}">
                    <h4>{news['title']}</h4>
                    <p>{news.get('summary', '')}</p>
                </div>
            """, unsafe_allow_html=True)

    # Business Areas
    st.markdown('<div class="section-subtitle">💼 주요 사업 (Business Areas)</div>', unsafe_allow_html=True)
    for biz in data['business']:
        with st.expander(f"{biz['name']} ({biz['scale']})"):
            st.write(f"**개요**: {biz['desc']}")
            if 'details' in biz:
                for detail in biz['details']:
                    st.markdown(f"- {detail}")

    # Financial Table
    st.markdown('<div class="section-subtitle">📊 주요 재무 지표</div>', unsafe_allow_html=True)
    fin = data['financials']
    metric_names = {
        "Assets": "총자산", "Net Income": "당기순이익", "Revenue": "매출",
        "ROE": "ROE", "Delinquency Rate": "연체율",
        "NPL Ratio": "NPL비율"
    }
    
    years = list(fin.keys())
    metrics_keys = list(next(iter(fin.values())).keys()) if fin else []
    
    table_html = f'<table class="fin-table{table_class}"><thead><tr><th>구분</th>'
    for y in years:
        table_html += f'<th>{y}</th>'
    table_html += '</tr></thead><tbody>'
    
    for mk in metrics_keys:
        label = metric_names.get(mk, mk)
        table_html += f'<tr><td class="metric-name">{label}</td>'
        for y in years:
            val = fin[y].get(mk, 'N/A')
            if val and val != 'N/A':
                table_html += f'<td>{val}</td>'
            else:
                table_html += '<td>-</td>'
        table_html += '</tr>'
    
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # Timeline (History)
    st.markdown('<div class="section-subtitle">📜 주요 연혁</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline">'
    for event in data['history'][-5:]:
        year_text = event['year']
        current_class = ' current' if CURRENT_YEAR in year_text else ''
        timeline_html += f"""
            <div class="timeline-item{current_class}">
                <div class="timeline-year">{year_text}</div>
                <div class="timeline-event">{event['event']}</div>
            </div>"""
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

    # Recruitment
    st.markdown('<div class="section-subtitle">👥 채용 정보</div>', unsafe_allow_html=True)
    recruitment_values = data.get('recruitment_values')
    recruitment_link = data.get('recruitment_link')

    if recruitment_values:
        badges_html = '<div class="recruit-values">'
        for v in recruitment_values:
            badges_html += f'<span class="value-badge">{v}</span>'
        badges_html += '</div>'
        st.markdown(badges_html, unsafe_allow_html=True)

    recruit_key = "IBK" if is_ibk else "KDB"
    all_recruitment = recruitment_fetcher.get_all_recruitment_info(recruit_key)

    if all_recruitment:
        auto_items = [r for r in all_recruitment if r.get('is_auto')]
        static_items = [r for r in all_recruitment if not r.get('is_auto')]

        for rec in auto_items:
            st.markdown(f"""
                <div class="recruit-card upcoming">
                    <h4>🔔 {rec['title']}</h4>
                    <div class="meta">
                        <span>📅 {rec.get('period', '')}</span>
                        {f"<span>⏰ {rec.get('deadline', '')}</span>" if rec.get('deadline') else ''}
                    </div>
                    {f'<div class="recruit-note">{rec.get("note", "")}</div>' if rec.get('note') else ''}
                </div>
            """, unsafe_allow_html=True)
            if rec.get('link'):
                st.markdown(f"👉 [공고 바로가기]({rec['link']})")

        for rec in static_items:
            is_upcoming = CURRENT_YEAR in rec.get('title', '')
            card_class = 'upcoming' if is_upcoming else 'completed' if '완료' in rec.get('title', '') else ''
            icon = '🔴' if is_upcoming else '✅' if '완료' in rec.get('title', '') else '📋'
            
            meta_parts = []
            if rec.get('period'):
                meta_parts.append(f"📅 {rec['period']}")
            if rec.get('scale'):
                meta_parts.append(f"👥 {rec['scale']}")
            if rec.get('roles'):
                meta_parts.append(f"💼 {', '.join(rec['roles'])}")
            
            meta_html = ''.join(f'<span>{m}</span>' for m in meta_parts)

            st.markdown(f"""
                <div class="recruit-card {card_class}">
                    <h4>{icon} {rec['title']}</h4>
                    <div class="meta">{meta_html}</div>
                    {f'<div class="recruit-note">{rec.get("note", "")}</div>' if rec.get('note') else ''}
                </div>
            """, unsafe_allow_html=True)

    if recruitment_link:
        st.markdown(f"""<a href="{recruitment_link}" target="_blank" class="recruit-link">✏️ 채용 홈페이지 바로가기</a>""", unsafe_allow_html=True)

    # Case Studies
    st.markdown('<div class="section-subtitle">📋 주요 사업 사례</div>', unsafe_allow_html=True)
    cases = company_data.case_studies.get(company_name, {})

    if cases.get("success"):
        st.markdown('<div class="section-subtitle" style="font-size:14px;">✅ 성공 사례</div>', unsafe_allow_html=True)
        for case in cases["success"]:
            st.markdown(f"""
                <div class="case-card success">
                    <span class="category-tag">{case['category']}</span>
                    <h4>{case['title']} ({case.get('period', '')})</h4>
                    <p>{case['summary']}</p>
                </div>
            """, unsafe_allow_html=True)

    if cases.get("failure"):
        st.markdown('<div class="section-subtitle" style="font-size:14px;">⚠️ 실패/교훈 사례</div>', unsafe_allow_html=True)
        for case in cases["failure"]:
            st.markdown(f"""
                <div class="case-card failure">
                    <span class="category-tag">{case['category']}</span>
                    <h4>{case['title']} ({case.get('period', '')})</h4>
                    <p>{case['summary']}</p>
                </div>
            """, unsafe_allow_html=True)

# Main Layout
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["기업 개요", "IBK캐피탈 뉴스", "산은캐피탈 뉴스", "캐피탈 업황", "거시경제", "IBK기업은행", "KDB산업은행"])

with tab1:
     st.markdown('<div class="section-title"><span class="icon">🏢</span> IBK캐피탈 vs 산은캐피탈 비교 분석</div>', unsafe_allow_html=True)
     col_info1, col_info2 = st.columns(2)
     with col_info1:
         display_company_info("IBK Capital", "ibk_info")
     with col_info2:
         display_company_info("KDB Capital", "kdb_info")

def display_archive(company_key, title, filter_mode="all"):
    st.markdown(f'<div class="section-title"><span class="icon">📰</span> {title}</div>', unsafe_allow_html=True)
    
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
        "키워드 검색 (제목 + 본문)...",
        placeholder="예: PF, 금리, 실적, 인수합병...",
        key=f"search_{company_key}"
    )

    # Date Filtering
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
         selected_year = st.selectbox("전체 연도", ["All", 2026, 2025, 2024, 2023, 2022, 2021, 2020], key=f"year_{company_key}")
    with col_filter2:
         selected_month = st.selectbox("전체 월", ["All"] + list(range(1, 13)), key=f"month_{company_key}")

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

# Scroll to Top Button
st.markdown("""
    <div class="scroll-top-btn" onclick="window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});">
        ↑
    </div>
    <script>
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
