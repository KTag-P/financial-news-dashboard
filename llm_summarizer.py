"""
LLM-based summarization using Google Gemini API (Free Tier).
Falls back to simple_summarizer when API is unavailable.
"""
import os
from dotenv import load_dotenv
import simple_summarizer

load_dotenv()

_model = None
_api_available = False
_init_done = False


def _init_client():
    """Lazy initialization of Google Gemini client."""
    global _model, _api_available, _init_done
    if _init_done:
        return
    _init_done = True

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Streamlit Cloud secrets fallback
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass
    if not api_key:
        _api_available = False
        return

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        _model = client
        _api_available = True
    except ImportError:
        print("[llm_summarizer] google-genai 패키지가 필요합니다: pip install google-genai")
        _api_available = False
    except Exception as e:
        print(f"[llm_summarizer] Gemini 초기화 실패: {e}")
        _api_available = False


def is_available():
    """Check if LLM summarization is available."""
    _init_client()
    return _api_available


def _call_gemini(prompt, max_tokens=500):
    """Helper to call Gemini API."""
    try:
        from google.genai import types
        response = _model.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.3,
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"[llm_summarizer] Gemini API 호출 실패: {e}")
        return None


def summarize(text, num_sentences=4, focus_keyword=None):
    """
    Summarize Korean financial news text using Gemini Flash.
    Falls back to simple_summarizer if API unavailable.
    """
    _init_client()

    if not _api_available or not text or len(text) < 50:
        return simple_summarizer.summarize_korean(
            text, num_sentences=num_sentences, focus_keyword=focus_keyword
        )

    focus_instruction = ""
    if focus_keyword:
        focus_instruction = f"특히 '{focus_keyword}'와 관련된 내용을 중심으로 요약해주세요."

    prompt = f"""다음 한국어 금융 뉴스 기사를 {num_sentences}문장으로 간결하게 요약해주세요.
{focus_instruction}
핵심 수치와 사실 위주로 요약하고, 기자 이름이나 출처 정보는 제외해주세요.

기사 원문:
{text[:3000]}"""

    result = _call_gemini(prompt, max_tokens=500)
    if result:
        return result
    
    return simple_summarizer.summarize_korean(
        text, num_sentences=num_sentences, focus_keyword=focus_keyword
    )


def analyze_sentiment(text):
    """
    Analyze sentiment of Korean financial news.
    Returns: 'positive', 'negative', or 'neutral'
    """
    _init_client()

    if not _api_available or not text or len(text) < 30:
        return _rule_based_sentiment(text)

    prompt = f"""다음 한국어 금융 뉴스의 감성을 분석해주세요.
반드시 'positive', 'negative', 'neutral' 중 하나만 답해주세요. 다른 설명 없이 단어 하나만 출력해주세요.

기사:
{text[:1500]}"""

    result = _call_gemini(prompt, max_tokens=10)
    if result:
        result = result.lower().strip()
        if result in ('positive', 'negative', 'neutral'):
            return result
    return _rule_based_sentiment(text)


def _rule_based_sentiment(text):
    """Fallback rule-based sentiment for when API is unavailable."""
    if not text:
        return 'neutral'

    positive_kw = ['성장', '증가', '최대', '호실적', '흑자', '확대', '상승', '개선', '수상', '돌파']
    negative_kw = ['감소', '하락', '적자', '부실', '연체', '위기', '손실', '축소', '하향', '침체']

    pos_count = sum(1 for kw in positive_kw if kw in text)
    neg_count = sum(1 for kw in negative_kw if kw in text)

    if pos_count > neg_count + 1:
        return 'positive'
    elif neg_count > pos_count + 1:
        return 'negative'
    return 'neutral'


def generate_synthesis_report(news_items, title="", company_name=""):
    """
    Generate a comprehensive synthesis report using Gemini API.
    Falls back to rule-based report_generator if API unavailable.
    """
    _init_client()

    if not _api_available:
        import report_generator
        return report_generator.generate_synthesis_report(
            news_items, title=title, company_name=company_name
        )

    # Build source material
    source_text = ""
    for item in news_items[:20]:
        date = item.get('published', '')[:10]
        item_title = item.get('title', '')
        content = item.get('full_content', '') or item.get('summary', '')
        source_text += f"[{date}] {item_title}\n{content[:500]}\n\n"

    prompt = f"""당신은 한국 금융 업계 전문 애널리스트입니다.
다음 {len(news_items)}개의 뉴스 기사를 종합하여 '{company_name}'에 대한 심층 분석 리포트를 작성해주세요.

리포트 형식 (Markdown):
## 📑 {company_name} 경영 분석 리포트
### 🌟 종합 요약 (Executive Summary)
- 핵심 트렌드 3-5개를 bullet point로
### 🔍 주요 테마별 심층 분석
- 각 주요 테마를 소제목과 함께 2-3문장으로 분석
### ⚠️ 리스크 요인
- 주의해야 할 리스크 2-3가지
### 📈 전망
- 향후 전망 2-3문장

뉴스 원문:
{source_text[:6000]}"""

    result = _call_gemini(prompt, max_tokens=2000)
    if result:
        return result

    import report_generator
    return report_generator.generate_synthesis_report(
        news_items, title=title, company_name=company_name
    )
