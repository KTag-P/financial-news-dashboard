
import re
from collections import Counter

def clean_text(text):
    """
    Removes reporter bylines, emails, and brackets commonly found in news.
    """
    # Remove [Name Reporter] or (Name) at start
    text = re.sub(r'^\[.*?\]', '', text) 
    text = re.sub(r'^\(.*?(=|기자).*?\)', '', text)
    text = re.sub(r'^[가-힣]{2,4} 기자 = ', '', text)
    
    # Remove email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
    
    # Remove common press suffixes
    text = re.sub(r'무단전재 및 재배포 금지', '', text)
    text = re.sub(r'Copyrights', '', text)
    
    return text.strip()

def summarize_korean(text, num_sentences=3):
    """
    Simple extractive summarizer for Korean text.
    ranks sentences by keyword frequency.
    """
    if not text:
        return "내용 없음"
    
    # 0. Clean Text
    text = clean_text(text)

    # 1. Split sentences (simple heuristic)
    sentences = re.split(r'(?<=[.?!])\s+', text)
    
    # Filter out short/metadata sentences
    valid_sentences = []
    
    for s in sentences:
        s = s.strip()
        # Aggressive skipping
        if len(s) < 30: continue # Too short
        if "기자" in s and ("=" in s or "]" in s): continue # "Hong Gil-dong Reporter ="
        if "@" in s: continue # Email
        if "Copyright" in s or "무단전재" in s: continue
        if s.startswith("["): continue # [News Agency]
        
        valid_sentences.append(s)
             
    if not valid_sentences:
        valid_sentences = sentences[:5] # Fallback to first few if overkill

    if len(valid_sentences) <= num_sentences:
        return " ".join(valid_sentences)

    # 2. Tokenize (simple whitespace + cleanup)
    words = []
    for s in valid_sentences:
        # Remove special chars for counting
        clean_s = re.sub(r'[^\w\s]', '', s)
        words.extend(clean_s.split())

    # 3. Calculate Word Frequencies
    word_freq = Counter(words)
    max_freq = max(word_freq.values()) if word_freq else 1
    
    # normalize
    for w in word_freq:
        word_freq[w] /= max_freq

    # 4. Score Sentences
    scores = []
    for i, s in enumerate(valid_sentences):
        score = 0
        s_words = re.sub(r'[^\w\s]', '', s).split()
        for w in s_words:
             score += word_freq.get(w, 0)
        
        # Penalty for very short sentences
        if len(s_words) < 5:
            score *= 0.5
            
        scores.append((score, i, s))

    # 5. Select Top Sentences (Preserve Order)
    # Sort by score desc
    ranked_sentences = sorted(scores, key=lambda x: x[0], reverse=True)[:num_sentences]
    # Sort by original index
    ranked_sentences.sort(key=lambda x: x[1])

    final_summary = " ".join([item[2] for item in ranked_sentences])
    return final_summary
