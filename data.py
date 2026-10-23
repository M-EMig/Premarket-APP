import yfinance as yf


def history(ticker, period="6mo"):
    df = yf.Ticker(ticker).history(period=period, auto_adjust=True)
    return df.dropna() if not df.empty else df


def last_price(ticker):
    try:
        df = yf.Ticker(ticker).history(period="1d", interval="5m")
        if not df.empty:
            return float(df["Close"].iloc[-1])
    except Exception:
        pass
    df = history(ticker, "5d")
    return float(df["Close"].iloc[-1]) if not df.empty else None
