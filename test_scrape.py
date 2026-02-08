from newspaper import Article
import feedparser

def test_newspaper_scrape():
    # Get a real link from RSS
    rss_url = f"https://news.google.com/rss/search?q=IBK캐피탈&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    if feed.entries:
        first_entry = feed.entries[0]
        url = first_entry.link
        print(f"Target URL: {url}")
        
        try:
            print("Downloading article...")
            article = Article(url)
            article.download()
            article.parse()
            
            print(f"Title: {article.title}")
            print(f"Content Length: {len(article.text)}")
            try:
                print(f"Content Preview:\n{article.text[:500]}")
            except:
                print("Content preview failed (encoding)")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No entries found.")

if __name__ == "__main__":
    test_newspaper_scrape()
