// ============================================
// 캐피탈사 채용 대비 Dashboard - Premium App Logic
// ============================================

// Global state
let newsData = {};
let currentTab = 'overview';
const NEWS_PER_PAGE = 15;
const pageState = {};

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    initTabs();
    initHeaderScroll();
    initScrollAnimations();
    renderMarketIndicators();
    renderOverviewTab();
    await loadNewsData();
    initScrollTop();
    renderFinancialCharts();
    
    // Trigger initial animations
    requestAnimationFrame(() => {
        document.querySelectorAll('.stagger-children').forEach(el => el.classList.add('animate'));
        triggerScrollAnimations();
    });
});

// ============ DARK MODE ============
function initTheme() {
    const saved = localStorage.getItem('dashboard-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    setTheme(theme);

    document.getElementById('theme-toggle').addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
        localStorage.setItem('dashboard-theme', next);
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.querySelector('#theme-toggle i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    // Re-render charts if they exist (for color updates)
    if (typeof Chart !== 'undefined' && Chart.instances) {
        Object.values(Chart.instances).forEach(chart => {
            if (chart) {
                updateChartTheme(chart, theme);
            }
        });
    }
}

function updateChartTheme(chart, theme) {
    const textColor = theme === 'dark' ? '#94a3b8' : '#64748b';
    const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    
    if (chart.options.scales) {
        Object.values(chart.options.scales).forEach(scale => {
            if (scale.ticks) scale.ticks.color = textColor;
            if (scale.grid) scale.grid.color = gridColor;
        });
    }
    if (chart.options.plugins) {
        if (chart.options.plugins.title) chart.options.plugins.title.color = textColor;
        if (chart.options.plugins.legend?.labels) chart.options.plugins.legend.labels.color = textColor;
    }
    chart.update('none');
}

// ============ HEADER SCROLL EFFECT ============
function initHeaderScroll() {
    const header = document.getElementById('main-header');
    let ticking = false;
    
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                header.classList.toggle('scrolled', window.scrollY > 10);
                ticking = false;
            });
            ticking = true;
        }
    });
}

// ============ SCROLL ANIMATIONS ============
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Also animate stagger children
                if (entry.target.classList.contains('stagger-children')) {
                    entry.target.classList.add('animate');
                }
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.fade-in-up, .stagger-children').forEach(el => {
        observer.observe(el);
    });
}

function triggerScrollAnimations() {
    document.querySelectorAll('.fade-in-up').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 40) {
            el.classList.add('visible');
        }
    });
}

// ============ TAB SYSTEM ============
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    currentTab = tabId;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    const panel = document.getElementById(`panel-${tabId}`);
    panel.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Re-trigger animations on the newly visible panel
    requestAnimationFrame(() => {
        panel.querySelectorAll('.fade-in-up').forEach(el => el.classList.add('visible'));
        panel.querySelectorAll('.stagger-children').forEach(el => el.classList.add('animate'));
    });
}

// ============ MARKET INDICATORS ============
function renderMarketIndicators() {
    const marketData = [
        { label: 'KOSPI', price: '2,612.34', change: '+1.23%', dir: 'up', icon: '📈' },
        { label: 'KOSDAQ', price: '741.56', change: '-0.45%', dir: 'down', icon: '📉' },
        { label: 'USD/KRW', price: '1,438.20', change: '+0.32%', dir: 'up', icon: '💵' },
        { label: 'JPY/KRW', price: '9.41', change: '-0.18%', dir: 'down', icon: '💴' },
        { label: '미국채 10Y', price: '4.52%', change: '+0.05%', dir: 'up', icon: '🏛️' },
        { label: 'NASDAQ', price: '19,823.44', change: '+0.89%', dir: 'up', icon: '🇺🇸' },
        { label: 'Nikkei 225', price: '39,145.20', change: '+0.67%', dir: 'up', icon: '🇯🇵' },
        { label: 'Gold', price: '$2,912.50', change: '+0.21%', dir: 'up', icon: '🥇' },
        { label: 'Silver', price: '$32.45', change: '-0.33%', dir: 'down', icon: '🥈' },
        { label: 'Copper', price: '$9,234.00', change: '+0.15%', dir: 'up', icon: '🏗️' }
    ];

    const grid = document.getElementById('market-grid');
    grid.innerHTML = marketData.map(m => `
        <div class="market-card">
            <div class="market-label">${m.label}</div>
            <div class="market-price ${m.dir}">${m.price}</div>
            <div class="market-change ${m.dir}">
                <i class="fas fa-caret-${m.dir === 'up' ? 'up' : 'down'}" style="font-size:14px;"></i>
                ${m.change}
            </div>
        </div>
    `).join('');
}

// ============ OVERVIEW TAB ============
function renderOverviewTab() {
    renderCompanyPanel('IBK Capital', 'ibk', document.getElementById('ibk-panel'));
    renderCompanyPanel('KDB Capital', 'kdb', document.getElementById('kdb-panel'));
}

function renderCompanyPanel(companyName, code, container) {
    const data = companyInfo[companyName];
    const issues = keyIssues[companyName] || [];
    const cases = caseStudies[companyName] || {};

    let html = '';

    // Key Issues
    html += `<div class="section-subtitle">🔑 2026 경영 전략 (Key Issues)</div>`;
    issues.forEach(issue => {
        html += `
        <div class="issue-card">
            <span class="tag">${issue.tag}</span>
            <h4>${issue.title}</h4>
            <p>${issue.summary}</p>
        </div>`;
    });

    // Business Areas
    html += `<div class="section-subtitle" style="margin-top:28px;">💼 주요 사업 (Business Areas)</div>`;
    data.business.forEach((biz, i) => {
        html += `
        <div class="biz-card">
            <div class="biz-card-header" onclick="toggleBiz(this)">
                <span>${biz.name}</span>
                <span class="scale">${biz.scale} <i class="fas fa-chevron-down" style="font-size:10px;"></i></span>
            </div>
            <div class="biz-card-body">
                <p style="margin-bottom:12px;"><strong>개요:</strong> ${biz.desc}</p>
                ${biz.details.map(d => `<div class="detail-item">${d}</div>`).join('')}
            </div>
        </div>`;
    });

    // Financials
    html += `<div class="section-subtitle" style="margin-top:28px;">📊 주요 재무 지표</div>`;
    html += `<div style="overflow-x:auto;border-radius:var(--radius-md);border:1px solid var(--border-subtle);"><table class="fin-table"><thead><tr><th>구분</th>`;
    const years = Object.keys(data.financials);
    years.forEach(y => html += `<th>${y}</th>`);
    html += `</tr></thead><tbody>`;
    const metrics = Object.keys(Object.values(data.financials)[0]);
    metrics.forEach(metric => {
        html += `<tr><td class="year-cell">${metric}</td>`;
        years.forEach(y => {
            const val = data.financials[y][metric] || '-';
            html += `<td>${val}</td>`;
        });
        html += `</tr>`;
    });
    html += `</tbody></table></div>`;

    // History
    html += `<div class="section-subtitle" style="margin-top:28px;">📜 주요 연혁</div>`;
    html += `<div class="timeline">`;
    data.history.forEach(h => {
        const isCurrent = h.year === '2025' || h.year === '2026';
        html += `
        <div class="timeline-item ${isCurrent ? 'current' : ''}">
            <span class="timeline-year">${h.year}</span>
            <div class="timeline-event">${h.event}</div>
        </div>`;
    });
    html += `</div>`;

    // Recruitment
    html += `<div class="section-subtitle" style="margin-top:28px;">🧑‍🤝‍🧑 채용 정보</div>`;
    if (data.recruitmentValues) {
        html += `<div class="recruit-values">`;
        data.recruitmentValues.forEach(v => html += `<span class="value-badge">${v}</span>`);
        html += `</div>`;
    }
    data.recruitment.forEach(rec => {
        const isUpcoming = rec.title.includes('예상') || rec.title.includes('예정');
        html += `
        <div class="recruit-card ${isUpcoming ? 'upcoming' : ''}">
            <h4>${isUpcoming ? '🔴 ' : '✅ '}${rec.title}</h4>
            <div class="meta">
                <span><i class="fas fa-calendar-alt"></i> ${rec.period}</span>
                <span><i class="fas fa-users"></i> ${rec.scale}</span>
                <span><i class="fas fa-briefcase"></i> ${rec.roles.join(', ')}</span>
            </div>
            ${rec.note ? `<p style="margin-top:10px;font-size:12px;color:var(--text-secondary);line-height:1.5;">${rec.note}</p>` : ''}
        </div>`;
    });
    if (data.recruitmentLink) {
        html += `<a href="${data.recruitmentLink}" target="_blank" class="news-link" style="margin-top:10px;"><i class="fas fa-external-link-alt"></i> 채용 홈페이지 바로가기</a>`;
    }

    // Case Studies
    html += `<div class="section-subtitle" style="margin-top:28px;">📋 주요 사업 사례</div>`;
    if (cases.success) {
        html += `<p style="font-size:13px;font-weight:700;margin-bottom:10px;color:var(--success);">✅ 성공 사례</p>`;
        cases.success.forEach((c, i) => {
            html += renderCaseCard(c, 'success', `${code}_s_${i}`);
        });
    }
    if (cases.failure) {
        html += `<p style="font-size:13px;font-weight:700;margin:18px 0 10px;color:var(--warning);">⚠️ 실패/교훈 사례</p>`;
        cases.failure.forEach((c, i) => {
            html += renderCaseCard(c, 'failure', `${code}_f_${i}`);
        });
    }

    container.innerHTML = html;
}

function renderCaseCard(c, type, id) {
    return `
    <div class="case-card ${type}" onclick="toggleCase('${id}')">
        <span class="category-tag">${c.category}</span>
        <h4>${c.title}</h4>
        <p>${c.summary}</p>
        <div class="case-details" id="case-${id}">
            <ul style="font-size:13px;padding-left:20px;color:var(--text-secondary);line-height:1.7;">
                ${c.details.map(d => `<li style="margin-bottom:6px;">${d}</li>`).join('')}
            </ul>
            <div class="case-lesson">💡 <strong>시사점:</strong> ${c.lesson}</div>
        </div>
    </div>`;
}

function toggleBiz(el) {
    const body = el.nextElementSibling;
    body.classList.toggle('open');
    const icon = el.querySelector('.scale i');
    if (icon) icon.style.transform = body.classList.contains('open') ? 'rotate(180deg)' : '';
}

function toggleCase(id) {
    const el = document.getElementById(`case-${id}`);
    el.classList.toggle('open');
}

// ============ NEWS DATA LOADING ============
async function loadNewsData() {
    const panel = document.getElementById('news-loading');
    if (panel) panel.style.display = 'flex';
    
    try {
        const resp = await fetch('reference/news_history.json');
        newsData = await resp.json();
        
        renderNewsArchive('IBK', 'ibk-news', 'IBK캐피탈 뉴스 아카이브');
        renderNewsArchive('KDB', 'kdb-news', '산은캐피탈 뉴스 아카이브');
        renderNewsArchive('Capital Industry', 'industry-news', '캐피탈 업황 아카이브');
        renderNewsArchive('Macro Economy', 'macro-news', '거시경제 아카이브');
        
        const lastUpdated = newsData._last_updated || '알 수 없음';
        document.getElementById('data-date').innerHTML = `<i class="fas fa-database"></i> ${lastUpdated}`;
    } catch (e) {
        console.error('Failed to load news data:', e);
        ['ibk-news', 'kdb-news', 'industry-news', 'macro-news'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = `<div class="empty-state"><div class="icon">📭</div><p>뉴스 데이터를 불러올 수 없습니다.</p></div>`;
        });
    }
    if (panel) panel.style.display = 'none';
}

// ============ NEWS ARCHIVE RENDERING ============
function renderNewsArchive(key, containerId, title) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const allNews = newsData[key] || [];
    if (!pageState[key]) {
        pageState[key] = { page: 1, year: 'All', month: 'All', search: '' };
    }

    const yearsSet = new Set();
    allNews.forEach(item => {
        try {
            const d = new Date(item.published);
            if (!isNaN(d)) yearsSet.add(d.getFullYear());
        } catch(e) {}
    });
    const years = Array.from(yearsSet).sort((a, b) => b - a);

    container.innerHTML = `
        <div class="news-toolbar">
            <div class="search-box">
                <i class="fas fa-search search-icon"></i>
                <input type="text" placeholder="키워드 검색 (제목 + 본문)..." id="search-${key}" 
                    value="${pageState[key].search}" 
                    oninput="debounceSearch('${key}', '${containerId}', '${title}')">
            </div>
            <select class="filter-select" id="year-${key}" onchange="filterNews('${key}', '${containerId}', '${title}')">
                <option value="All">전체 연도</option>
                ${years.map(y => `<option value="${y}" ${pageState[key].year == y ? 'selected' : ''}>${y}년</option>`).join('')}
            </select>
            <select class="filter-select" id="month-${key}" onchange="filterNews('${key}', '${containerId}', '${title}')">
                <option value="All">전체 월</option>
                ${Array.from({length:12}, (_,i) => i+1).map(m => `<option value="${m}" ${pageState[key].month == m ? 'selected' : ''}>${m}월</option>`).join('')}
            </select>
        </div>
        <div id="news-list-${key}"></div>
    `;

    renderFilteredNews(key, containerId, title);
}

let searchTimers = {};
function debounceSearch(key, containerId, title) {
    clearTimeout(searchTimers[key]);
    searchTimers[key] = setTimeout(() => filterNews(key, containerId, title), 300);
}

function filterNews(key, containerId, title) {
    const searchEl = document.getElementById(`search-${key}`);
    const yearEl = document.getElementById(`year-${key}`);
    const monthEl = document.getElementById(`month-${key}`);

    pageState[key].search = searchEl ? searchEl.value : '';
    pageState[key].year = yearEl ? yearEl.value : 'All';
    pageState[key].month = monthEl ? monthEl.value : 'All';
    pageState[key].page = 1;

    renderFilteredNews(key, containerId, title);
}

function renderFilteredNews(key, containerId, title) {
    const allNews = newsData[key] || [];
    const state = pageState[key];
    const searchLower = state.search.toLowerCase().trim();

    let filtered = allNews.filter(item => {
        if (!item || typeof item !== 'object') return false;
        try {
            if (state.year !== 'All') {
                const d = new Date(item.published);
                if (isNaN(d) || d.getFullYear() !== parseInt(state.year)) return false;
            }
            if (state.month !== 'All') {
                const d = new Date(item.published);
                if (isNaN(d) || (d.getMonth() + 1) !== parseInt(state.month)) return false;
            }
            if (searchLower) {
                const text = ((item.title || '') + ' ' + (item.summary || '') + ' ' + (item.full_content || '')).toLowerCase();
                if (!text.includes(searchLower)) return false;
            }
            return true;
        } catch(e) { return false; }
    });

    filtered.sort((a, b) => {
        try { return new Date(b.published) - new Date(a.published); }
        catch(e) { return 0; }
    });

    const totalPages = Math.ceil(filtered.length / NEWS_PER_PAGE);
    const page = Math.min(state.page, totalPages || 1);
    const startIdx = (page - 1) * NEWS_PER_PAGE;
    const pageItems = filtered.slice(startIdx, startIdx + NEWS_PER_PAGE);

    const listEl = document.getElementById(`news-list-${key}`);
    if (!listEl) return;

    let html = `<div class="news-count"><i class="fas fa-newspaper"></i> 총 <strong>${filtered.length}</strong>건의 뉴스</div>`;

    if (pageItems.length === 0) {
        html += `<div class="empty-state"><div class="icon">📭</div><p>조건에 맞는 뉴스가 없습니다.</p></div>`;
    } else {
        pageItems.forEach((item, i) => {
            const globalIdx = startIdx + i;
            let dateStr = '';
            try {
                const d = new Date(item.published);
                dateStr = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
            } catch(e) { dateStr = '날짜 미상'; }

            let titleDisplay = item.title || '제목 없음';
            if (searchLower) {
                const regex = new RegExp(`(${escapeRegExp(state.search)})`, 'gi');
                titleDisplay = titleDisplay.replace(regex, '<mark>$1</mark>');
            }

            const summary = item.summary || item.full_content || '내용 없음';
            const shortSummary = summary.length > 200 ? summary.substring(0, 200) + '...' : summary;

            html += `
            <div class="news-item" id="news-${key}-${globalIdx}">
                <div class="news-item-header" onclick="toggleNews('${key}', ${globalIdx})">
                    <span class="news-date">${dateStr}</span>
                    <span class="news-title">${titleDisplay}</span>
                    <i class="fas fa-chevron-down news-expand-icon"></i>
                </div>
                <div class="news-item-body">
                    <div class="news-summary">
                        <div class="label">💡 AI 요약</div>
                        ${shortSummary}
                    </div>
                    ${item.link ? `<a href="${item.link}" target="_blank" class="news-link"><i class="fas fa-external-link-alt"></i> 기사 원문 바로가기</a>` : ''}
                    ${item.full_content ? `
                    <details style="margin-top:12px;">
                        <summary style="cursor:pointer;font-size:13px;color:var(--text-muted);font-weight:600;padding:8px 0;">📜 뉴스 원문 전체 보기</summary>
                        <div class="news-full-text">${item.full_content}</div>
                    </details>` : ''}
                </div>
            </div>`;
        });
    }

    // Pagination
    if (totalPages > 1) {
        html += `<div class="pagination">`;
        html += `<button onclick="goPage('${key}', '${containerId}', '${title}', ${page - 1})" ${page <= 1 ? 'disabled' : ''}><i class="fas fa-chevron-left"></i></button>`;
        
        const maxVisible = 7;
        let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);
        if (endPage - startPage < maxVisible - 1) startPage = Math.max(1, endPage - maxVisible + 1);

        if (startPage > 1) {
            html += `<button onclick="goPage('${key}', '${containerId}', '${title}', 1)">1</button>`;
            if (startPage > 2) html += `<button disabled>···</button>`;
        }

        for (let p = startPage; p <= endPage; p++) {
            html += `<button class="${p === page ? 'active' : ''}" onclick="goPage('${key}', '${containerId}', '${title}', ${p})">${p}</button>`;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) html += `<button disabled>···</button>`;
            html += `<button onclick="goPage('${key}', '${containerId}', '${title}', ${totalPages})">${totalPages}</button>`;
        }

        html += `<button onclick="goPage('${key}', '${containerId}', '${title}', ${page + 1})" ${page >= totalPages ? 'disabled' : ''}><i class="fas fa-chevron-right"></i></button>`;
        html += `</div>`;
    }

    listEl.innerHTML = html;
}

function toggleNews(key, idx) {
    const el = document.getElementById(`news-${key}-${idx}`);
    if (el) el.classList.toggle('open');
}

function goPage(key, containerId, title, page) {
    if (page < 1) return;
    pageState[key].page = page;
    renderFilteredNews(key, containerId, title);
    const listEl = document.getElementById(`news-list-${key}`);
    if (listEl) listEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function escapeRegExp(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ============ FINANCIAL CHARTS ============
function renderFinancialCharts() {
    if (typeof Chart === 'undefined') return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    const fontFamily = 'Pretendard';

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    font: { family: fontFamily, size: 13, weight: '500' },
                    color: textColor,
                    padding: 20,
                    usePointStyle: true,
                    pointStyle: 'circle',
                    boxWidth: 8,
                    boxHeight: 8
                }
            },
            tooltip: {
                backgroundColor: isDark ? '#1e293b' : '#0f172a',
                titleFont: { family: fontFamily, size: 13, weight: '600' },
                bodyFont: { family: fontFamily, size: 12 },
                padding: 12,
                cornerRadius: 8,
                boxPadding: 6,
                usePointStyle: true
            }
        }
    };

    // Net Income Chart
    const ctx1 = document.getElementById('chart-net-income');
    if (ctx1) {
        new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: financialChartData.labels,
                datasets: [
                    {
                        label: 'IBK캐피탈',
                        data: financialChartData.ibkNetIncome,
                        backgroundColor: 'rgba(21, 101, 192, 0.85)',
                        borderColor: '#1565c0',
                        borderWidth: 0,
                        borderRadius: 8,
                        borderSkipped: false
                    },
                    {
                        label: '산은캐피탈',
                        data: financialChartData.kdbNetIncome,
                        backgroundColor: 'rgba(0, 105, 92, 0.85)',
                        borderColor: '#00695c',
                        borderWidth: 0,
                        borderRadius: 8,
                        borderSkipped: false
                    }
                ]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: { display: true, text: '당기순이익 비교 (억원)', font: { size: 15, weight: '700', family: fontFamily }, color: textColor, padding: { bottom: 20 } }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { callback: v => v.toLocaleString() + '억', color: textColor, font: { family: fontFamily } }, grid: { color: gridColor } },
                    x: { ticks: { color: textColor, font: { family: fontFamily, weight: '600' } }, grid: { display: false } }
                }
            }
        });
    }

    // ROE Chart
    const ctx2 = document.getElementById('chart-roe');
    if (ctx2) {
        new Chart(ctx2, {
            type: 'line',
            data: {
                labels: financialChartData.labels,
                datasets: [
                    {
                        label: 'IBK캐피탈',
                        data: financialChartData.ibkROE,
                        borderColor: '#1565c0',
                        backgroundColor: 'rgba(21, 101, 192, 0.08)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointBackgroundColor: '#1565c0',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 3,
                        pointHoverRadius: 9,
                        borderWidth: 3
                    },
                    {
                        label: '산은캐피탈',
                        data: financialChartData.kdbROE,
                        borderColor: '#00695c',
                        backgroundColor: 'rgba(0, 105, 92, 0.08)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointBackgroundColor: '#00695c',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 3,
                        pointHoverRadius: 9,
                        borderWidth: 3
                    }
                ]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: { display: true, text: 'ROE 추이 (%)', font: { size: 15, weight: '700', family: fontFamily }, color: textColor, padding: { bottom: 20 } }
                },
                scales: {
                    y: { beginAtZero: false, ticks: { callback: v => v + '%', color: textColor, font: { family: fontFamily } }, grid: { color: gridColor } },
                    x: { ticks: { color: textColor, font: { family: fontFamily, weight: '600' } }, grid: { display: false } }
                }
            }
        });
    }

    // Assets Chart
    const ctx3 = document.getElementById('chart-assets');
    if (ctx3) {
        new Chart(ctx3, {
            type: 'bar',
            data: {
                labels: financialChartData.labels,
                datasets: [
                    {
                        label: 'IBK캐피탈',
                        data: financialChartData.ibkAssets,
                        backgroundColor: 'rgba(21, 101, 192, 0.75)',
                        borderRadius: 8,
                        borderSkipped: false
                    },
                    {
                        label: '산은캐피탈',
                        data: financialChartData.kdbAssets,
                        backgroundColor: 'rgba(0, 105, 92, 0.75)',
                        borderRadius: 8,
                        borderSkipped: false
                    }
                ]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: { display: true, text: '총자산 비교 (조원)', font: { size: 15, weight: '700', family: fontFamily }, color: textColor, padding: { bottom: 20 } }
                },
                scales: {
                    y: { beginAtZero: false, ticks: { callback: v => v + '조', color: textColor, font: { family: fontFamily } }, grid: { color: gridColor } },
                    x: { ticks: { color: textColor, font: { family: fontFamily, weight: '600' } }, grid: { display: false } }
                }
            }
        });
    }
}

// ============ SCROLL TO TOP ============
function initScrollTop() {
    const btn = document.getElementById('scroll-top');
    let ticking = false;
    
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                btn.classList.toggle('visible', window.scrollY > 400);
                ticking = false;
            });
            ticking = true;
        }
    });
    
    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}
