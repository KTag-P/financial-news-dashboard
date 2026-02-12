
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
    
    return text.strip()

def summarize_korean(text, num_sentences=3, max_length=600, focus_keyword=None):
    """
    Concise extractive summarizer for Korean financial news.
    
    Args:
        text: Article text to summarize
        num_sentences: Number of sentences to extract (default 3)
        max_length: Maximum character length (default 600)
        focus_keyword: Company name to prioritize (e.g., "산은캐피탈")
    
    Returns:
        Summary string focusing on focus_keyword if provided
    """
    # Handle empty/placeholder content
    if not text:
        return "기사 요약 준비 중..."
    
    # Check for placeholder content - try to summarize anyway if there's any text
    placeholder_patterns = [
        "과거 기사입니다",
        "Historical Data",
    ]
    
    # Only skip if text is VERY short and contains placeholder
    cleaned_text = text.strip()
    if len(cleaned_text) < 30:
        for pattern in placeholder_patterns:
            if pattern in text:
                return text  # Return what we have
    
    # 0. Clean Text
    text = clean_text(text)
    
    # Handle very short text
    if len(text) < 50:
        return "기사 원문 링크를 통해 확인해 주세요."

    # 1. Split sentences (simple heuristic)
    sentences = re.split(r'(?<=[.?!다])\s+', text)
    
    # Filter out short/metadata sentences
    valid_sentences = []
    
    for s in sentences:
        s = s.strip()
        # Aggressive skipping
        if len(s) < 15: continue
        if "기자" in s and ("=" in s or "]" in s): continue
        if "@" in s: continue
        if "Copyright" in s or "무단전재" in s or "저작권" in s: continue
        if s.startswith("["): continue
        if "▲" in s or "▼" in s: continue
        if re.match(r'^[0-9\s\-\.\,]+$', s): continue  # Just numbers
        
        valid_sentences.append(s)
             
    if not valid_sentences:
        # Fallback: just take first portion of text
        if len(text) > 100:
            return text[:max_length]
        return "기사 원문 링크를 통해 확인해 주세요."

    # 2. Financial & Focus Keyword Boosting
    business_keywords = ["순이익", "실적", "투자", "매출", "성장", "자산", "증가", "감소",
                         "금리", "환율", "전망", "인수", "합병", "MOU", "사업", "펀드",
                         "수익", "영업이익", "당기순이익", "대출", "채권", "주가"]

    # 3. Score Sentences
    scores = []
    for i, s in enumerate(valid_sentences):
        score = 0
        
        # CRITICAL: Focus keyword boost (+20 per mention)
        # This ensures sentences mentioning the target company are prioritized
        if focus_keyword:
            # Handle various forms of company names
            focus_variants = [focus_keyword]
            if "캐피탈" in focus_keyword:
                # Add alternate names (e.g., "산은캐피탈" -> "KDB캐피탈", "산업은행캐피탈")
                if "산은" in focus_keyword:
                    focus_variants.extend(["KDB캐피탈", "산업은행캐피탈", "KDB Capital"])
                elif "IBK" in focus_keyword:
                    focus_variants.extend(["기업은행캐피탈", "IBK Capital"])
                    
            for variant in focus_variants:
                if variant in s:
                    score += 20  # High priority
        
        # Business keyword boost (+3 per keyword)
        for kw in business_keywords:
            if kw in s:
                score += 3
        
        # Length boost (prefer medium-length sentences)
        word_count = len(s.split())
        if 8 <= word_count <= 40:
            score += 2
            
        # Position boost (first sentences often summarize)
        if i == 0:
            score += 3
        elif i < 3:
            score += 1
            
        scores.append((score, i, s))

    # 4. Select Top Sentences (Preserve Order)
    # First, try to get sentences with focus_keyword
    if focus_keyword:
        focus_sentences = [(sc, idx, sent) for sc, idx, sent in scores if sc >= 20]
        if focus_sentences:
            # Sort by score, take top
            focus_sentences = sorted(focus_sentences, key=lambda x: x[0], reverse=True)[:num_sentences]
            focus_sentences.sort(key=lambda x: x[1])  # Restore order
            final_summary = " ".join([item[2] for item in focus_sentences])
            if len(final_summary) > max_length:
                final_summary = final_summary[:max_length]
            return final_summary
    
    # Fallback: general ranking
    ranked = sorted(scores, key=lambda x: x[0], reverse=True)[:num_sentences]
    ranked.sort(key=lambda x: x[1])  # Restore reading order

    final_summary = " ".join([item[2] for item in ranked])
    
    # Enforce max length (but don't add "..." - just cut cleanly at sentence boundary if possible)
    if len(final_summary) > max_length:
        final_summary = final_summary[:max_length]
        
    return final_summary
