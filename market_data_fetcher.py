import yfinance as yf

def get_market_data():
    """
    Fetches real-time market data for KOSPI, USD/KRW, USD/JPY, Gold, Silver, Copper.
    Returns a dictionary with formatted strings.
    """
    tickers = {
        'KOSPI': '^KS11',
        'USD/KRW': 'KRW=X',
        'US 10Y Bond': '^TNX',
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Copper': 'HG=F'
    }
    
    data = {}
    
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            # Fetch 5 days to ensure we have previous close even after weekends/holidays
            history = ticker.history(period="5d")
            
            if len(history) < 1:
                data[name] = {'price': 'N/A', 'change': '0.00%', 'color': 'black'}
                continue
                
            current = history['Close'].iloc[-1]
            
            # Get previous close for change calc
            if len(history) >= 2:
                prev = history['Close'].iloc[-2]
            else:
                prev = history['Open'].iloc[-1] # Fallback
            
            change = ((current - prev) / prev) * 100
            
            # Format
            if name == 'USD/KRW':
                 fmt_price = f"{current:.2f}원"
            elif name == 'US 10Y Bond':
                 fmt_price = f"{current:.2f}%"
            else:
                 fmt_price = f"{current:,.2f}"

            color = "red" if change > 0 else "blue" # Red is up in Korea
            sign = "+" if change > 0 else ""
            
            data[name] = {
                'price': fmt_price,
                'change': f"{sign}{change:.2f}%",
                'color': color
            }
        except Exception as e:
            # print(f"Error fetching {name}: {e}")
            data[name] = {'price': 'N/A', 'change': '0.00%', 'color': 'black'}
            
    return data
