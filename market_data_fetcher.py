import yfinance as yf
import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

def _fetch_single_ticker(name, symbol):
    """Fetches data for a single ticker."""
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="5d")

        if len(history) < 1:
            return name, {'price': 'N/A', 'change': '0.00%', 'color': 'black', 'symbol': symbol}

        current = history['Close'].iloc[-1]

        if len(history) >= 2:
            prev = history['Close'].iloc[-2]
        else:
            prev = history['Open'].iloc[-1]

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

        if name == 'USD/KRW':
            price_str = f"{current:.2f}원"
        elif name == 'JPY/KRW':
            price_str = f"{current:.2f}원"
        elif 'Bond' in name:
            price_str = f"{current:.2f}%"
        elif name in ['Gold', 'Silver', 'Copper']:
            price_str = f"${current:,.2f}"
        else:
            price_str = f"{current:,.2f}"

        return name, {
            'price': price_str,
            'change': change_str,
            'color': color,
            'symbol': symbol
        }

    except Exception:
        return name, {'price': 'N/A', 'change': '0.00%', 'color': 'black', 'symbol': symbol}

@st.cache_data(ttl=300)
def get_market_data():
    """
    Fetches key market indicators in parallel.
    Cached for 5 minutes to avoid redundant API calls.
    """
    tickers = {
        'KOSPI': '^KS11',
        'KOSDAQ': '^KQ11',
        'NASDAQ': '^IXIC',
        'Nikkei 225': '^N225',
        'USD/KRW': 'KRW=X',
        'JPY/KRW': 'JPYKRW=X',
        'US 10Y Bond': '^TNX',
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Copper': 'HG=F'
    }

    data = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(_fetch_single_ticker, name, sym) for name, sym in tickers.items()]
        for future in as_completed(futures):
            name, result = future.result()
            data[name] = result

    return data

@st.cache_data(ttl=300)
def get_historical_data(symbol, period="5y"):
    """
    Fetches historical closing prices for a given symbol.
    Cached for 5 minutes.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period)
        if not history.empty:
            return history['Close']
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
    return pd.Series()
