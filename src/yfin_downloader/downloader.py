import yfinance
from yfin_downloader.utils import save_pickle


def download_stock_history(ticker, data_dir, period='1mo'):
    print('downloading %s' % ticker)
    stock = yfinance.Ticker(ticker)
    df = stock.history(period=period)
    if not df.empty:
        save_pickle(df, '%s/%s_prices.pkl' % (data_dir, ticker))
        return True
    return False
