
import simple_summarizer
from collections import Counter
import re
from datetime import datetime


def extract_keywords(text, top_n=5, target_company=None):
    """
    Extracts top N keywords, boosting those that appear near the target company.
    """
    stopwords = set(["뉴스", "기자", "밝혔다", "따르면", "있다", "것으로", "대한", "위해", "통해", "지난", "이번", "경우", "관련", "등", "및", "이", "그", "저", "수", "것", "들", "제", "개", "전", "후", "네", "아", "휴", "아이구", "아이쿠", "아이고", "어", "나", "우리", "저희", "따라", "의해", "을", "를", "에", "의", "가", "으로", "로", "에게", "뿐이다", "의거하여", "근거하여", "입각하여", "기준으로", "예하면", "예를", "들면", "들자면", "저기", "저쪽", "저것", "그때", "그럼", "그러면", "요컨대", "다시", "말하자면", "말하면", "즉", "구체적으로", "말해", "시작하여", "관하여", "비길수", "없다", "하기", "때문에", "그", "여러분", "채용", "공고", "모집"])
    
    # Competitor names to exclude from keywords
    competitors = ["신한", "KB", "국민", "우리", "하나", "롯데", "현대", "삼성", "BC"]
    
    words = re.findall(r'\w+', text)
    filtered_words = []
    
    for w in words:
        if len(w) > 1 and w not in stopwords:
            # Exclude competitor names if valid
            if not any(c in w for c in competitors):
                filtered_words.append(w)
    
    # Weight certain financial keywords
    weighted_words = []
    for w in filtered_words:
        weighted_words.append(w)
        if w in ["금리", "PF", "부동산", "실적", "순이익", "배당", "주가", "발행", "채권", "CEO", "인사", "디지털", "플랫폼", "신기술", "펀드", "투자"]:
            weighted_words.append(w) # Add again to boost
            
    return [item[0] for item in Counter(weighted_words).most_common(top_n)]

def generate_synthesis_report(news_items, title="월간 핵심 리포트", company_name=""):
    """
    Generates a synthesized report focused strictly on the target company.
    """
    now = datetime.now().strftime("%Y-%m-%d")
    
    target_kws = []
    if "IBK" in title or "IBK" in company_name: target_kws = ["IBK", "기업은행"]
    elif "산은" in title or "KDB" in company_name: target_kws = ["KDB", "산은", "산업은행"]
    
    competitors = ["신한" , "KB", "국민", "우리", "하나", "롯데", "현대", "삼성"]

    # 1. Combine & Filter Text
    relevant_sentences = []
    all_text_for_keywords = ""
    
    for item in news_items:
        content = item.get('full_content', '') or item.get('summary', '')
        # Split into sentences
        sentences = re.split(r'(?<=[.?!])\s+', content)
        for s in sentences:
            s_clean = simple_summarizer.clean_text(s)
            if len(s_clean) < 20: continue
            
    # ... (inside loop)
            # Context Filtering
            # Condition 0: Strict Junk Filter (Captions, Attendee Lists)
            if s_clean.startswith("(") or s_clean.startswith("[") or "왼쪽부터" in s_clean or "오른쪽부터" in s_clean or "기념촬영" in s_clean:
                continue

            # Condition 1: Must not be primarily about a competitor (unless target is also mentioned)
            is_competitor_news = any(c in s_clean for c in competitors)
            is_target_news = any(t in s_clean for t in target_kws) if target_kws else True
            
            if is_competitor_news and not is_target_news:
                continue # Skip pure competitor news
                
            relevant_sentences.append(s_clean)
            all_text_for_keywords += s_clean + " "

    if not relevant_sentences:
        return "분석할 관련 데이터가 부족합니다."

    full_relevant_text = " ".join(relevant_sentences)

    # 2. Extract Top Themes (from filtered text)
    keywords = extract_keywords(full_relevant_text, top_n=5, target_company=target_kws[0] if target_kws else None)
    
    # 3. Generate Executive Summary (Focus on Target + Business Score)
    # We prioritize sentences that have the target keyword AND high business score
    scored_candidates = []
    
    # Define Business Keywords
    business_kws = ["순이익", "실적", "투자", "펀드", "성장", "금융", "지원", "MOU", "전략", "디지털", "영업", "자산", "발행", "채권", "확대", "강화"]
    junk_kws = ["참석", "개최", "사진", "오전", "오후", "서울", "호텔", "취임", "인사", "방문", "기념", "보수", "연봉", "사외이사", "지급", "기부", "성금", "봉사", "전달", "나눔", "후원"]

    for s in relevant_sentences:
        score = 0
        # Base Score: Target Company Mention
        if target_kws and any(t in s for t in target_kws):
             score += 10
        
        # Business Score
        for bk in business_kws:
            if bk in s: score += 5
            
        # Junk Score (Penalty)
        for jk in junk_kws:
            if jk in s: score -= 5
            
        # Length Score (Too short is bad, too long is okay if informative)
        if len(s) < 30: score -= 10
        
        # Competitor Penalty for Executive Summary (Strict)
        if any(c in s for c in competitors): score -= 5

        scored_candidates.append((score, s))
    
    # Sort by score desc
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Pick Top 5 Unique High-Scoring Sentences
    top_exec_sentences = []
    seen_exec = set()
    for score, s in scored_candidates:
        if len(top_exec_sentences) >= 5: break
        if score > 5 and s not in seen_exec: # Minimum threshold
             top_exec_sentences.append(s)
             seen_exec.add(s)
    
    if not top_exec_sentences: # Fallback
        top_exec_sentences = [s for _, s in scored_candidates[:3]]

    exec_summary_bullets = ""
    for s in top_exec_sentences:
         exec_summary_bullets += f"- {s.strip()}.\n"
    
    # 4. Generate Theme-based Sections
    theme_sections = ""
    used_sentences = set()
    
    for kw in keywords:
        # Avoid the target company name itself as a "theme" (too broad)
        if target_kws and any(t in kw for t in target_kws): continue
        if len(kw) < 2: continue
        
        # Find sentences containing the keyword AND strictly relevant
        theme_candidates = []
        for s in relevant_sentences:
            if kw in s:
                # Double check competitor filtering
                if any(c in s for c in competitors) and not (target_kws and any(t in s for t in target_kws)):
                    continue
                
                if s not in used_sentences and len(s) < 300:
                    theme_candidates.append(s)
                    used_sentences.add(s)
        
        if theme_candidates:
            # Pick top 2-3
            top_sentences = sorted(list(set(theme_candidates)), key=len, reverse=True)[:3]
            theme_sections += f"#### 🔑 {kw}\n"
            for s in top_sentences:
                theme_sections += f"- {s.strip()}\n"
            theme_sections += "\n"

    # 5. Build Final Markdown
    report = f"""
## 📑 {company_name} 경영 분석 리포트 (Briefing)
**생성일**: {now} | **분석 대상**: {len(news_items)}건의 기사 중 관련 내용 추출

### 🌟 종합 요약 (Executive Summary)
> **핵심 트렌드**: {company_name} 관련 주요 이슈와 흐름은 다음과 같습니다.

{exec_summary_bullets}

---

### 🔍 주요 테마별 심층 분석 (Deep Dive)
**{company_name}**의 관점에서 주요 키워드를 분석했습니다.

{theme_sections}

---

### 📚 출처 (Sources)
"""
    for item in news_items[:10]: # List top 10 titles
        date = item.get('published', '')[:10]
        report += f"1. **[{date}]** {item.get('title')}\n"
        
    return report
