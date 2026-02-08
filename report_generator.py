from datetime import datetime

def generate_markdown_report(news_items, title="일일 뉴스 보고서 (Daily Report)", date_str=None):
    """
    Generates a markdown report from a list of news items (Korean Version).
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    report = f"# 📑 {title} ({date_str})\n\n"
    report += "## 💡 요약 (Executive Summary)\n"
    report += "> [!NOTE]\n"
    report += "> 이 보고서는 수집된 뉴스를 바탕으로 자동 생성되었습니다. NotebookLM에 업로드하여 오디오 브리핑을 생성해보세요.\n\n"
    
    report += f"**총 {len(news_items)}건**의 주요 뉴스가 수집되었습니다.\n\n"
    report += "---\n\n"
    report += "## 🗞️ 주요 뉴스 목록 (Key Updates)\n"
    
    for i, news in enumerate(news_items, 1):
        title = news['title']
        major_keywords = ['실적', '최대', '순이익', '배당', 'CEO', '대표', '인수', '합병', 'M&A', '발행']
        is_major = any(k in title for k in major_keywords)
        
        prefix = "🔥 " if is_major else ""
        report += f"### {i}. {prefix}{title}\n"
        report += f"- **발행일**: {news.get('published', 'N/A')}\n"
        report += f"- **원문 링크**: {news.get('link', '')}\n"
        
        if news.get('summary'):
            # 5-7 lines summary truncation logic
            full_summary = news['summary']
            sentences = full_summary.split('. ')
            truncated_summary = '. '.join(sentences[:5]) + '.' if len(sentences) > 5 else full_summary
            
            # Use Blockquote with larger text using Header logic if possible, or just cleaner formatting
            report += f"\n### 📝 내용 요약\n{truncated_summary}\n"
        else:
             report += f"\n> *내용을 가져오지 못했습니다. (원문 링크를 확인하세요)*\n"
             
        report += "\n---\n"
        
    return report
