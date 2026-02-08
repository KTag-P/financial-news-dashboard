from datetime import datetime

def generate_markdown_report(news_items, title="Daily News Report", date_str=None):
    """
    Generates a markdown report from a list of news items.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    report = f"# {title} ({date_str})\n\n"
    report += "## Executive Summary\n"
    report += "> [!NOTE]\n"
    report += "> This summary is automatically generated based on the collected news items below.\n\n"
    
    report += f"Collected {len(news_items)} unique news items.\n\n"
    
    report += "## Key Updates\n"
    
    for i, news in enumerate(news_items, 1):
        report += f"### {i}. {news['title']}\n"
        report += f"- **Published**: {news.get('published', 'N/A')}\n"
        report += f"- **Link**: {news.get('link', '')}\n"
        if news.get('summary'):
            report += f"\n{news['summary']}\n"
        report += "\n"
        
    return report
