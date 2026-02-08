from report_generator import generate_markdown_report

def test_report():
    sample_news = [
        {
            'title': 'Test News 1',
            'link': 'http://example.com/1',
            'published': '2025-01-01',
            'summary': 'This is a summary of news 1.'
        },
        {
            'title': 'Test News 2',
            'link': 'http://example.com/2',
            'published': '2025-01-02',
            'summary': 'This is a summary of news 2.'
        }
    ]
    
    print("Testing Report Generation...")
    report = generate_markdown_report(sample_news, title="Test Company Report")
    print("\n--- Report Preview ---\n")
    print(report)
    
    if "Test Company Report" in report and "Test News 1" in report:
        print("\nTest Passed!")
    else:
        print("\nTest Failed!")

if __name__ == "__main__":
    test_report()
