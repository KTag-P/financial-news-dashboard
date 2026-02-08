import yfinance as yf
import pandas as pd

def get_market_data():
    """
    Fetches key market indicators: KOSPI, KOSDAQ, NASDAQ, Nikkei, USD/KRW, US 10Y Bond, Gold, Silver, Copper
    """
    tickers = {
        'KOSPI': '^KS11',
        'KOSDAQ': '^KQ11',
        'NASDAQ': '^IXIC',
        'Nikkei 225': '^N225',
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
                data[name] = {'price': 'N/A', 'change': '0.00%', 'color': 'black', 'symbol': symbol}
                continue
            
            current = history['Close'].iloc[-1]
            
            # Get previous close
            if len(history) >= 2:
                prev = history['Close'].iloc[-2]
            else:
                prev = history['Open'].iloc[-1] # Fallback
            
            change_rate = ((current - prev) / prev) * 100
            
            if change_rate > 0:
                color = "red"
                change_str = f"+{change_rate:.2f}%"
            elif change_rate < 0:
                color = "blue"
                change_str = f"{change_rate:.2f}%"
            else:
                color = "black"
                change_str = "0.00%"
            
            # Formatting
            if name == 'USD/KRW':
                price_str = f"{current:.2f}원"
            elif 'Bond' in name:
                price_str = f"{current:.2f}%"
            elif name in ['Gold', 'Silver', 'Copper']:
                 price_str = f"${current:,.2f}"
            else:
                price_str = f"{current:,.2f}"
                
            data[name] = {
                'price': price_str,
                'change': change_str,
                'color': color,
                'symbol': symbol # Return symbol for chart fetching
            }
            
        except Exception as e:
            data[name] = {'price': 'N/A', 'change': '0.00%', 'color': 'black', 'symbol': symbol}
            
    return data

def get_historical_data(symbol, period="5y"):
    """
    Fetches historical closing prices for a given symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period)
        if not history.empty:
            return history['Close']
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
    return pd.Series()
