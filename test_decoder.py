import feedparser
try:
    from googlenewsdecoder import new_decoderv1
except ImportError:
    print("googlenewsdecoder not found, trying manual decode")

def test_decoder():
    # Get a real link from RSS
    rss_url = f"https://news.google.com/rss/search?q=IBK캐피탈&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    if feed.entries:
        first_entry = feed.entries[0]
        url = first_entry.link
        print(f"Target URL: {url}")
        
        try:
            # Note: Usage depends on the library version. 
            # Trying standard usage patterns seen in docs/examples.
            # new_decoderv1(url) often works.
            
            real_url = new_decoderv1(url)
            if real_url.get('status'):
                 decoded_url = real_url['decoded_url']
                 print(f"Decoded URL: {decoded_url}")
            else:
                 print("Decoding failed")
                 
        except Exception as e:
            print(f"Error decoding: {e}")
            # Fallback check manual base64?
            
    else:
        print("No entries found.")

if __name__ == "__main__":
    test_decoder()
