from report_generator import generate_markdown_report

news_items = [
    {
        "title": "IBK캐피탈 역대 최대 실적 달성",
        "published": "2024-12-31",
        "link": "http://example.com",
        "image": "http://example.com/image.jpg",
        "summary": "IBK캐피탈이 2024년 순이익 2,142억원을 기록하며 역대 최대 실적을 달성했다."
    }
]

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

report = generate_markdown_report(news_items, title="IBK캐피탈 테스트 보고서")
print(report)

if "역대 최대 실적" in report and "News Image" in report:
    print("\nSUCCESS: Report generated correctly with Korean text and image.")
else:
    print("\nFAILED: Report missing key elements.")
