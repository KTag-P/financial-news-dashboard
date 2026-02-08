
import re
from collections import Counter

def clean_text(text):
    """
    Removes reporter bylines, emails, and brackets commonly found in news.
    """
    if not text:
        return ""
        
    # Remove [Name Reporter] or (Name) at start
    text = re.sub(r'^\[.*?\]', '', text) 
    text = re.sub(r'^\(.*?(=|기자).*?\)', '', text)
    text = re.sub(r'^[가-힣]{2,4} 기자 = ', '', text)
    
    # Remove email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
    
    # Remove common press suffixes
    text = re.sub(r'무단전재 및 재배포 금지', '', text)
    text = re.sub(r'Copyrights?.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'저작권자.*', '', text)
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    
    # Remove image/graphic markers
    text = re.sub(r'이미지 크게보기.*?기자\)', '', text)
    text = re.sub(r'\[.*?기자\]', '', text)
    text = re.sub(r'그래픽=.*?기자', '', text)
    
    return text.strip()

def summarize_korean(text, num_sentences=4, max_length=800, focus_keyword=None):
    """
    Concise extractive summarizer for Korean financial news.
    Returns multiple key sentences, prioritizing content over brevity.
    """
    # Handle empty/placeholder content
    if not text or len(text.strip()) < 10:
        return "기사 요약 준비 중..."
    
    # Clean Text
    text = clean_text(text)
    
    # Handle very short text - just return it
    if len(text) < 100:
        return text
    
    # Split sentences - improved regex for Korean
    sentences = re.split(r'(?<=[.?!다요])\s+', text)
    
    # Filter out short/metadata sentences
    valid_sentences = []
    
    for s in sentences:
        s = s.strip()
        if len(s) < 15: continue
        if "기자" in s and ("=" in s or "]" in s): continue
        if "@" in s: continue
        if "Copyright" in s or "무단전재" in s or "저작권" in s: continue
        if s.startswith("["): continue
        if "▲" in s or "▼" in s: continue
        if re.match(r'^[0-9\s\-\.\,]+$', s): continue
        if "이미지 크게보기" in s: continue
        if "그래픽=" in s: continue
        
        valid_sentences.append(s)
             
    if not valid_sentences:
        # Fallback: just return the cleaned text
        return text[:max_length] if len(text) > max_length else text

    # Financial & Focus Keyword Boosting
    business_keywords = ["순이익", "실적", "투자", "매출", "성장", "자산", "증가", "감소",
                         "금리", "환율", "전망", "인수", "합병", "MOU", "사업", "펀드",
                         "수익", "영업이익", "당기순이익", "대출", "채권", "주가", "출자",
                         "PEF", "사모펀드", "캐피탈", "금융"]

    # Score Sentences
    scores = []
    for i, s in enumerate(valid_sentences):
        score = 0
        
        # Focus keyword boost (+15 per mention)
        if focus_keyword:
            focus_variants = [focus_keyword]
            if "캐피탈" in focus_keyword:
                if "산은" in focus_keyword:
                    focus_variants.extend(["KDB캐피탈", "산업은행캐피탈", "KDB Capital"])
                elif "IBK" in focus_keyword:
                    focus_variants.extend(["기업은행캐피탈", "IBK Capital"])
                    
            for variant in focus_variants:
                if variant in s:
                    score += 15
        
        # Business keyword boost (+2 per keyword)
        for kw in business_keywords:
            if kw in s:
                score += 2
        
        # Length boost (prefer medium-length sentences)
        if 20 <= len(s) <= 150:
            score += 3
        elif len(s) > 150:
            score += 1
            
        # Position boost (first sentences often summarize)
        if i == 0:
            score += 4
        elif i < 3:
            score += 2
        elif i < 5:
            score += 1
            
        scores.append((score, i, s))

    # Select Top Sentences - ALWAYS get at least num_sentences
    # Sort by score, take top
    ranked = sorted(scores, key=lambda x: x[0], reverse=True)[:num_sentences]
    ranked.sort(key=lambda x: x[1])  # Restore reading order

    final_summary = " ".join([item[2] for item in ranked])
    
    # Enforce max length
    if len(final_summary) > max_length:
        final_summary = final_summary[:max_length]
        
    return final_summary if final_summary else text[:max_length]
