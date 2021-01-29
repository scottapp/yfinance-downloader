import yfinance


def download_stock_history(ticker, period='1mo'):
    stock = yfinance.Ticker(ticker)
    df = stock.history(period=period)
    return df
