
import simple_summarizer
from collections import Counter
import re
from datetime import datetime

def extract_keywords(text, top_n=5):
    """
    Extracts top N keywords from text, excluding common stopwords.
    """
    # Simple stopword list (can be expanded)
    stopwords = set(["뉴스", "기자", "밝혔다", "따르면", "있다", "것으로", "대한", "위해", "통해", "지난", "이번", "경우", "관련", "등", "및", "이", "그", "저", "수", "것", "들", "제", "개", "전", "후", "네", "아", "휴", "아이구", "아이쿠", "아이고", "어", "나", "우리", "저희", "따라", "의해", "을", "를", "에", "의", "가", "으로", "로", "에게", "뿐이다", "의거하여", "근거하여", "입각하여", "기준으로", "예하면", "예를", "들면", "들자면", "저기", "저쪽", "저것", "그때", "그럼", "그러면", "요컨대", "다시", "말하자면", "말하면", "즉", "구체적으로", "말해", "시작하여", "관하여", "비길수", "없다", "하기", "때문에", "그", "여러분"])
    
    words = re.findall(r'\w+', text)
    filtered_words = [w for w in words if len(w) > 1 and w not in stopwords]
    
    # Weight certain financial keywords
    weighted_words = []
    for w in filtered_words:
        weighted_words.append(w)
        if w in ["금리", "PF", "부동산", "실적", "순이익", "배당", "주가", "발행", "채권", "CEO", "인사", "디지털", "플랫폼"]:
            weighted_words.append(w) # Add again to boost weight
            
    return [item[0] for item in Counter(weighted_words).most_common(top_n)]

def generate_synthesis_report(news_items, title="월간 핵심 리포트"):
    """
    Generates a synthesized report from multiple news items.
    """
    now = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Combine All Text
    all_text = ""
    for item in news_items:
        content = item.get('full_content', '') or item.get('summary', '')
        all_text += content + "\n"
    
    if len(all_text) < 100:
        return "분석할 데이터가 부족합니다."

    # 2. Extract Top Themes
    keywords = extract_keywords(all_text, top_n=5)
    
    # 3. Generate Executive Summary (Overall)
    exec_summary = simple_summarizer.summarize_korean(all_text, num_sentences=5)
    
    # 4. Generate Theme-based Sections
    theme_sections = ""
    used_sentences = set() # To avoid repetition
    
    for kw in keywords:
        # Find sentences containing the keyword
        relevant_sentences = []
        for sentence in re.split(r'(?<=[.?!])\s+', all_text):
            if kw in sentence and len(sentence) > 30:
                clean_s = simple_summarizer.clean_text(sentence)
                if clean_s not in used_sentences:
                    relevant_sentences.append(clean_s)
        
        # Summarize these sentences
        if relevant_sentences:
            theme_summary = simple_summarizer.summarize_korean(" ".join(relevant_sentences), num_sentences=2)
            theme_sections += f"#### 🔑 키워드: {kw}\n{theme_summary}\n\n"
            used_sentences.add(theme_summary)

    # 5. Build Final Markdown
    report = f"""
## 📊 {title} (AI Synthesis)

### 📝 종합 요약 (Executive Summary)
{exec_summary}

---

### 🔍 주요 키워드별 심층 분석
{theme_sections}

---

### 🗞️ 분석 대상 뉴스 ({len(news_items)}건)
"""
    for item in news_items[:10]: # List top 10 titles only
        report += f"- {item.get('title')}\n"
        
    return report
