"""
Complete design overhaul: Apply ALL styles from 새 폴더 reference design.
Transforms: CSS, display_company_info, display_archive, adds keyword search.
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original: {len(content.splitlines())} lines")

# =====================================================
# STEP 1: Add missing CSS classes from style.css
# We need to add: issue-card, fin-table, timeline, 
# biz-card, recruit-card, case-card, news-toolbar, search-box
# =====================================================

ADDITIONAL_CSS = """
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
"""

# Find the closing </style> tag in the CSS block and insert additional CSS before it
old_style_close = "</style>\n\"\"\", unsafe_allow_html=True)"
new_style_close = ADDITIONAL_CSS + "\n</style>\n\"\"\", unsafe_allow_html=True)"
content = content.replace(old_style_close, new_style_close, 1)

# =====================================================
# STEP 2: Rewrite display_company_info function 
# to use custom HTML (company panels, issue cards,
# financial tables, timelines, recruitment cards, case cards)
# =====================================================

OLD_DISPLAY_FUNC_START = "def display_company_info(company_name, key):"
OLD_DISPLAY_FUNC_END = "                st.warning(f\"**교훈**: {case['lesson']}\")"

# Find the function
func_start = content.index(OLD_DISPLAY_FUNC_START)
func_end = content.index(OLD_DISPLAY_FUNC_END, func_start) + len(OLD_DISPLAY_FUNC_END)

NEW_DISPLAY_FUNC = '''def display_company_info(company_name, key):
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
            """, unsafe_allow_html=True)'''

content = content[:func_start] + NEW_DISPLAY_FUNC + content[func_end:]

# =====================================================
# STEP 3: Update display_archive header to use section-title
# =====================================================
old_archive_header = '    st.header(f"🗄️ {title}")'
new_archive_header = '    st.markdown(f\'<div class="section-title"><span class="icon">📰</span> {title}</div>\', unsafe_allow_html=True)'
content = content.replace(old_archive_header, new_archive_header)

# =====================================================
# STEP 4: Update the Altair chart line color to match theme
# =====================================================
content = content.replace("mark_line(color='#C9A96E'", "mark_line(color='#4150f0'")

# =====================================================
# STEP 5: Update company panel header on Tab1
# The reference design shows "IBK캐피탈 vs 산은캐피탈 비교 분석" 
# as a section title before the two columns
# =====================================================
old_tab1 = """with tab1:
     col_info1, col_info2 = st.columns(2)
     with col_info1:
         display_company_info("IBK Capital", "ibk_info")
     with col_info2:
         display_company_info("KDB Capital", "kdb_info")"""

new_tab1 = """with tab1:
     st.markdown('<div class="section-title"><span class="icon">🏢</span> IBK캐피탈 vs 산은캐피탈 비교 분석</div>', unsafe_allow_html=True)
     col_info1, col_info2 = st.columns(2)
     with col_info1:
         display_company_info("IBK Capital", "ibk_info")
     with col_info2:
         display_company_info("KDB Capital", "kdb_info")"""

content = content.replace(old_tab1, new_tab1)

# =====================================================
# STEP 6: Style the news archive search/filter UI
# Change selectbox labels to Korean-style
# =====================================================
old_year_select = 'selected_year = st.selectbox(f"{title} 연도 Archive", ["All", 2026, 2025, 2024, 2023, 2022, 2021, 2020], key=f"year_{company_key}")'
new_year_select = 'selected_year = st.selectbox("전체 연도", ["All", 2026, 2025, 2024, 2023, 2022, 2021, 2020], key=f"year_{company_key}")'
content = content.replace(old_year_select, new_year_select)

old_month_select = 'selected_month = st.selectbox(f"월(Month) 선택", ["All"] + list(range(1, 13)), key=f"month_{company_key}")'
new_month_select = 'selected_month = st.selectbox("전체 월", ["All"] + list(range(1, 13)), key=f"month_{company_key}")'
content = content.replace(old_month_select, new_month_select)

# Update search placeholder to match reference
old_search = '        "🔍 키워드 검색 (제목 + 본문)",'
new_search = '        "키워드 검색 (제목 + 본문)...",'
content = content.replace(old_search, new_search)

# Write output
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated: {len(content.splitlines())} lines")
print("✅ Full design applied successfully!")
